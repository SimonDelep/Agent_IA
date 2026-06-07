# Agent unique — MCP + RAG (Azure AI Search)

Un seul agent Azure OpenAI (API Responses) qui combine :

- **14 outils MCP** du serveur NordTrail Gear ([`Serveur_MCP/mcp_server/server.py`](../Serveur_MCP/mcp_server/server.py))
- **`search_company_documents`** — recherche dans **Azure AI Search** ([`Rag_project/retrieve_azure.py`](../Rag_project/retrieve_azure.py)), sans second appel LLM dans l'outil

Le dossier [`Agent/`](../Agent/) n'est pas modifié.

## Prérequis

1. **Base SQLite + API FastAPI**

```bash
cd Serveur_MCP
python database/seed_database.py
pip install -r requirements.txt
uvicorn api.main:app --reload --port 8000
```

2. **Index Azure AI Search (RAG)**

Depuis la racine du dépôt, configurez `dev.env` (voir ci-dessous), puis ingérez les documents :

```bash
cd Rag_project
python ingest_azure.py
```

Le script crée l'index s'il n'existe pas et vectorise les fichiers de `Rag_project/documents/`.

3. **Variables Azure** — copier le modèle à la racine du dépôt, puis renseigner vos clés :

```bash
cp dev.env.example dev.env
```

Le fichier `dev.env` n'est jamais versionné. Variables requises :

**Orchestrateur (Responses API)**

- `AZURE_OPENAI_API_KEY`
- `AZURE_OPENAI_ENDPOINT`
- `AZURE_OPENAI_API_VERSION`
- `AZURE_OPENAI_DEPLOYMENT`

**RAG (embeddings + Azure AI Search)**

- `AZURE_OPENAI_EMBEDDING_MODEL`
- `AZURE_SEARCH_API_KEY`
- `AZURE_SEARCH_ENDPOINT`
- `AZURE_SEARCH_INDEX_NAME`

4. **Dépendances agent**

```bash
pip install -r single_agent/requirements.txt
pip install -r Serveur_MCP/requirements.txt
```

## Vérification rapide

```bash
python -m single_agent.smoke_test
```

Valide la connexion MCP (14 outils + `check_api_health`) et une recherche RAG dans Azure AI Search.

> Le smoke test appelle Azure (embeddings + Search). L'API FastAPI doit tourner pour la partie MCP.

## Lancement

Depuis la racine du dépôt `Agent_IA` :

```bash
python -m single_agent.main
```

Mode interactif : une question par ligne (`quit` pour quitter).

Exemples intégrés au démarrage si vous lancez sans argument (voir `main.py`).

Question unique en ligne de commande :

```bash
python -m single_agent.main "Quelle est la politique de retour pour une chaussure portée 10 jours ?"
```

## Architecture

```text
Question utilisateur
    → Azure Responses API (boucle outils)
    → search_company_documents  →  Rag_project.retrieve_azure()  →  Azure AI Search
    → outils MCP (stdio)        →  API REST :8000
    → Réponse finale en français
```

## Variables optionnelles

| Variable | Défaut | Description |
|----------|--------|-------------|
| `NORDTRAIL_API_URL` | `http://127.0.0.1:8000` | URL API NordTrail |
| `MCP_COMMAND` | `python` | Exécutable pour le serveur MCP |
| `MAX_TOOL_ITERATIONS` | `10` | Limite de tours outils |
| `TOP_K` | `5` | Passages RAG par recherche |
| `DOCUMENTS_FOLDER` | `Rag_project/documents` | Dossier source pour `ingest_azure.py` |
| `CHUNK_SIZE` | `1500` | Taille des chunks à l'ingestion |
| `CHUNK_OVERLAP` | `150` | Chevauchement entre chunks |

## Dépannage

- **Erreur MCP / connexion** : vérifier que l'API tourne sur le port configuré (`check_api_health` via MCP).
- **RAG vide (`found=false`)** : relancer `python ingest_azure.py` dans `Rag_project/` et vérifier `AZURE_SEARCH_*` dans `dev.env`.
- **Erreur d'index Search** : l'ingestion recrée l'index au premier lancement ; vérifiez que la clé API Search a les droits admin.
- **Clés manquantes** : copier `dev.env.example` vers `dev.env` à la racine du dépôt.

## RAG local (Chroma) — optionnel

Pour un index vectoriel local (sans Azure AI Search), utilisez `Rag_project/ingest.py` et adaptez `single_agent/rag_tool.py` pour importer `retrieve` au lieu de `retrieve_azure`. Par défaut, l'agent utilise **Azure AI Search**.
