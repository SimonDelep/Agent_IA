"""État partagé du graphe supervisor."""

from __future__ import annotations

from langgraph.graph import MessagesState


class AgentState(MessagesState):
    """Messages de conversation + routage supervisor et anti-boucle."""

    next: str
    agents_visited: list[str]
    supervisor_turns: int
