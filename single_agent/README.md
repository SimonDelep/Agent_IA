# Agent unique — MCP + RAG

Un seul agent Azure OpenAI (API Responses) qui combine :

- **14 outils MCP** du serveur NordTrail Gear ([`Serveur_MCP/mcp_server/server.py`](../Serveur_MCP/mcp_server/server.py))
- **`search_company_documents`** — recherche dans la base documentaire Chroma ([`Rag_project`](../Rag_project/)), sans second appel LLM dans l'outil

Le dossier [`Agent/`](../Agent/) n'est pas modifié.

## Prérequis

1. **Base SQLite + API FastAPI**

```bash
cd Serveur_MCP
python database/seed_database.py
pip install -r requirements.txt
uvicorn api.main:app --reload --port 8000
```

2. **Index Chroma (RAG)**

```bash
cd Rag_project
# Fichier .env ou dev.env avec clés Azure + Chroma
python ingest_azure.py   # ou votre script d'ingestion habituel
```

3. **Variables Azure** — copier le modèle à la racine du dépôt, puis renseigner vos clés :

```bash
cp dev.env.example dev.env
```

Le fichier `dev.env` n'est jamais versionné. Variables requises :

- `AZURE_OPENAI_API_KEY`
- `AZURE_OPENAI_ENDPOINT`
- `AZURE_OPENAI_API_VERSION`
- `AZURE_OPENAI_DEPLOYMENT`

Pour le RAG seul, vous pouvez aussi utiliser un `.env` dans `Rag_project/` (voir [`Rag_project/.env.example`](../Rag_project/.env.example)).

4. **Dépendances agent**

```bash
pip install -r single_agent/requirements.txt
pip install -r Serveur_MCP/requirements.txt
```

## Vérification rapide (sans Azure)

```bash
python -m single_agent.smoke_test
```

Valide la connexion MCP (14 outils + `check_api_health`) et, si `dev.env` / Chroma sont configurés, une recherche RAG.

## Lancement

Depuis la racine du dépôt `Agent_IA` :

```bash
python -m single_agent.main
```

Mode interactif : une question par ligne (`quit` pour quitter).

Exemples intégrés au démarrage si vous lancez sans argument (voir `main.py`).

## Architecture

```text
Question utilisateur
    → Azure Responses API (boucle outils)
    → search_company_documents  →  Rag_project.retrieve()
    → outils MCP (stdio)        →  API REST :8000
    → Réponse finale en français
```

## Variables optionnelles

| Variable | Défaut | Description |
|----------|--------|-------------|
| `NORDTRAIL_API_URL` | `http://127.0.0.1:8000` | URL API NordTrail |
| `MCP_COMMAND` | `python` | Exécutable pour le serveur MCP |
| `MAX_TOOL_ITERATIONS` | `10` | Limite de tours outils |
| `TOP_K` | `5` | Chunks RAG par recherche |

## Dépannage

- **Erreur MCP / connexion** : vérifier que l'API tourne sur le port configuré (`check_api_health` via MCP).
- **RAG vide** : ré-ingérer les documents et vérifier `CHROMA_PATH` dans l'environnement Rag_project.
- **Clés manquantes** : copier `dev.env.example` vers `dev.env` à la racine, ou configurer `Rag_project/.env`.
