"""Wrapper LangChain pour l'outil RAG documentaire."""

from __future__ import annotations

from typing import Any

from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field

from multi_agent import config
from single_agent.rag_tool import search_company_documents


class SearchDocumentsInput(BaseModel):
    query: str = Field(description="Question ou mots-clés à rechercher dans la base documentaire")
    top_k: int | None = Field(
        default=None,
        description=f"Nombre de passages à récupérer (défaut {config.DEFAULT_RAG_TOP_K})",
    )


def build_rag_tool() -> StructuredTool:
    """Construit l'outil search_company_documents pour LangGraph."""

    def _search(query: str, top_k: int | None = None) -> str:
        kwargs: dict[str, Any] = {"query": query}
        if top_k is not None:
            kwargs["top_k"] = top_k
        return search_company_documents(**kwargs)

    return StructuredTool.from_function(
        func=_search,
        name="search_company_documents",
        description=(
            "Recherche dans les documents internes NordTrail Gear (politiques de retour, "
            "garantie, livraison, annulation, SAV, catalogue). "
            "Retourne des extraits et les noms de sources. "
            "À utiliser pour les règles métier avant de promettre une action au client."
        ),
        args_schema=SearchDocumentsInput,
    )
