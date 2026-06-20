"""
Guardrails d'entree utilisateur pour limiter les prompt injections.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from multi_agent import config

SENSITIVE_KEYWORDS = (
    "api_key",
    "token",
    "secret",
    "mot de passe",
    "password",
    "confidentiel",
    "interne",
    "document interne",
    "donnees sensibles",
)

INJECTION_PATTERNS: tuple[tuple[str, str], ...] = (
    (
        "instruction_override",
        r"(ignore|oublie|bypass|contourne).{0,60}(instructions?|regles?|politiques?|system)",
    ),
    (
        "data_exfiltration",
        r"(affiche|donne|revele|exporte|liste).{0,80}(documents?|secrets?|tokens?|api[_\s-]?keys?)",
    ),
    (
        "jailbreak",
        r"(mode\s+developpeur|developer\s+mode|jailbreak|prompt\s+injection|system\s+prompt)",
    ),
    (
        "credential_harvesting",
        r"(fichier\.env|env\s+vars|variables?\s+d[' ]environnement|credentials?)",
    ),
)

SAFE_BLOCK_MESSAGE = (
    "Votre demande a ete bloquee par la politique de securite car elle semble viser "
    "des informations confidentielles ou un contournement des instructions. "
    "Reformulez votre question sur un besoin client legitime (commande, retour, produit, politique)."
)


@dataclass(frozen=True)
class GuardrailDecision:
    allow: bool
    reason: str
    matched_rule: str | None = None


def _normalize_text(user_text: str) -> str:
    return " ".join((user_text or "").strip().lower().split())


def evaluate_user_input_guardrail(user_text: str) -> GuardrailDecision:
    """
    Evalue l'entree utilisateur pour bloquer les injections evidentes.
    """
    if not config.GUARDRAIL_ENABLED:
        return GuardrailDecision(allow=True, reason="guardrail_disabled")

    normalized = _normalize_text(user_text)
    if not normalized:
        return GuardrailDecision(allow=False, reason="empty_prompt", matched_rule="empty_prompt")

    for rule_name, pattern in INJECTION_PATTERNS:
        if re.search(pattern, normalized, flags=re.IGNORECASE | re.DOTALL):
            return GuardrailDecision(allow=False, reason="prompt_injection_detected", matched_rule=rule_name)

    sensitive_hits = [kw for kw in SENSITIVE_KEYWORDS if kw in normalized]
    if len(sensitive_hits) >= 2:
        return GuardrailDecision(
            allow=False,
            reason="sensitive_exfiltration_intent",
            matched_rule="sensitive_keywords",
        )

    return GuardrailDecision(allow=True, reason="ok")


def guardrail_user_message() -> str:
    return SAFE_BLOCK_MESSAGE
