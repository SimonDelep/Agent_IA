"""
Wrappers LangChain StructuredTool autour du client MCP (session partagée).
"""

from __future__ import annotations

import re
from typing import Any

from langchain_core.tools import StructuredTool
from langsmith import traceable
from mcp import ClientSession
from pydantic import BaseModel, Field, create_model

from multi_agent import config
from single_agent.mcp_client import call_mcp_tool

TYPE_MAP: dict[str, type] = {
    "string": str,
    "integer": int,
    "number": float,
    "boolean": bool,
}

SENSITIVE_ARGUMENT_NAMES = {
    "password",
    "pass",
    "token",
    "secret",
    "api_key",
    "authorization",
    "email",
}


def _redact_args(arguments: dict[str, Any]) -> dict[str, Any]:
    redacted: dict[str, Any] = {}
    for key, value in arguments.items():
        if key.lower() in SENSITIVE_ARGUMENT_NAMES:
            redacted[key] = "[REDACTED]"
            continue
        if isinstance(value, str) and len(value) > 200:
            redacted[key] = f"{value[:200]}...[truncated]"
            continue
        redacted[key] = value
    return redacted


def _model_name_from_tool(tool_name: str) -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9]", "_", tool_name)
    if not cleaned or cleaned[0].isdigit():
        cleaned = f"Tool_{cleaned}"
    return f"{cleaned}Args"


def _json_schema_to_pydantic(tool_name: str, schema: dict[str, Any] | None) -> type[BaseModel]:
    """Convertit un JSON Schema MCP minimal en modèle Pydantic pour LangChain."""
    if not schema:
        return create_model(_model_name_from_tool(tool_name))

    properties = schema.get("properties", {})
    required = set(schema.get("required", []))
    fields: dict[str, Any] = {}

    for prop_name, prop_schema in properties.items():
        py_type = TYPE_MAP.get(prop_schema.get("type", "string"), str)
        description = prop_schema.get("description", "")
        if prop_name in required:
            fields[prop_name] = (py_type, Field(description=description))
        else:
            fields[prop_name] = (
                py_type | None,
                Field(default=None, description=description),
            )

    if not fields:
        return create_model(_model_name_from_tool(tool_name))

    return create_model(_model_name_from_tool(tool_name), **fields)


def _make_mcp_tool(
    session: ClientSession,
    mcp_tool: Any,
    *,
    agent_name: str | None = None,
) -> StructuredTool:
    name = mcp_tool.name
    description = mcp_tool.description or ""
    args_schema = _json_schema_to_pydantic(name, mcp_tool.inputSchema)

    async def _invoke(**kwargs: Any) -> str:
        filtered = {k: v for k, v in kwargs.items() if v is not None}
        traced_args = _redact_args(filtered) if config.AUDIT_VERBOSE_TRACING else {}

        @traceable(name=f"nordtrail.tool.{name}", run_type="tool")
        async def _traced_call(
            redacted_arguments: dict[str, Any],
            tool_name: str,
            tool_agent: str,
        ) -> str:
            return await call_mcp_tool(session, name, filtered)

        return await _traced_call(
            redacted_arguments=traced_args,
            tool_name=name,
            tool_agent=agent_name or "unknown_agent",
        )

    return StructuredTool(
        name=name,
        description=description,
        coroutine=_invoke,
        args_schema=args_schema,
    )


async def build_mcp_tools(
    session: ClientSession,
    tool_names: list[str],
    *,
    agent_name: str | None = None,
) -> list[StructuredTool]:
    """Construit des StructuredTool LangChain pour les outils MCP demandés."""
    listed = await session.list_tools()
    tools_by_name = {tool.name: tool for tool in listed.tools}

    missing = [name for name in tool_names if name not in tools_by_name]
    if missing:
        raise ValueError(f"Outils MCP introuvables : {', '.join(missing)}")

    return [
        _make_mcp_tool(session, tools_by_name[name], agent_name=agent_name)
        for name in tool_names
    ]
