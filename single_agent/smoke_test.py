"""
Tests manuels légers (sans appel Azure) pour valider MCP et RAG.
Usage : python -m single_agent.smoke_test
"""

from __future__ import annotations

import asyncio
import json
import sys

from single_agent.mcp_client import call_mcp_tool, list_mcp_tools, mcp_session
from single_agent.rag_tool import search_company_documents


async def test_mcp() -> bool:
    print("--- MCP ---")
    try:
        async with mcp_session() as session:
            tools = await list_mcp_tools(session)
            print(f"  Outils listés : {len(tools)}")
            health = await call_mcp_tool(session, "check_api_health", {})
            print(f"  check_api_health : {health[:120]}...")
        return True
    except Exception as exc:
        print(f"  ÉCHEC : {exc}")
        return False


def test_rag() -> bool:
    print("--- RAG ---")
    try:
        result = json.loads(
            search_company_documents("politique de retour chaussures", top_k=2)
        )
        print(f"  found={result.get('found')}, sources={result.get('sources', [])}")
        if result.get("context"):
            print(f"  context (extrait) : {result['context'][:200]}...")
        return True
    except Exception as exc:
        print(f"  ÉCHEC : {exc}")
        return False


def main() -> int:
    ok_mcp = asyncio.run(test_mcp())
    ok_rag = test_rag()
    if ok_mcp and ok_rag:
        print("\nSmoke test OK (MCP + RAG). Lancez l'agent avec dev.env configuré.")
        return 0
    print("\nSmoke test incomplet — voir README pour les prérequis.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
