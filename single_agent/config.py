"""
Configuration centralisée pour l'agent unique.
Charge les variables d'environnement avant tout import Rag_project.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

from dotenv import load_dotenv

REPO_ROOT = Path(__file__).resolve().parent.parent
RAG_PROJECT_ROOT = REPO_ROOT / "Rag_project"
SERVEUR_MCP_ROOT = REPO_ROOT / "Serveur_MCP"

# Azure OpenAI (agent orchestrateur — même convention que Agent/)
load_dotenv(REPO_ROOT / "dev.env")
load_dotenv(REPO_ROOT / "Agent" / "dev.env")
load_dotenv(RAG_PROJECT_ROOT / "dev.env")
load_dotenv(RAG_PROJECT_ROOT / ".env")

AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION")
AZURE_OPENAI_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT")

# MCP subprocess
MCP_COMMAND = os.getenv("MCP_COMMAND", "python")
MCP_SERVER_MODULE = os.getenv("MCP_SERVER_MODULE", "mcp_server.server")
NORDTRAIL_API_URL = os.getenv("NORDTRAIL_API_URL", "http://127.0.0.1:8000")

MAX_TOOL_ITERATIONS = int(os.getenv("MAX_TOOL_ITERATIONS", "10"))
DEFAULT_RAG_TOP_K = int(os.getenv("TOP_K", "5"))


def ensure_rag_project_on_path() -> None:
    """Permet d'importer retrieve / rag depuis Rag_project."""
    rag_path = str(RAG_PROJECT_ROOT)
    if rag_path not in sys.path:
        sys.path.insert(0, rag_path)


def get_mcp_server_params():
    from mcp.client.stdio import StdioServerParameters

    return StdioServerParameters(
        command=MCP_COMMAND,
        args=["-m", MCP_SERVER_MODULE],
        cwd=str(SERVEUR_MCP_ROOT),
        env={
            **os.environ,
            "NORDTRAIL_API_URL": NORDTRAIL_API_URL,
        },
    )
