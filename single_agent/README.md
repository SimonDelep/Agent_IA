# Agent unique — MCP + RAG (ChromaDB)

Un seul agent Azure OpenAI (API Responses) qui combine :

- **14 outils MCP** du serveur NordTrail Gear ([`Serveur_MCP/mcp_server/server.py`](../Serveur_MCP/mcp_server/server.py))
- **`search_company_documents`** — recherche dans **ChromaDB** ([`Rag_project/retrieve.py`](../Rag_project/retrieve.py)), sans second appel LLM dans l'outil

Le dossier [`Agent/`](../Agent/) n'est pas modifié.

## Prérequis

1. **Base SQLite + API FastAPI** (port **8001** — évite le conflit avec ChromaDB sur 8000)

```bash
cd Serveur_MCP
python database/seed_database.py
pip install -r requirements.txt
uvicorn api.main:app --reload --port 8001
```

2. **Index ChromaDB (RAG)**

Depuis la racine du dépôt, configurez `dev.env` (voir ci-dessous), puis ingérez les documents :

```bash
python Rag_project/ingest.py
```

Le script vectorise les fichiers de `Rag_project/documents/` et stocke l'index dans `CHROMA_PATH` (défaut : `./db/chroma_store` à la racine du dépôt).

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

**RAG (embeddings + ChromaDB)**

- `AZURE_OPENAI_EMBEDDING_MODEL`
- `CHROMA_PATH` (optionnel, défaut `./db/chroma_store`)
- `CHROMA_COLLECTION` (optionnel, défaut `nordtrail_documents`)

**API NordTrail**

- `NORDTRAIL_API_URL` (défaut `http://127.0.0.1:8001`)

4. **Dépendances agent**

```bash
pip install -r single_agent/requirements.txt
pip install -r Serveur_MCP/requirements.txt
```

## Vérification rapide

```bash
python -m single_agent.smoke_test
```

Valide la connexion MCP (14 outils + `check_api_health`) et une recherche RAG dans ChromaDB.

> Le smoke test appelle Azure pour les embeddings. L'API FastAPI doit tourner pour la partie MCP, et l'index Chroma doit être ingéré.

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
    → search_company_documents  →  Rag_project.retrieve()  →  ChromaDB
    → outils MCP (stdio)        →  API REST :8001
    → Réponse finale en français
```

## Variables optionnelles

| Variable | Défaut | Description |
|----------|--------|-------------|
| `NORDTRAIL_API_URL` | `http://127.0.0.1:8001` | URL API NordTrail |
| `MCP_COMMAND` | `python` | Exécutable pour le serveur MCP |
| `MAX_TOOL_ITERATIONS` | `10` | Limite de tours outils |
| `TOP_K` | `5` | Passages RAG par recherche |
| `DOCUMENTS_FOLDER` | `Rag_project/documents` | Dossier source pour `ingest.py` |
| `CHUNK_SIZE` | `1500` | Taille des chunks à l'ingestion |
| `CHUNK_OVERLAP` | `150` | Chevauchement entre chunks |

## Dépannage

- **Erreur MCP / connexion** : vérifier que l'API tourne sur le port configuré (`check_api_health` via MCP).
- **RAG vide (`found=false`)** : relancer `python Rag_project/ingest.py` et vérifier `CHROMA_PATH` / `AZURE_OPENAI_EMBEDDING_MODEL` dans `dev.env`.
- **Erreur Chroma `default_tenant`** : API sur port **8001** (pas 8000), `chromadb>=1.0`, réingérer après fermeture de Streamlit si besoin.
- **Clés manquantes** : copier `dev.env.example` vers `dev.env` à la racine du dépôt.

## RAG Azure AI Search — optionnel

Pour un index cloud au lieu de ChromaDB, utilisez `Rag_project/ingest_azure.py` et adaptez `single_agent/rag_tool.py` pour importer `retrieve_azure` au lieu de `retrieve`. Par défaut, l'agent utilise **ChromaDB local**.

## Voir aussi — multi_agent/

Pour une architecture supervisor avec observabilité et sécurité renforcée, voir [`multi_agent/README.md`](../multi_agent/README.md) :

- **Guardrail anti prompt-injection** sur l'entrée Streamlit (`GUARDRAIL_ENABLED`, `GUARDRAIL_BLOCK_MODE`)
- **Traces LangSmith auditables** : runs agents (`nordtrail.agent.*`), outils (`nordtrail.tool.*`), tags `guardrail:*` et metadata de corrélation
