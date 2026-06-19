"""
Smoke test multi-agents — MCP, RAG et compilation du graphe LangGraph.
Usage : python -m multi_agent.smoke_test
"""

from __future__ import annotations

import asyncio
import json
import sys

from multi_agent import config
from multi_agent.graph.builder import build_supervisor_graph, get_llm
from multi_agent.tools.mcp_tools import build_mcp_tools
from multi_agent.tools.rag_tool import build_rag_tool
from multi_agent.tracing.langsmith import is_tracing_enabled, setup_tracing
from single_agent.mcp_client import call_mcp_tool, list_mcp_tools, mcp_session
from single_agent.rag_tool import search_company_documents

setup_tracing()


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


async def test_graph_compile() -> bool:
    print("--- Graphe LangGraph ---")
    try:
        llm = get_llm()
        print(f"  LLM : {config.AZURE_OPENAI_DEPLOYMENT}")

        async with mcp_session() as session:
            service_tools = await build_mcp_tools(session, config.SERVICE_CLIENT_TOOLS)
            product_tools = await build_mcp_tools(session, config.PRODUCT_EXPERT_TOOLS)
            rag_tool = build_rag_tool()
            graph = await build_supervisor_graph(session)

            print(f"  Outils service_client : {len(service_tools)}")
            print(f"  Outils product_expert : {len(product_tools)}")
            print(f"  Outil documentaire : {rag_tool.name}")
            print(f"  Graphe compilé : {type(graph).__name__}")

        _ = llm
        return True
    except Exception as exc:
        print(f"  ÉCHEC : {exc}")
        return False


def test_langsmith_config() -> bool:
    print("--- LangSmith ---")
    enabled = is_tracing_enabled()
    print(f"  Tracing activé : {enabled}")
    if enabled:
        print(f"  Projet : {config.LANGCHAIN_PROJECT}")
    else:
        print("  (Optionnel) Définissez LANGCHAIN_TRACING_V2=true et LANGCHAIN_API_KEY dans dev.env")
    return True


def main() -> int:
    ok_mcp = asyncio.run(test_mcp())
    ok_rag = test_rag()
    ok_graph = asyncio.run(test_graph_compile())
    test_langsmith_config()

    if ok_mcp and ok_rag and ok_graph:
        print("\nSmoke test OK (MCP + RAG + graphe). Lancez : python -m multi_agent.main")
        return 0
    print("\nSmoke test incomplet — voir multi_agent/README.md pour les prérequis.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
