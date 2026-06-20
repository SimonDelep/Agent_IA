"""
Assemblage du StateGraph LangGraph — pattern supervisor multi-agents.
"""

from __future__ import annotations

from typing import Literal

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import AzureChatOpenAI
from langgraph.graph import END, START, StateGraph
from langgraph.prebuilt import create_react_agent
from langsmith import traceable
from mcp import ClientSession
from pydantic import BaseModel, Field

from multi_agent import config
from multi_agent.agents.document import DOCUMENT_PROMPT
from multi_agent.agents.orchestrator import FINALIZE_PROMPT, SUPERVISOR_PROMPT
from multi_agent.agents.product_expert import PRODUCT_EXPERT_PROMPT
from multi_agent.agents.service_client import SERVICE_CLIENT_PROMPT
from multi_agent.graph.state import AgentState
from multi_agent.tools.mcp_tools import build_mcp_tools
from multi_agent.tools.rag_tool import build_rag_tool

MEMBERS = [
    config.AGENT_SERVICE_CLIENT,
    config.AGENT_PRODUCT_EXPERT,
    config.AGENT_DOCUMENT,
]


class SupervisorRoute(BaseModel):
    """Décision de routage du supervisor."""

    next: Literal[
        "service_client",
        "product_expert",
        "document",
        "FINISH",
    ] = Field(description="Prochain agent à invoquer, ou FINISH si la demande est traitée")
    reasoning: str = Field(description="Brève justification du choix de routage")


def get_llm() -> AzureChatOpenAI:
    if not config.AZURE_OPENAI_API_KEY or not config.AZURE_OPENAI_ENDPOINT:
        raise ValueError(
            "Configuration Azure manquante. Définissez AZURE_OPENAI_API_KEY et "
            "AZURE_OPENAI_ENDPOINT dans dev.env."
        )
    if not config.AZURE_OPENAI_DEPLOYMENT:
        raise ValueError("AZURE_OPENAI_DEPLOYMENT manquant dans dev.env.")

    return AzureChatOpenAI(
        azure_endpoint=config.AZURE_OPENAI_ENDPOINT,
        api_key=config.AZURE_OPENAI_API_KEY,
        api_version=config.AZURE_OPENAI_API_VERSION,
        azure_deployment=config.AZURE_OPENAI_DEPLOYMENT,
        temperature=0,
    )


async def build_supervisor_graph(session: ClientSession):
    """
    Construit et compile le graphe supervisor avec session MCP partagée.
    """
    llm = get_llm()

    service_tools = await build_mcp_tools(
        session,
        config.SERVICE_CLIENT_TOOLS,
        agent_name=config.AGENT_SERVICE_CLIENT,
    )
    product_tools = await build_mcp_tools(
        session,
        config.PRODUCT_EXPERT_TOOLS,
        agent_name=config.AGENT_PRODUCT_EXPERT,
    )
    document_tools = [build_rag_tool(agent_name=config.AGENT_DOCUMENT)]

    service_client_agent = create_react_agent(
        llm,
        tools=service_tools,
        prompt=SERVICE_CLIENT_PROMPT,
        name=config.AGENT_SERVICE_CLIENT,
    )
    product_expert_agent = create_react_agent(
        llm,
        tools=product_tools,
        prompt=PRODUCT_EXPERT_PROMPT,
        name=config.AGENT_PRODUCT_EXPERT,
    )
    document_agent = create_react_agent(
        llm,
        tools=document_tools,
        prompt=DOCUMENT_PROMPT,
        name=config.AGENT_DOCUMENT,
    )

    router_llm = llm.with_structured_output(
        SupervisorRoute,
        method="function_calling",
    )

    def _resolve_route(raw: SupervisorRoute | dict) -> SupervisorRoute:
        if isinstance(raw, SupervisorRoute):
            return raw
        return SupervisorRoute.model_validate(raw)

    @traceable(name="nordtrail.agent.supervisor", run_type="chain")
    def supervisor_node(state: AgentState) -> dict:
        turns = state.get("supervisor_turns", 0) + 1
        visited = list(state.get("agents_visited") or [])

        if turns > config.MAX_SUPERVISOR_TURNS:
            return {
                "next": "FINISH",
                "supervisor_turns": turns,
                "agents_visited": visited,
            }

        visited_label = ", ".join(visited) if visited else "aucun"
        system_content = (
            f"{SUPERVISOR_PROMPT}\n\n"
            f"Agents déjà consultés : {visited_label}."
        )

        route = _resolve_route(
            router_llm.invoke(
                [SystemMessage(content=system_content), *state["messages"]]
            )
        )
        next_step = route.next

        if next_step != "FINISH" and next_step in visited:
            next_step = "FINISH"

        updated_visited = visited
        if next_step != "FINISH" and next_step not in visited:
            updated_visited = visited + [next_step]

        return {
            "next": next_step,
            "supervisor_turns": turns,
            "agents_visited": updated_visited,
        }

    @traceable(name="nordtrail.agent.finalize", run_type="chain")
    def finalize_node(state: AgentState) -> dict:
        messages = [
            SystemMessage(content=FINALIZE_PROMPT),
            *state["messages"],
        ]
        response = llm.invoke(messages)
        return {"messages": [response]}

    def supervisor_router(state: AgentState) -> str:
        if state["next"] == "FINISH":
            return config.AGENT_FINALIZE
        return state["next"]

    builder = StateGraph(AgentState)
    builder.add_node(config.AGENT_SUPERVISOR, supervisor_node)
    builder.add_node(config.AGENT_SERVICE_CLIENT, service_client_agent)
    builder.add_node(config.AGENT_PRODUCT_EXPERT, product_expert_agent)
    builder.add_node(config.AGENT_DOCUMENT, document_agent)
    builder.add_node(config.AGENT_FINALIZE, finalize_node)

    builder.add_edge(START, config.AGENT_SUPERVISOR)
    for member in MEMBERS:
        builder.add_edge(member, config.AGENT_SUPERVISOR)

    builder.add_conditional_edges(
        config.AGENT_SUPERVISOR,
        supervisor_router,
        {
            config.AGENT_SERVICE_CLIENT: config.AGENT_SERVICE_CLIENT,
            config.AGENT_PRODUCT_EXPERT: config.AGENT_PRODUCT_EXPERT,
            config.AGENT_DOCUMENT: config.AGENT_DOCUMENT,
            config.AGENT_FINALIZE: config.AGENT_FINALIZE,
        },
    )
    builder.add_edge(config.AGENT_FINALIZE, END)

    return builder.compile()
