# NordTrail Gear — Base de données SQLite

Base de données relationnelle simulant un entrepôt e-commerce pour **NordTrail Gear** (équipement trail et randonnée). Monnaie : **CAD**.

## Structure

```text
database/
├── schema.sql           # Schéma SQL (tables, index, contraintes)
├── seed_database.py     # Crée nordtrail.db et charge les seeds
├── db.py                # Accès SQLite pour futurs outils MCP
├── nordtrail.db         # Généré (ignoré par git)
├── seeds/               # Données sources versionnées
│   ├── products.csv
│   ├── clients.json
│   ├── warehouses.json
│   ├── inventory.json
│   ├── orders.json
│   ├── coupons.json
│   └── returns.json
├── DEMO_IDS.md          # Identifiants pour tests manuels
└── README.md
```

## Tables

| Table | Description |
|-------|-------------|
| `clients` | Clients (loyauté, province, drapeaux de risque) |
| `products` | Catalogue trail (15 SKU) |
| `warehouses` | Entrepôts MTL, Québec, Vancouver |
| `inventory` | Stock par produit et entrepôt |
| `orders` | Commandes avec taxes et livraison |
| `order_items` | Lignes de commande normalisées |
| `coupons` | Codes promo |
| `returns` | Demandes de retour |

## Initialisation

```bash
cd Serveur_MCP/database
python seed_database.py
```

Le script supprime `nordtrail.db` existant et le recrée.

## Exemple de requête

```bash
sqlite3 nordtrail.db "SELECT order_id, status, total_amount FROM orders WHERE client_id = 'CL-004';"
```

## Utilisation depuis Python

```python
from db import get_connection, get_order_by_id

with get_connection() as conn:
    order = get_order_by_id(conn, "NTG-2026-000201")
    print(order)
```

## API REST

Une API FastAPI expose ces données et les actions métier (annulation, retours, validation coupons).

```bash
cd Serveur_MCP
pip install -r requirements.txt
python database/seed_database.py
uvicorn api.main:app --reload --port 8000
```

Documentation : [api/README.md](../api/README.md)
