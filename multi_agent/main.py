"""
CLI de démonstration pour le système multi-agents NordTrail Gear.
"""

from __future__ import annotations

import sys

from multi_agent.runner import run_multi_agent
from multi_agent.tracing.langsmith import is_tracing_enabled, setup_tracing

setup_tracing()

SAMPLE_QUESTIONS = [
    (
        "Quelle est la politique de retour pour une chaussure portée environ "
        "10 jours ? Cite les sources documentaires."
    ),
    (
        "Quel est le statut de la commande NTG-2026-000201 et quelles informations "
        "as-tu sur le client associé ?"
    ),
    (
        "Le client felix.roy@example.ca demande d'annuler sa commande (id de commande : NTG-2026-000208). "
        "Vérifie d'abord les règles d'annulation dans les documents, puis le statut "
        "de sa commande via l'API."
    ),
]


def _run_question(question: str) -> None:
    print("=" * 80)
    print("QUESTION :", question)
    print()
    try:
        answer = run_multi_agent(question)
    except Exception as exc:
        print("ERREUR :", exc)
        return
    print("RÉPONSE :")
    print(answer)
    print()


def main() -> None:
    tracing_status = "activé" if is_tracing_enabled() else "désactivé"
    print(f"Multi-agents NordTrail Gear — LangGraph + LangSmith (tracing {tracing_status})")

    if len(sys.argv) > 1:
        _run_question(" ".join(sys.argv[1:]))
        return

    print("Entrez une question (ligne vide = exemples intégrés, 'quit' pour quitter).\n")

    try:
        first = input("Question : ").strip()
    except (EOFError, KeyboardInterrupt):
        print()
        return

    if first.lower() in ("quit", "exit", "q"):
        return

    if first:
        _run_question(first)
        return

    for question in SAMPLE_QUESTIONS:
        _run_question(question)


if __name__ == "__main__":
    main()
