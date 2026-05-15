# Assistant RAG pour service client

Ce projet implémente la première partie de notre système d’assistant IA : un **RAG** (*Retrieval-Augmented Generation*) capable de répondre à des courriels clients en s’appuyant sur une base documentaire métier.

L’objectif est simple : permettre à l’assistant de chercher les bonnes informations dans les documents de l’entreprise avant de générer une réponse claire, fiable et sourcée.

---

## Contexte du projet

Notre entreprise fictive est une boutique en ligne spécialisée dans les produits outdoor : randonnée, trail, bivouac et équipement technique.

Le service client reçoit régulièrement des courriels concernant :

- les retours de produits ;
- les annulations de commande ;
- les garanties ;
- les délais de livraison ;
- les recommandations produits ;
- les problèmes de commande.

Le RAG permet à l’assistant de répondre à ces demandes en utilisant les documents internes de l’entreprise plutôt que de répondre uniquement avec les connaissances générales du modèle.

---

## Ce que fait le système RAG

Le système suit le fonctionnement suivant :

```text
Question ou courriel client
        ↓
Recherche dans la base documentaire
        ↓
Récupération des passages les plus pertinents
        ↓
Injection de ces passages dans le prompt
        ↓
Génération d’une réponse contextualisée
        ↓
Retour de la réponse avec les sources utilisées
```

Le modèle ne répond donc pas “dans le vide”.  
Il s’appuie sur les documents indexés dans la base vectorielle.

---

## Documents utilisés

La base documentaire contient plusieurs types de documents métier :

```text
documents/
├── politique_retours.md
├── politique_garantie.md
├── faq_livraison.md
├── conditions_annulation.md
├── guide_tailles.md
├── procedure_sav_interne.md
├── catalogue_produits.csv
└── commandes_exemples.json
```

Ces documents permettent de tester plusieurs cas réalistes :

- retour d’un produit déjà utilisé ;
- demande d’annulation ;
- produit encore sous garantie ;
- commande en retard ;
- choix d’un produit selon un besoin client ;
- question sur les délais ou frais de livraison.

---

## Structure du projet

```text
projet-rag/
├── .env
├── config.py
├── utils.py
├── embeddings.py
├── vectorstore.py
├── ingest.py
├── retrieve.py
├── rag.py
├── documents/
├── chroma_db/
└── README.md
```

### Rôle des fichiers

| Fichier | Rôle |
|---|---|
| `config.py` | Regroupe les paramètres principaux du projet |
| `utils.py` | Charge, nettoie et découpe les documents |
| `embeddings.py` | Génère les embeddings des textes |
| `vectorstore.py` | Gère la base vectorielle ChromaDB |
| `ingest.py` | Indexe les documents dans ChromaDB |
| `retrieve.py` | Recherche les passages pertinents |
| `rag.py` | Lance le pipeline RAG complet |

---

## Installation

Créer un environnement virtuel :

```bash
python -m venv .venv
```

Activer l’environnement :

```bash
# Windows
.venv\Scripts\activate
```

```bash
# Linux / macOS
source .venv/bin/activate
```

Installer les dépendances :

```bash
pip install openai chromadb pypdf python-dotenv
```

---

## Configuration

Créer un fichier `.env` à la racine du projet.

### Option avec OpenAI

```env
OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL=gpt-4o-mini
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
```

### Option avec Azure OpenAI

```env
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com
AZURE_OPENAI_API_KEY=your_api_key_here
AZURE_OPENAI_DEPLOYMENT=your_deployment_name
AZURE_OPENAI_EMBEDDING_DEPLOYMENT=your_embedding_deployment_name
```

Les clés API ne doivent jamais être écrites directement dans le code.

---

## Ingestion des documents

Avant de poser des questions au RAG, il faut indexer les documents.

```bash
python ingest.py
```

Ce script :

1. lit les documents du dossier `documents/` ;
2. nettoie leur contenu ;
3. découpe les textes en morceaux ;
4. génère un embedding pour chaque morceau ;
5. stocke les résultats dans ChromaDB.

La base vectorielle est sauvegardée localement dans le dossier :

```text
chroma_db/
```

---

## Stratégie de chunking

Les documents sont découpés en morceaux de taille moyenne afin de garder assez de contexte sans créer des blocs trop longs.

Paramètres utilisés :

```text
chunk_size = 500
overlap = 50
```

Ce choix permet :

