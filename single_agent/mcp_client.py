"""
Client MCP stdio — liste et exécute les outils du serveur NordTrail Gear.
"""

from __future__ import annotations

import copy
from contextlib import asynccontextmanager
from typing import Any, AsyncIterator

from mcp import ClientSession
from mcp.client.stdio import stdio_client
from mcp.types import CallToolResult, TextContent

from single_agent.config import get_mcp_server_params


def _normalize_parameters(schema: dict[str, Any] | None) -> dict[str, Any]:
    """Adapte le JSON Schema MCP au format attendu par l'API Responses."""
    if not schema:
        return {
            "type": "object",
            "properties": {},
            "required": [],
            "additionalProperties": False,
        }

    params = copy.deepcopy(schema)
    params.pop("$schema", None)
    if params.get("type") != "object":
        params = {
            "type": "object",
            "properties": params.get("properties", {}),
            "required": params.get("required", []),
        }
    params.setdefault("additionalProperties", False)
    return params


def mcp_tool_to_responses_format(tool: Any) -> dict[str, Any]:
    """Convertit un outil MCP en définition function pour Azure OpenAI."""
    return {
        "type": "function",
        "name": tool.name,
        "description": tool.description or "",
        "parameters": _normalize_parameters(tool.inputSchema),
    }


def text_from_call_tool_result(result: CallToolResult) -> str:
    """Extrait le texte renvoyé par call_tool."""
    if result.isError:
        parts = []
        for block in result.content:
            if isinstance(block, TextContent):
                parts.append(block.text)
        return "\n".join(parts) if parts else "Erreur lors de l'appel de l'outil MCP."

    parts = []
    for block in result.content:
        if isinstance(block, TextContent):
            parts.append(block.text)
        else:
            parts.append(str(block))
    return "\n".join(parts) if parts else ""


@asynccontextmanager
async def mcp_session() -> AsyncIterator[ClientSession]:
    """
    Ouvre une session MCP stdio pour toute la durée d'un run_agent.
    """
    server_params = get_mcp_server_params()
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            yield session


async def list_mcp_tools(session: ClientSession) -> list[dict[str, Any]]:
    """Liste les outils MCP convertis au format Responses API."""
    listed = await session.list_tools()
    return [mcp_tool_to_responses_format(t) for t in listed.tools]


async def call_mcp_tool(
    session: ClientSession,
    name: str,
    arguments: dict[str, Any] | None,
) -> str:
    """Appelle un outil MCP et retourne le résultat textuel."""
    result = await session.call_tool(name, arguments or {})
    return text_from_call_tool_result(result)
