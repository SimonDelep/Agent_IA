"""Prompts des agents spécialisés."""

from multi_agent.agents.document import DOCUMENT_PROMPT
from multi_agent.agents.orchestrator import FINALIZE_PROMPT, SUPERVISOR_PROMPT
from multi_agent.agents.product_expert import PRODUCT_EXPERT_PROMPT
from multi_agent.agents.service_client import SERVICE_CLIENT_PROMPT

__all__ = [
    "SUPERVISOR_PROMPT",
    "FINALIZE_PROMPT",
    "SERVICE_CLIENT_PROMPT",
    "PRODUCT_EXPERT_PROMPT",
    "DOCUMENT_PROMPT",
]
