"""
Agent unique NordTrail Gear — boucle Azure Responses + MCP + RAG.
"""

from __future__ import annotations

import asyncio
import json
from typing import Any

from mcp import ClientSession
from openai import AzureOpenAI

from single_agent import config
from single_agent.mcp_client import call_mcp_tool, list_mcp_tools, mcp_session
from single_agent.rag_tool import RAG_TOOL_DEFINITION, search_company_documents

AGENT_INSTRUCTIONS = """
Tu es l'assistant service client de NordTrail Gear (e-commerce outdoor, CAD).

Règles :
- Réponds en français, de manière claire, professionnelle et structurée.
- Utilise search_company_documents pour les politiques internes (retours, garantie,
  livraison, annulation, SAV). Fonde tes affirmations sur le champ "context" et cite
  les "sources" retournées.
- Utilise les outils MCP pour les données en temps réel : commandes, clients,
  produits, retours, coupons.
- Flux typique : identifier client/commande (MCP) → vérifier les règles (RAG) →
  agir via MCP si la politique le permet.
- Ne invente pas de règles ni de statuts ; en cas de doute ou contexte insuffisant,
  recommande une vérification par un agent humain.
- Avant cancel_order ou create_return_request, vérifie le statut et l'éligibilité.
""".strip()


def _get_client() -> AzureOpenAI:
    if not config.AZURE_OPENAI_API_KEY or not config.AZURE_OPENAI_ENDPOINT:
        raise ValueError(
            "Configuration Azure manquante. Définissez AZURE_OPENAI_API_KEY et "
            "AZURE_OPENAI_ENDPOINT dans dev.env à la racine du dépôt."
        )
    if not config.AZURE_OPENAI_DEPLOYMENT:
        raise ValueError(
            "AZURE_OPENAI_DEPLOYMENT manquant dans dev.env."
        )

    return AzureOpenAI(
        api_key=config.AZURE_OPENAI_API_KEY,
        api_version=config.AZURE_OPENAI_API_VERSION,
        azure_endpoint=config.AZURE_OPENAI_ENDPOINT,
    )


async def _dispatch_tool(
    session: ClientSession,
    tool_name: str,
    arguments: dict[str, Any],
) -> str:
    if tool_name == "search_company_documents":
        return search_company_documents(**arguments)
    return await call_mcp_tool(session, tool_name, arguments)


async def run_agent_async(user_question: str) -> str:
    """
    Exécute l'agent avec session MCP ouverte pour toute la conversation outils.
    """
    client = _get_client()
    model = config.AZURE_OPENAI_DEPLOYMENT

    async with mcp_session() as session:
        mcp_tools = await list_mcp_tools(session)
        tools = mcp_tools + [RAG_TOOL_DEFINITION]

        response = client.responses.create(
            model=model,
            instructions=AGENT_INSTRUCTIONS,
            input=user_question,
            tools=tools,
        )

        for _ in range(config.MAX_TOOL_ITERATIONS):
            function_calls = [
                item for item in response.output
                if item.type == "function_call"
            ]

            if not function_calls:
                return response.output_text or ""

            tool_outputs = []

            for call in function_calls:
                tool_name = call.name
                arguments = json.loads(call.arguments)
                result = await _dispatch_tool(session, tool_name, arguments)

                tool_outputs.append({
                    "type": "function_call_output",
                    "call_id": call.call_id,
                    "output": result,
                })

            response = client.responses.create(
                model=model,
                previous_response_id=response.id,
                input=tool_outputs,
            )

        return (
            response.output_text
            or "Limite d'itérations atteinte sans réponse finale."
        )


def run_agent(user_question: str) -> str:
    """Point d'entrée synchrone pour scripts et CLI."""
    return asyncio.run(run_agent_async(user_question))
