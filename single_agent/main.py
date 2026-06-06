"""
CLI de démonstration pour l'agent unique MCP + RAG.
"""

from __future__ import annotations

import sys

from single_agent.agent import run_agent

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
        "Le client marie.tremblay@email.com demande d'annuler sa commande en attente. "
        "Vérifie d'abord les règles d'annulation dans les documents, puis le statut "
        "de sa commande via l'API."
    ),
]


def _run_question(question: str) -> None:
    print("=" * 80)
    print("QUESTION :", question)
    print()
    try:
        answer = run_agent(question)
    except Exception as exc:
        print("ERREUR :", exc)
        return
    print("RÉPONSE :")
    print(answer)
    print()


def main() -> None:
    if len(sys.argv) > 1:
        _run_question(" ".join(sys.argv[1:]))
        return

    print("Agent unique NordTrail Gear — MCP + RAG")
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
