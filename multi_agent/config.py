"""
Configuration multi-agents — réutilise single_agent + variables LangSmith.
"""

from __future__ import annotations

import os

from single_agent import config as base_config

# Azure OpenAI (orchestrateur + agents spécialisés)
AZURE_OPENAI_API_KEY = base_config.AZURE_OPENAI_API_KEY
AZURE_OPENAI_ENDPOINT = base_config.AZURE_OPENAI_ENDPOINT
AZURE_OPENAI_API_VERSION = base_config.AZURE_OPENAI_API_VERSION
AZURE_OPENAI_DEPLOYMENT = base_config.AZURE_OPENAI_DEPLOYMENT

# MCP / RAG (délégation à single_agent)
MCP_COMMAND = base_config.MCP_COMMAND
MCP_SERVER_MODULE = base_config.MCP_SERVER_MODULE
NORDTRAIL_API_URL = base_config.NORDTRAIL_API_URL
DEFAULT_RAG_TOP_K = base_config.DEFAULT_RAG_TOP_K
REPO_ROOT = base_config.REPO_ROOT
RAG_PROJECT_ROOT = base_config.RAG_PROJECT_ROOT
SERVEUR_MCP_ROOT = base_config.SERVEUR_MCP_ROOT

ensure_rag_project_on_path = base_config.ensure_rag_project_on_path
get_mcp_server_params = base_config.get_mcp_server_params

# LangGraph
GRAPH_RECURSION_LIMIT = int(os.getenv("GRAPH_RECURSION_LIMIT", "50"))
MAX_SUPERVISOR_TURNS = int(os.getenv("MAX_SUPERVISOR_TURNS", "6"))

# LangSmith
LANGCHAIN_TRACING_V2 = os.getenv("LANGCHAIN_TRACING_V2", "false").lower() == "true"
LANGCHAIN_ENDPOINT = os.getenv("LANGCHAIN_ENDPOINT", "https://api.smith.langchain.com")
LANGCHAIN_API_KEY = os.getenv("LANGCHAIN_API_KEY")
LANGCHAIN_PROJECT = os.getenv("LANGCHAIN_PROJECT", "nordtrail-multi-agent")

# Noms des nœuds / agents
AGENT_SERVICE_CLIENT = "service_client"
AGENT_PRODUCT_EXPERT = "product_expert"
AGENT_DOCUMENT = "document"
AGENT_SUPERVISOR = "supervisor"
AGENT_FINALIZE = "finalize"

SERVICE_CLIENT_TOOLS = [
    "get_client_by_email",
    "get_client",
    "get_order_status",
    "list_client_orders",
    "cancel_order",
    "create_return_request",
    "get_return",
    "list_returns",
    "update_return_status",
    "validate_coupon",
]

PRODUCT_EXPERT_TOOLS = [
    "search_products",
    "get_product",
    "get_product_stock",
]

DOCUMENT_TOOLS = [
    "search_company_documents",
]


def bootstrap_langsmith() -> bool:
    """
    Exporte les variables LangSmith dans os.environ.
    Doit s'exécuter avant tout import langchain_core / langgraph.
    """
    if not LANGCHAIN_TRACING_V2 or not LANGCHAIN_API_KEY:
        return False

    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    os.environ["LANGCHAIN_ENDPOINT"] = LANGCHAIN_ENDPOINT
    os.environ["LANGCHAIN_API_KEY"] = LANGCHAIN_API_KEY
    os.environ["LANGCHAIN_PROJECT"] = LANGCHAIN_PROJECT
    return True


bootstrap_langsmith()