- de garder des passages assez complets ;
- d’éviter de couper une règle métier importante ;
- d’améliorer les chances de récupérer le bon contexte ;
- de limiter le bruit dans le prompt final.

L’overlap permet de conserver une continuité entre deux chunks voisins.

---

## Recherche documentaire

La recherche sémantique se fait avec ChromaDB.

Exemple :

```bash
python retrieve.py
```

Le système transforme la question en embedding, puis récupère les passages les plus proches dans la base vectorielle.

Par défaut, on récupère les 5 passages les plus pertinents :

```text
top_k = 5
```

Un `top_k` trop faible peut manquer des informations importantes.  
Un `top_k` trop élevé peut ajouter du bruit dans le contexte.

---

## Génération de réponse

Le fichier `rag.py` lance le pipeline complet.

Exemple :

```bash
python rag.py
```

Le système :

1. reçoit une question ou un courriel client ;
2. récupère les passages utiles ;
3. construit un prompt avec le contexte ;
4. génère une réponse ;
5. retourne aussi les sources utilisées.

Exemple de question :

```text
Bonjour, j’ai acheté des chaussures de trail il y a 22 jours.
Je les ai utilisées une fois dehors, mais elles me font mal.
Puis-je les retourner ?
```

Exemple de réponse attendue :

```text
Le retour est encore dans le délai de 30 jours. Cependant, la politique de retour indique que les chaussures utilisées en extérieur ne sont pas automatiquement remboursables si elles présentent des traces d’usage. Le client peut contacter le service client pour une étude exceptionnelle, mais le remboursement n’est pas garanti.

Sources utilisées :
- politique_retours.md
```

---

## Pourquoi utiliser un RAG ?

Un RAG est adapté à ce projet parce que les réponses du service client dépendent de documents métier précis.

Sans RAG, le modèle pourrait inventer une règle ou répondre de manière trop générale.

Avec le RAG, l’assistant peut :

- utiliser les politiques internes ;
- citer les sources ;
- s’adapter si les documents changent ;
- limiter les hallucinations ;
- préparer l’évolution vers un agent capable d’agir.

---

## Évaluation

Le système peut être évalué avec un jeu de questions-réponses préparé à l’avance.

Exemple de fichier :

```text
evaluation/questions_test.csv
```

Chaque ligne contient :

| Champ | Description |
|---|---|
| `question` | Question ou courriel client |
| `expected_answer` | Réponse attendue |
| `expected_sources` | Documents qui devraient être retrouvés |

Métriques possibles :

| Métrique | Objectif |
|---|---|
| `faithfulness` | Vérifier que la réponse est bien fondée sur les documents |
| `answer_relevancy` | Vérifier que la réponse répond à la question |
| `context_recall` | Vérifier que les bons documents sont récupérés |
| `context_precision` | Vérifier que les documents récupérés sont pertinents |

L’objectif n’est pas seulement d’avoir une réponse fluide.  
L’objectif est d’avoir une réponse correcte, justifiée et traçable.

---

## Limites actuelles

Cette première version reste volontairement simple.

Limites identifiées :

- le chunking est encore basique ;
- la recherche est uniquement vectorielle ;
- il n’y a pas encore de reranking ;
- les tableaux sont traités simplement ;
- le système ne peut pas encore modifier une commande ;
- les appels d’outils seront ajoutés dans la phase suivante.

Ces limites sont normales pour une première version RAG.

---

## Prochaine étape

La prochaine phase consistera à transformer ce RAG en **agent LLM unique connecté à des outils**.

L’agent devra pouvoir :

- lire un courriel client ;
- identifier l’intention ;
- extraire les informations importantes ;
- utiliser le RAG pour consulter les règles ;
- appeler une API simulée ;
- produire une réponse finale fiable.

Exemples d’outils futurs :

```text
get_order_status(order_id)
cancel_order(order_id)
create_return_request(order_id)
check_warranty(product_id)
search_product_catalog(criteria)
```

Le RAG devient donc la base de connaissance de l’agent.

---

## Résumé

Cette partie du projet construit un système RAG simple, lisible et fonctionnel.

Il permet :

- d’ingérer des documents métier ;
- de créer une base vectorielle ;
- de récupérer les passages pertinents ;
- de générer des réponses contextualisées ;
- de citer les sources utilisées ;
- de préparer l’évolution vers un agent plus complet.

Ce projet sert de fondation pour les prochaines étapes : agent avec outils, puis orchestration multi-agents.
