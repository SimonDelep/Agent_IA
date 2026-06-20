"""
Interface Streamlit — assistant service client NordTrail Gear (multi-agents).

Lancement depuis la racine du dépôt :
    python -m streamlit run multi_agent/app.py
"""

from __future__ import annotations

import sys
from pathlib import Path

# Streamlit exécute ce fichier depuis multi_agent/ : ajouter la racine du dépôt au path.
_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from multi_agent import config  # noqa: F401 — bootstrap LangSmith avant LangChain

import streamlit as st

from multi_agent.runner import run_multi_agent_chat
from multi_agent.security.guardrails import (
    evaluate_user_input_guardrail,
    guardrail_user_message,
)
from multi_agent.tracing.langsmith import setup_tracing

setup_tracing()

st.set_page_config(
    page_title="NordTrail Gear — Assistant",
    page_icon="🏔️",
    layout="centered",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
    <style>
        [data-testid="stSidebar"] { display: none; }
        [data-testid="stSidebarCollapsedControl"] { display: none; }
    </style>
    """,
    unsafe_allow_html=True,
)

WELCOME_MESSAGE = (
    "Bonjour ! Je suis l'assistant service client NordTrail Gear. "
    "Posez-moi vos questions sur les commandes, retours, produits ou politiques d'entreprise."
)

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": WELCOME_MESSAGE}]

header_col, action_col = st.columns([5, 1])
with header_col:
    st.title("NordTrail Gear")
    st.caption("Assistant service client multi-agents")
with action_col:
    if st.button("Effacer", use_container_width=True):
        st.session_state.messages = [{"role": "assistant", "content": WELCOME_MESSAGE}]
        st.rerun()

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Posez votre question…"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    decision = evaluate_user_input_guardrail(prompt)

    with st.spinner("Les agents traitent votre demande…"):
        try:
            if not decision.allow:
                if config.GUARDRAIL_BLOCK_MODE == "hard":
                    answer = guardrail_user_message()
                else:
                    answer = run_multi_agent_chat(
                        st.session_state.messages,
                        guardrail_verdict="blocked_soft",
                        guardrail_reason=decision.reason,
                        guardrail_rule=decision.matched_rule,
                    )
            else:
                answer = run_multi_agent_chat(
                    st.session_state.messages,
                    guardrail_verdict="allow",
                    guardrail_reason=decision.reason,
                    guardrail_rule=decision.matched_rule,
                )
            st.session_state.messages.append({"role": "assistant", "content": answer})
        except Exception as exc:
            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": f"Désolé, une erreur s'est produite : {exc}",
                }
            )

    st.rerun()
