# NordTrail Gear — API REST (FastAPI)

API service client pour commandes, retours, catalogue et coupons. S'appuie sur SQLite (`database/nordtrail.db`).

## Prérequis

```bash
cd Serveur_MCP
pip install -r requirements.txt
python database/seed_database.py
```

## Lancement

```bash
cd Serveur_MCP
uvicorn api.main:app --reload --port 8001
```

- Documentation interactive : http://127.0.0.1:8001/docs
- Santé : http://127.0.0.1:8001/health

> **Port 8001** par défaut dans `dev.env.example` et les configs agent/MCP — évite le conflit avec ChromaDB qui utilise souvent le port 8000. Le port doit correspondre à `NORDTRAIL_API_URL`.

Variables optionnelles :

| Variable | Défaut | Description |
|----------|--------|-------------|
| `NORDTRAIL_DB_PATH` | `database/nordtrail.db` | Chemin vers la base SQLite |
| `API_PORT` | `8001` | Port lu par `api/config.py` si vous utilisez un lanceur custom |

## Endpoints principaux

| Ressource | Routes |
|-----------|--------|
| Clients | `GET/POST /clients`, `GET /clients/by-email`, `GET/PATCH/DELETE /clients/{id}` |
| Commandes | `GET /orders`, `GET /orders/{id}`, `POST /orders/{id}/cancel`, `PATCH /orders/{id}` (notes) |
| Produits | `GET /products`, `GET /products/{id}`, `GET /products/{id}/stock` |
| Inventaire | `GET /warehouses`, `GET /inventory` |
| Retours | `GET/POST /returns`, `GET/PATCH /returns/{id}` |
| Coupons | `GET /coupons`, `GET /coupons/{code}`, `POST /coupons/validate` |

Identifiants de test : voir [database/DEMO_IDS.md](../database/DEMO_IDS.md).

## Tests

```bash
cd Serveur_MCP
pytest
```

## Architecture

```text
routers/  →  services/ (règles métier)  →  repositories/  →  database/db.py
```

Les erreurs métier renvoient HTTP **409** avec `{"detail": "..."}` en français.

## Serveur MCP

Voir [mcp_server/README.md](../mcp_server/README.md) — outils Cursor, [`single_agent`](../../single_agent/) et [`multi_agent`](../../multi_agent/) appelant cette API via HTTP.
