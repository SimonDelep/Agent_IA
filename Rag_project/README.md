# Assistant RAG pour service client — NordTrail Gear

Ce projet implémente la base documentaire du système d'assistant IA : un **RAG** (*Retrieval-Augmented Generation*) capable de répondre à des courriels clients en s'appuyant sur les politiques et documents internes de NordTrail Gear.

L'agent unique ([`single_agent/`](../single_agent/)) consomme cette base via **Azure AI Search** (`retrieve_azure.py`). Une variante **ChromaDB** locale reste disponible pour le développement hors cloud.

---

## Contexte du projet

Boutique en ligne spécialisée outdoor (randonnée, trail, bivouac). Le service client reçoit des demandes sur les retours, annulations, garanties, livraisons et recommandations produits.

Le RAG permet à l'assistant de s'appuyer sur les documents internes plutôt que sur les seules connaissances générales du modèle.

---

## Ce que fait le système RAG

```text
Question ou courriel client
        ↓
Recherche hybride (texte + vecteur) dans Azure AI Search
        ↓
Récupération des passages les plus pertinents
        ↓
Injection de ces passages dans le prompt (agent ou rag.py)
        ↓
Génération d'une réponse contextualisée
        ↓
Retour de la réponse avec les sources utilisées
```

---

## Documents utilisés

```text
documents/
├── politique_retours.pdf
├── politique_garantie.pdf
├── faq_livraison.md
├── conditions_annulation.md
├── guide_tailles.md
├── procedure_sav_interne.md
├── catalogue_produits.csv
├── clients_exemples.json
├── commandes_exemples.json
└── emails_clients_test.csv   # évaluation uniquement — non indexé
```

---

## Structure du projet

```text
Rag_project/
├── config.py              # Variables d'environnement (lit dev.env à la racine)
├── utils.py               # Chargement, nettoyage, chunking
├── embeddings.py          # Embeddings Azure OpenAI
├── ingest_azure.py        # Ingestion → Azure AI Search (backend par défaut)
├── retrieve_azure.py        # Recherche hybride Azure AI Search
├── ingest.py              # Ingestion → ChromaDB (option local)
├── retrieve.py            # Recherche ChromaDB (option local)
├── vectorstore.py         # Interface ChromaDB
├── rag.py                 # Pipeline RAG complet (retrieve + LLM)
├── rag_test.py            # Tests Azure Search + LLM
├── documents/
└── README.md
```

| Fichier | Rôle |
|---|---|
| `ingest_azure.py` | Indexe les documents dans Azure AI Search (utilisé par `single_agent`) |
| `retrieve_azure.py` | Recherche hybride dans l'index Azure |
| `ingest.py` / `retrieve.py` | Variante locale ChromaDB |
| `rag.py` | Pipeline RAG autonome avec génération LLM |
| `embeddings.py` | Génération des embeddings via Azure OpenAI |

---

## Installation

```bash
pip install openai chromadb pypdf python-dotenv azure-search-documents
```

Ou, depuis la racine du dépôt :

```bash
pip install -r single_agent/requirements.txt
```

---

## Configuration

Les variables sont centralisées dans `dev.env` à la **racine du dépôt** (`Agent_IA/dev.env`). `config.py` charge ce fichier automatiquement.

```bash
cp ../dev.env.example ../dev.env
```

Variables essentielles :

```env
# Azure OpenAI
AZURE_OPENAI_API_KEY=...
AZURE_OPENAI_ENDPOINT=...
AZURE_OPENAI_API_VERSION=2025-04-01-preview
AZURE_OPENAI_EMBEDDING_MODEL=nordtrail-embedding
AZURE_OPENAI_DEPLOYMENT=nordtrail-llm          # pour rag.py

# Azure AI Search
AZURE_SEARCH_API_KEY=...
AZURE_SEARCH_ENDPOINT=https://your-search.search.windows.net
AZURE_SEARCH_INDEX_NAME=index-rag-canadien

# Ingestion
DOCUMENTS_FOLDER=Rag_project/documents
CHUNK_SIZE=1500
CHUNK_OVERLAP=150
TOP_K=5
```

Voir aussi [`.env.example`](.env.example) pour la liste complète.

---

## Ingestion — Azure AI Search (recommandé)

```bash
cd Rag_project
python ingest_azure.py
```

Ce script :

1. lit les documents du dossier `documents/` ;
2. nettoie et découpe les textes (chunks de 1500 caractères, overlap 150) ;
3. génère un embedding Azure OpenAI par chunk ;
4. crée l'index Search s'il n'existe pas ;
5. uploade les vecteurs dans Azure AI Search.

Exemple de sortie :

```text
INGESTION DES DOCUMENTS DANS AZURE AI SEARCH
Trouvé 9 fichiers à traiter
INGESTION TERMINÉE: 57 chunks indexés au total
```

---

## Ingestion — ChromaDB (option locale)

Pour un index vectoriel local sans Azure AI Search :

```bash
cd Rag_project
python ingest.py
```

Les données sont stockées dans `CHROMA_PATH` (défaut : `./db/chroma_store` à la racine du dépôt).

---

## Recherche documentaire

**Azure AI Search** (backend `single_agent`) :

```python
from retrieve_azure import retrieve
results = retrieve("politique de retour chaussures", top_k=5)
```

**ChromaDB** (local) :

```bash
python retrieve.py
```

Par défaut, `top_k = 5` passages récupérés.

---

## Pipeline RAG complet (avec LLM)

Le fichier `rag.py` enchaîne retrieval + génération de réponse :

```bash
python rag.py
```

Pour tester Azure Search avec plusieurs questions :

```bash
python rag_test.py
```

---

## Intégration avec `single_agent`

L'agent unique appelle `search_company_documents` qui délègue à `retrieve_azure.py`. Flux :

```text
single_agent.main
    → agent.py (Azure Responses API)
    → rag_tool.py → retrieve_azure.py → Azure AI Search
    → mcp_client.py → API FastAPI :8000
```

Voir [`single_agent/README.md`](../single_agent/README.md) pour le démarrage complet.

---

## Stratégie de chunking

Paramètres par défaut (`dev.env`) :

```text
CHUNK_SIZE = 1500
CHUNK_OVERLAP = 150
```

Ces valeurs conservent des passages métier complets tout en limitant le bruit dans le contexte injecté au LLM.

---

## Évaluation

Le fichier `emails_clients_test.csv` sert aux tests d'évaluation et **n'est pas indexé** dans la base RAG.

Métriques possibles : faithfulness, answer relevancy, context recall, context precision.

---

## Dépannage

| Problème | Action |
|---|---|
| RAG vide dans `single_agent` | Relancer `python ingest_azure.py`, vérifier `AZURE_SEARCH_*` |
| Erreur embedding | Vérifier `AZURE_OPENAI_EMBEDDING_MODEL` (nom du déploiement Azure) |
| Index introuvable | `ingest_azure.py` crée l'index automatiquement au premier lancement |
| Encodage console Windows | `$env:PYTHONIOENCODING="utf-8"` avant les scripts Python |

Guide détaillé : [`SETUP.md`](SETUP.md).

---

## Résumé

Ce projet fournit :

- l'ingestion documentaire vers **Azure AI Search** (production) ou **ChromaDB** (local) ;
- la recherche sémantique hybride pour alimenter l'agent `single_agent` ;
- un pipeline RAG autonome (`rag.py`) pour tests et démonstrations ;
- des réponses traçables avec citation des sources documentaires.
