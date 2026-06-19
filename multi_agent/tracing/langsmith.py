"""Configuration LangSmith — doit être appelée avant les imports LangChain."""

from __future__ import annotations

import os

from multi_agent import config


def setup_tracing() -> bool:
    """Active le tracing LangSmith (idempotent)."""
    return config.bootstrap_langsmith()


def is_tracing_enabled() -> bool:
    return os.getenv("LANGCHAIN_TRACING_V2", "").lower() == "true" and bool(
        os.getenv("LANGCHAIN_API_KEY") or config.LANGCHAIN_API_KEY
    )
