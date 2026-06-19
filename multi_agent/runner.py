"""
Point d'entrée async — exécute le graphe multi-agents avec tracing LangSmith.
"""

from __future__ import annotations

import hashlib

from multi_agent import config  # noqa: F401 — bootstrap LangSmith avant LangChain

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from langsmith import traceable

from multi_agent.graph.builder import build_supervisor_graph
from single_agent.mcp_client import mcp_session

ChatTurn = dict[str, str]


def _chat_turns_to_messages(turns: list[ChatTurn]) -> list[BaseMessage]:
    messages: list[BaseMessage] = []
    for turn in turns:
        role = turn.get("role", "")
        content = (turn.get("content") or "").strip()
        if not content:
            continue
        if role == "user":
            messages.append(HumanMessage(content=content))
        elif role == "assistant":
            messages.append(AIMessage(content=content))
    return messages


def _extract_response(messages: list) -> str:
    for message in reversed(messages):
        if isinstance(message, AIMessage) and message.content:
            content = message.content
            if isinstance(content, str):
                return content
            if isinstance(content, list):
                parts = []
                for block in content:
                    if isinstance(block, str):
                        parts.append(block)
                    elif isinstance(block, dict) and block.get("type") == "text":
                        parts.append(block.get("text", ""))
                return "\n".join(p for p in parts if p)
    return "Aucune réponse générée."


@traceable(name="nordtrail_multi_agent_run", run_type="chain")
async def run_multi_agent_async(
    user_question: str,
    *,
    chat_history: list[ChatTurn] | None = None,
) -> str:
    """Exécute le graphe supervisor avec une session MCP partagée."""
    question_hash = hashlib.sha256(user_question.encode()).hexdigest()[:12]

    if chat_history:
        graph_messages = _chat_turns_to_messages(chat_history)
    else:
        graph_messages = [HumanMessage(content=user_question)]

    async with mcp_session() as session:
        graph = await build_supervisor_graph(session)
        initial_state = {
            "messages": graph_messages,
            "agents_visited": [],
            "supervisor_turns": 0,
            "next": "",
        }
        result = await graph.ainvoke(
            initial_state,
            config={
                "recursion_limit": config.GRAPH_RECURSION_LIMIT,
                "metadata": {
                    "agent_system": "multi_agent",
                    "user_question_hash": question_hash,
                },
                "tags": ["nordtrail", "multi-agent", "supervisor"],
            },
        )

    return _extract_response(result["messages"])


def run_multi_agent(user_question: str) -> str:
    """Point d'entrée synchrone pour scripts et CLI."""
    import asyncio

    return asyncio.run(run_multi_agent_async(user_question))


def run_multi_agent_chat(chat_history: list[ChatTurn]) -> str:
    """Point d'entrée synchrone pour l'interface conversationnelle Streamlit."""
    import asyncio

    user_messages = [m for m in chat_history if m.get("role") == "user"]
    if not user_messages:
        return "Aucune question à traiter."

    latest_question = user_messages[-1]["content"]
    return asyncio.run(
        run_multi_agent_async(latest_question, chat_history=chat_history)
    )
