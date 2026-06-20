"""Wrapper LangChain pour l'outil RAG documentaire."""

from __future__ import annotations

from typing import Any

from langchain_core.tools import StructuredTool
from langsmith import traceable
from pydantic import BaseModel, Field

from multi_agent import config
from single_agent.rag_tool import search_company_documents


class SearchDocumentsInput(BaseModel):
    query: str = Field(description="Question ou mots-clés à rechercher dans la base documentaire")
    top_k: int | None = Field(
        default=None,
        description=f"Nombre de passages à récupérer (défaut {config.DEFAULT_RAG_TOP_K})",
    )


def build_rag_tool(*, agent_name: str = "document") -> StructuredTool:
    """Construit l'outil search_company_documents pour LangGraph."""

    def _search(query: str, top_k: int | None = None) -> str:
        kwargs: dict[str, Any] = {"query": query}
        if top_k is not None:
            kwargs["top_k"] = top_k

        traced_query = query[:200] + ("...[truncated]" if len(query) > 200 else "")
        traced_input = {"query": traced_query, "top_k": top_k}
        if not config.AUDIT_VERBOSE_TRACING:
            traced_input = {}

        @traceable(name="nordtrail.tool.search_company_documents", run_type="tool")
        def _traced_search(
            redacted_arguments: dict[str, Any],
            tool_name: str,
            tool_agent: str,
        ) -> str:
            return search_company_documents(**kwargs)

        return _traced_search(
            redacted_arguments=traced_input,
            tool_name="search_company_documents",
            tool_agent=agent_name,
        )

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
