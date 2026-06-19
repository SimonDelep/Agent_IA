# Multi-agents — LangGraph + LangSmith

Architecture multi-agents pour NordTrail Gear avec un **supervisor LangGraph** et **LangSmith** pour l'observabilité. Le package [`single_agent/`](../single_agent/) reste intact comme référence monolithique.

## Agents

| Agent | Outils | Rôle |
|-------|--------|------|
| **Orchestrateur** | Routage structuré (`next` → agent ou `FINISH`) | Coordonne les spécialistes, synthèse finale |
| **Service client** | 10 outils MCP (commandes, retours, clients, coupons) | Actions transactionnelles SAV |
| **Expert produit** | 3 outils MCP (catalogue, stock) | Recommandations et disponibilité |
| **Documentaire** | `search_company_documents` (RAG ChromaDB) | Politiques entreprise |

## Prérequis

Identiques à `single_agent/` :

1. **API FastAPI** sur le port **8001** (évite le conflit avec ChromaDB sur 8000)
2. **Index ChromaDB** ingéré (`python Rag_project/ingest.py`)
3. **Variables Azure** dans `dev.env` à la racine du dépôt
4. **Compte LangSmith** (optionnel mais recommandé pour l'observabilité)

```bash
cd Serveur_MCP
python database/seed_database.py
pip install -r requirements.txt
uvicorn api.main:app --reload --port 8001
```

```bash
pip install -r multi_agent/requirements.txt
pip install -r single_agent/requirements.txt
pip install -r Serveur_MCP/requirements.txt
```

## Configuration LangSmith

Ajoutez dans `dev.env` :

```env
LANGCHAIN_TRACING_V2=true
LANGCHAIN_ENDPOINT=https://api.smith.langchain.com
LANGCHAIN_API_KEY=lsv2_pt_...
LANGCHAIN_PROJECT=nordtrail-multi-agent
```

> **Important :** `LANGCHAIN_TRACING_V2` doit être `true` (pas seulement la clé API).

Chaque exécution apparaît dans [smith.langchain.com](https://smith.langchain.com) avec :
- Span racine `nordtrail_multi_agent_run`
- Nœuds LangGraph : `supervisor` → agents spécialisés → `finalize`
- Appels LLM et tool calls MCP/RAG

## Vérification rapide

```bash
python -m multi_agent.smoke_test
```

Valide MCP (14 outils), RAG ChromaDB et la compilation du graphe LangGraph.

## Lancement

Depuis la racine `Agent_IA` :

```bash
python -m multi_agent.main
```

Mode interactif ou question unique :

```bash
python -m multi_agent.main "Quelle est la politique de retour pour une chaussure portée 10 jours ?"
```

### Interface Streamlit

```bash
python -m streamlit run multi_agent/app.py
```

Ouvrez l'URL affichée (défaut `http://localhost:8501`). La barre latérale affiche **LangSmith : activé** si `LANGCHAIN_TRACING_V2=true` et `LANGCHAIN_API_KEY` sont définis dans `dev.env`.

## Architecture

```text
Question utilisateur
    → LangGraph Supervisor
        → service_client  → MCP (commandes, retours, clients)
        → product_expert  → MCP (catalogue, stock)
        → document        → RAG (ChromaDB via single_agent.rag_tool)
        → finalize        → synthèse réponse finale
    → LangSmith (traces)
```

```text
multi_agent/
├── graph/builder.py      # StateGraph supervisor + create_react_agent
├── agents/               # Prompts spécialisés
├── tools/                # Wrappers LangChain (MCP + RAG)
├── tracing/langsmith.py  # Setup observabilité
└── runner.py             # run_multi_agent_async()
```

## Comparaison avec single_agent/

| | `single_agent/` | `multi_agent/` |
|--|-----------------|----------------|
| Pattern | Agent unique, 15 outils | Supervisor + 3 spécialistes |
| API LLM | Azure Responses API | Azure Chat Completions (LangChain) |
| RAG | ChromaDB (`retrieve.py`) | ChromaDB (délégation à `single_agent.rag_tool`) |
| Routage | Implicite (prompt) | Explicite (supervisor structuré) |
| Observabilité | Aucune | LangSmith |

## Variables optionnelles

| Variable | Défaut | Description |
|----------|--------|-------------|
| `GRAPH_RECURSION_LIMIT` | `50` | Limite de récursion LangGraph (steps totaux) |
| `MAX_SUPERVISOR_TURNS` | `6` | Tours max du supervisor avant FINISH forcé |
| `LANGCHAIN_PROJECT` | `nordtrail-multi-agent` | Projet LangSmith |
| `NORDTRAIL_API_URL` | `http://127.0.0.1:8001` | URL API NordTrail |

## Dépannage

- **API non joignable** : démarrer `uvicorn api.main:app --port 8001` dans `Serveur_MCP/`
- **RAG Chroma `default_tenant`** : API sur port **8001** (pas 8000), `chromadb>=1.0`, réingérer : `python Rag_project/ingest.py` (fermer Streamlit avant)
- **Traces LangSmith absentes** : vérifier `LANGCHAIN_TRACING_V2=true` et `LANGCHAIN_API_KEY` avant le lancement
- **Boucles supervisor** : augmenter `GRAPH_RECURSION_LIMIT` ou reformuler la question
