"""
Create and seed the NordTrail Gear SQLite database (CAD).

Usage (from this directory):
    python seed_database.py

Recreates nordtrail.db from schema.sql and seeds/*.json|csv
"""

from __future__ import annotations

import csv
import json
import sqlite3
from pathlib import Path

DATABASE_DIR = Path(__file__).resolve().parent
DB_PATH = DATABASE_DIR / "nordtrail.db"
SCHEMA_PATH = DATABASE_DIR / "schema.sql"
SEEDS_DIR = DATABASE_DIR / "seeds"


def load_json(name: str) -> list | dict:
    path = SEEDS_DIR / name
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def apply_schema(conn: sqlite3.Connection) -> None:
    schema = SCHEMA_PATH.read_text(encoding="utf-8")
    conn.executescript(schema)


def clear_tables(conn: sqlite3.Connection) -> None:
    tables = [
        "returns",
        "order_items",
        "orders",
        "inventory",
        "coupons",
        "warehouses",
        "products",
        "clients",
    ]
    for table in tables:
        conn.execute(f"DELETE FROM {table}")


def seed_clients(conn: sqlite3.Connection) -> int:
    rows = load_json("clients.json")
    conn.executemany(
        """
        INSERT INTO clients (
            client_id, first_name, last_name, email, phone,
            province, country, loyalty_level, preferred_language,
            created_at, risk_flags, notes
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        [
            (
                r["client_id"],
                r["first_name"],
                r["last_name"],
                r["email"],
                r.get("phone"),
                r["province"],
                r["country"],
                r["loyalty_level"],
                r["preferred_language"],
                r["created_at"],
                json.dumps(r.get("risk_flags", []), ensure_ascii=False),
                r.get("notes"),
            )
            for r in rows
        ],
    )
    return len(rows)


def seed_products(conn: sqlite3.Connection) -> int:
    path = SEEDS_DIR / "products.csv"
    count = 0
    with path.open(encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    conn.executemany(
        """
        INSERT INTO products (
            product_id, name, category, price, currency,
            available_sizes, colors, warranty_months, weight_g,
            recommended_use, waterproof, return_eligible, is_active, notes
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1, ?)
        """,
        [
            (
                r["product_id"],
                r["name"],
                r["category"],
                float(r["price"]),
                r["currency"],
                r.get("available_sizes") or None,
                r.get("colors") or None,
                int(r["warranty_months"]),
                int(r["weight_g"]) if r.get("weight_g") else None,
                r.get("recommended_use") or None,
                r.get("waterproof") or None,
                int(r["return_eligible"]),
                r.get("notes") or None,
            )
            for r in rows
        ],
    )
    return len(rows)


def seed_warehouses(conn: sqlite3.Connection) -> int:
    rows = load_json("warehouses.json")
    conn.executemany(
        """
        INSERT INTO warehouses (warehouse_id, name, city, province, country, is_active)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        [
            (
                r["warehouse_id"],
                r["name"],
                r["city"],
                r["province"],
                r["country"],
                r["is_active"],
            )
            for r in rows
        ],
    )
    return len(rows)


def seed_inventory(conn: sqlite3.Connection) -> int:
    rows = load_json("inventory.json")
    conn.executemany(
        """
        INSERT INTO inventory (product_id, warehouse_id, quantity, reorder_threshold)
        VALUES (?, ?, ?, ?)
        """,
        [
            (
                r["product_id"],
                r["warehouse_id"],
                r["quantity"],
                r["reorder_threshold"],
            )
            for r in rows
        ],
    )
    return len(rows)


def seed_orders(conn: sqlite3.Connection) -> tuple[int, int]:
    rows = load_json("orders.json")
    order_count = 0
    item_count = 0
    for order in rows:
        conn.execute(
            """
            INSERT INTO orders (
                order_id, client_id, status, order_date, payment_status,
                shipping_province, shipping_method, tracking_number, delivery_date,
                subtotal_amount, shipping_amount, tax_amount, total_amount,
                currency, return_window_end, notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                order["order_id"],
                order["client_id"],
                order["status"],
                order["order_date"],
                order["payment_status"],
                order["shipping_province"],
                order["shipping_method"],
                order.get("tracking_number"),
                order.get("delivery_date"),
                order["subtotal_amount"],
                order["shipping_amount"],
                order["tax_amount"],
                order["total_amount"],
                order["currency"],
                order.get("return_window_end"),
                order.get("notes"),
            ),
        )
        order_count += 1
        for item in order["items"]:
            conn.execute(
                """
                INSERT INTO order_items (order_id, product_id, size, quantity, unit_price)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    order["order_id"],
                    item["product_id"],
                    item["size"],
                    item["quantity"],
                    item["unit_price"],
                ),
            )
            item_count += 1
    return order_count, item_count


def seed_coupons(conn: sqlite3.Connection) -> int:
    rows = load_json("coupons.json")
    conn.executemany(
        """
        INSERT INTO coupons (
            code, description, discount_percent, discount_fixed,
            min_order_amount, valid_from, valid_until,
            applies_to_sale, loyalty_required, is_active
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        [
            (
                r["code"],
                r.get("description"),
                r.get("discount_percent"),
                r.get("discount_fixed"),
                r["min_order_amount"],
                r["valid_from"],
                r["valid_until"],
                r["applies_to_sale"],
                r.get("loyalty_required"),
                r["is_active"],
            )
            for r in rows
        ],
    )
    return len(rows)


def seed_returns(conn: sqlite3.Connection) -> int:
    rows = load_json("returns.json")
    conn.executemany(
        """
        INSERT INTO returns (
            return_id, order_id, product_id, reason, status,
            requested_at, resolved_at, refund_amount, notes
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        [
            (
                r["return_id"],
                r["order_id"],
                r["product_id"],
                r["reason"],
                r["status"],
                r["requested_at"],
                r.get("resolved_at"),
                r.get("refund_amount"),
                r.get("notes"),
            )
            for r in rows
        ],
    )
    return len(rows)


def print_summary(conn: sqlite3.Connection) -> None:
    tables = [
        "clients",
        "products",
        "warehouses",
        "inventory",
        "orders",
        "order_items",
        "coupons",
        "returns",
    ]
    print(f"\nDatabase: {DB_PATH}")
    for table in tables:
        count = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        print(f"  {table}: {count} rows")


def main() -> None:
    if DB_PATH.exists():
        DB_PATH.unlink()

    conn = connect()
    try:
        apply_schema(conn)
        clear_tables(conn)

        clients = seed_clients(conn)
        products = seed_products(conn)
        warehouses = seed_warehouses(conn)
        inventory = seed_inventory(conn)
        orders, items = seed_orders(conn)
        coupons = seed_coupons(conn)
        returns = seed_returns(conn)

        conn.commit()
        print("NordTrail Gear database seeded successfully.")
        print(
            f"  clients={clients}, products={products}, warehouses={warehouses}, "
            f"inventory={inventory}, orders={orders}, order_items={items}, "
            f"coupons={coupons}, returns={returns}"
        )
        print_summary(conn)
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    main()
