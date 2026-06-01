"""
Thin SQLite access layer for NordTrail Gear MCP tools.
"""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

DATABASE_DIR = Path(__file__).resolve().parent
DEFAULT_DB_PATH = DATABASE_DIR / "nordtrail.db"


def get_connection(db_path: Path | None = None) -> sqlite3.Connection:
    path = db_path or DEFAULT_DB_PATH
    if not path.exists():
        raise FileNotFoundError(
            f"Database not found: {path}. Run: python seed_database.py"
        )
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def row_to_dict(row: sqlite3.Row | None) -> dict[str, Any] | None:
    if row is None:
        return None
    return dict(row)


def rows_to_dicts(rows: list[sqlite3.Row]) -> list[dict[str, Any]]:
    return [dict(r) for r in rows]


def parse_client_row(row: sqlite3.Row) -> dict[str, Any]:
    data = dict(row)
    data["risk_flags"] = json.loads(data.get("risk_flags") or "[]")
    return data


def get_order_by_id(conn: sqlite3.Connection, order_id: str) -> dict[str, Any] | None:
    order = conn.execute(
        "SELECT * FROM orders WHERE order_id = ?", (order_id,)
    ).fetchone()
    if not order:
        return None
    result = dict(order)
    result["items"] = rows_to_dicts(
        conn.execute(
            """
            SELECT oi.*, p.name AS product_name, p.category
            FROM order_items oi
            JOIN products p ON p.product_id = oi.product_id
            WHERE oi.order_id = ?
            """,
            (order_id,),
        ).fetchall()
    )
    client = conn.execute(
        "SELECT * FROM clients WHERE client_id = ?", (result["client_id"],)
    ).fetchone()
    result["client"] = parse_client_row(client) if client else None
    return result


def get_client_by_email(conn: sqlite3.Connection, email: str) -> dict[str, Any] | None:
    row = conn.execute(
        "SELECT * FROM clients WHERE lower(email) = lower(?)", (email,)
    ).fetchone()
    return parse_client_row(row) if row else None


def get_product_stock(
    conn: sqlite3.Connection, product_id: str
) -> list[dict[str, Any]]:
    return rows_to_dicts(
        conn.execute(
            """
            SELECT i.*, w.name AS warehouse_name, w.city, w.province
            FROM inventory i
            JOIN warehouses w ON w.warehouse_id = i.warehouse_id
            WHERE i.product_id = ?
            ORDER BY w.warehouse_id
            """,
            (product_id,),
        ).fetchall()
    )


def search_products(
    conn: sqlite3.Connection, query: str, category: str | None = None, limit: int = 10
) -> list[dict[str, Any]]:
    pattern = f"%{query}%"
    sql = """
        SELECT * FROM products
        WHERE is_active = 1
          AND (name LIKE ? OR product_id LIKE ? OR category LIKE ?)
    """
    params: list[Any] = [pattern, pattern, pattern]
    if category:
        sql += " AND category = ?"
        params.append(category)
    sql += " ORDER BY name LIMIT ?"
    params.append(limit)
    return rows_to_dicts(conn.execute(sql, params).fetchall())
