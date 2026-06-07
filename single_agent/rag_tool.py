"""
Outil RAG — recherche documentaire Azure AI Search sans génération LLM imbriquée.
"""

from __future__ import annotations

import json
from typing import Any

from single_agent.config import DEFAULT_RAG_TOP_K, ensure_rag_project_on_path

ensure_rag_project_on_path()

from rag import build_context, get_unique_sources  # noqa: E402
from retrieve_azure import retrieve  # noqa: E402


RAG_TOOL_DEFINITION: dict[str, Any] = {
    "type": "function",
    "name": "search_company_documents",
    "description": (
        "Recherche dans les documents internes NordTrail Gear (politiques de retour, "
        "garantie, livraison, annulation, SAV, catalogue). "
        "Retourne des extraits et les noms de sources. "
        "À utiliser pour les règles métier avant de promettre une action au client."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Question ou mots-clés à rechercher dans la base documentaire",
            },
            "top_k": {
                "type": "integer",
                "description": f"Nombre de passages à récupérer (défaut {DEFAULT_RAG_TOP_K})",
            },
        },
        "required": ["query"],
        "additionalProperties": False,
    },
}


def search_company_documents(query: str, top_k: int | None = None) -> str:
    """
    Recherche sémantique Azure AI Search — retourne contexte et sources en JSON.
    """
    k = top_k if top_k is not None else DEFAULT_RAG_TOP_K
    chunks = retrieve(query=query, top_k=k)

    if not chunks:
        return json.dumps(
            {
                "found": False,
                "sources": [],
                "context": "",
                "message": "Aucun document pertinent trouvé.",
            },
            ensure_ascii=False,
        )

    return json.dumps(
        {
            "found": True,
            "sources": get_unique_sources(chunks),
            "context": build_context(chunks),
        },
        ensure_ascii=False,
    )
