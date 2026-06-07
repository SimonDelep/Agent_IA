# Serveur MCP — NordTrail Gear

Expose les opérations service client via le protocole MCP (stdio). Chaque outil appelle l'**API FastAPI** locale.

## Prérequis

1. Base initialisée : `python database/seed_database.py`
2. **API démarrée** (obligatoire avant Cursor) :

```bash
cd Serveur_MCP
uvicorn api.main:app --reload --port 8000
```

3. Dépendances : `pip install -r requirements.txt` (inclut `mcp` et `httpx`)

## Lancer le serveur MCP (test manuel)

```bash
cd Serveur_MCP
python -m mcp_server.server
```

## Configuration Cursor

Ajoutez dans `.cursor/mcp.json` à la racine du projet (ajustez les chemins) :

```json
{
  "mcpServers": {
    "nordtrail-gear": {
      "command": "python",
      "args": ["-m", "mcp_server.server"],
      "cwd": "C:/Users/marin/Desktop/Marin/Etudes/UQAC/Semestre_ete/llm_cloud/Agent_IA/Serveur_MCP",
      "env": {
        "NORDTRAIL_API_URL": "http://127.0.0.1:8000"
      }
    }
  }
}
```

Redémarrez Cursor après modification. Vérifiez que l'API tourne sur le port configuré.

## Variables d'environnement

| Variable | Défaut | Description |
|----------|--------|-------------|
| `NORDTRAIL_API_URL` | `http://127.0.0.1:8000` | URL de base de l'API |
| `NORDTRAIL_API_TIMEOUT` | `30` | Timeout HTTP (secondes) |

## Outils exposés

| Outil | Action API |
|-------|------------|
| `check_api_health` | GET /health |
| `get_order_status` | GET /orders/{id} |
| `list_client_orders` | GET /orders?client_id= |
| `cancel_order` | POST /orders/{id}/cancel |
| `get_client_by_email` | GET /clients/by-email |
| `get_client` | GET /clients/{id} |
| `search_products` | GET /products?search= |
| `get_product` | GET /products/{id} |
| `get_product_stock` | GET /products/{id}/stock |
| `create_return_request` | POST /returns |
| `get_return` | GET /returns/{id} |
| `list_returns` | GET /returns |
| `update_return_status` | PATCH /returns/{id} |
| `validate_coupon` | POST /coupons/validate |

Scénarios de test : [database/DEMO_IDS.md](../database/DEMO_IDS.md).

## Architecture

```text
Cursor / Agent / single_agent  --stdio-->  mcp_server/server.py  --HTTP-->  api (FastAPI)  -->  SQLite
```

L'agent Python [`single_agent/`](../single_agent/) utilise ce serveur MCP en subprocess stdio et combine les outils avec un RAG Azure AI Search.

Les erreurs API (404, 409) sont renvoyées au modèle en JSON avec `error: true` et `detail` en français.
