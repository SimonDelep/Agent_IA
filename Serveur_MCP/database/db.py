"""
Thin SQLite access layer for NordTrail Gear MCP tools and API.
"""

from __future__ import annotations

import json
import re
import sqlite3
from datetime import date
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


# --- Clients ---


def list_clients(
    conn: sqlite3.Connection, skip: int = 0, limit: int = 50
) -> list[dict[str, Any]]:
    rows = conn.execute(
        "SELECT * FROM clients ORDER BY client_id LIMIT ? OFFSET ?",
        (limit, skip),
    ).fetchall()
    return [parse_client_row(r) for r in rows]


def get_client_by_id(conn: sqlite3.Connection, client_id: str) -> dict[str, Any] | None:
    row = conn.execute(
        "SELECT * FROM clients WHERE client_id = ?", (client_id,)
    ).fetchone()
    return parse_client_row(row) if row else None


def get_client_by_email(conn: sqlite3.Connection, email: str) -> dict[str, Any] | None:
    row = conn.execute(
        "SELECT * FROM clients WHERE lower(email) = lower(?)", (email,)
    ).fetchone()
    return parse_client_row(row) if row else None


def count_client_orders(conn: sqlite3.Connection, client_id: str) -> int:
    row = conn.execute(
        "SELECT COUNT(*) AS c FROM orders WHERE client_id = ?", (client_id,)
    ).fetchone()
    return int(row["c"]) if row else 0


def generate_client_id(conn: sqlite3.Connection) -> str:
    rows = conn.execute(
        "SELECT client_id FROM clients WHERE client_id LIKE 'CL-%'"
    ).fetchall()
    max_num = 0
    for row in rows:
        match = re.match(r"CL-(\d+)$", row["client_id"])
        if match:
            max_num = max(max_num, int(match.group(1)))
    return f"CL-{max_num + 1:03d}"


def create_client(conn: sqlite3.Connection, data: dict[str, Any]) -> dict[str, Any]:
    client_id = data.get("client_id") or generate_client_id(conn)
    conn.execute(
        """
        INSERT INTO clients (
            client_id, first_name, last_name, email, phone,
            province, country, loyalty_level, preferred_language,
            created_at, risk_flags, notes
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            client_id,
            data["first_name"],
            data["last_name"],
            data["email"],
            data.get("phone"),
            data["province"],
            data.get("country", "CA"),
            data["loyalty_level"],
            data.get("preferred_language", "fr"),
            data.get("created_at", date.today().isoformat()),
            json.dumps(data.get("risk_flags", []), ensure_ascii=False),
            data.get("notes"),
        ),
    )
    return get_client_by_id(conn, client_id)  # type: ignore[return-value]


def update_client(
    conn: sqlite3.Connection, client_id: str, updates: dict[str, Any]
) -> dict[str, Any] | None:
    allowed = {
        "first_name",
        "last_name",
        "email",
        "phone",
        "province",
        "country",
        "loyalty_level",
        "preferred_language",
        "notes",
        "risk_flags",
    }
    fields = {k: v for k, v in updates.items() if k in allowed and v is not None}
    if not fields:
        return get_client_by_id(conn, client_id)
    if "risk_flags" in fields:
        fields["risk_flags"] = json.dumps(fields["risk_flags"], ensure_ascii=False)
    set_clause = ", ".join(f"{k} = ?" for k in fields)
    values = list(fields.values()) + [client_id]
    conn.execute(f"UPDATE clients SET {set_clause} WHERE client_id = ?", values)
    return get_client_by_id(conn, client_id)


def delete_client(conn: sqlite3.Connection, client_id: str) -> bool:
    cur = conn.execute("DELETE FROM clients WHERE client_id = ?", (client_id,))
    return cur.rowcount > 0


# --- Orders ---


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


def list_orders(
    conn: sqlite3.Connection,
    client_id: str | None = None,
    status: str | None = None,
    skip: int = 0,
    limit: int = 50,
) -> list[dict[str, Any]]:
    sql = "SELECT * FROM orders WHERE 1=1"
    params: list[Any] = []
    if client_id:
        sql += " AND client_id = ?"
        params.append(client_id)
    if status:
        sql += " AND status = ?"
        params.append(status)
    sql += " ORDER BY order_date DESC LIMIT ? OFFSET ?"
    params.extend([limit, skip])
    return rows_to_dicts(conn.execute(sql, params).fetchall())


def update_order_status(
    conn: sqlite3.Connection, order_id: str, status: str
) -> dict[str, Any] | None:
    conn.execute(
        "UPDATE orders SET status = ? WHERE order_id = ?", (status, order_id)
    )
    row = conn.execute("SELECT * FROM orders WHERE order_id = ?", (order_id,)).fetchone()
    return dict(row) if row else None


def update_order_notes(
    conn: sqlite3.Connection, order_id: str, notes: str | None
) -> dict[str, Any] | None:
    conn.execute(
        "UPDATE orders SET notes = ? WHERE order_id = ?", (notes, order_id)
    )
    row = conn.execute("SELECT * FROM orders WHERE order_id = ?", (order_id,)).fetchone()
    return dict(row) if row else None


def append_order_notes(
    conn: sqlite3.Connection, order_id: str, extra: str
) -> None:
    row = conn.execute(
        "SELECT notes FROM orders WHERE order_id = ?", (order_id,)
    ).fetchone()
    if not row:
        return
    current = row["notes"] or ""
    new_notes = f"{current}\n{extra}".strip() if current else extra
    conn.execute(
        "UPDATE orders SET notes = ? WHERE order_id = ?", (new_notes, order_id)
    )


def order_has_product(
    conn: sqlite3.Connection, order_id: str, product_id: str
) -> bool:
    row = conn.execute(
        """
        SELECT 1 FROM order_items
        WHERE order_id = ? AND product_id = ?
        """,
        (order_id, product_id),
    ).fetchone()
    return row is not None


def get_order_item_line(
    conn: sqlite3.Connection, order_id: str, product_id: str
) -> dict[str, Any] | None:
    row = conn.execute(
        """
        SELECT * FROM order_items
        WHERE order_id = ? AND product_id = ?
        LIMIT 1
        """,
        (order_id, product_id),
    ).fetchone()
    return dict(row) if row else None


# --- Products ---


def get_product_by_id(conn: sqlite3.Connection, product_id: str) -> dict[str, Any] | None:
    row = conn.execute(
        "SELECT * FROM products WHERE product_id = ?", (product_id,)
    ).fetchone()
    return dict(row) if row else None


def list_all_products(
    conn: sqlite3.Connection, skip: int = 0, limit: int = 100
) -> list[dict[str, Any]]:
    return rows_to_dicts(
        conn.execute(
            "SELECT * FROM products WHERE is_active = 1 ORDER BY name LIMIT ? OFFSET ?",
            (limit, skip),
        ).fetchall()
    )


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
    conn: sqlite3.Connection,
    query: str | None = None,
    category: str | None = None,
    limit: int = 10,
) -> list[dict[str, Any]]:
    if query:
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
    sql = "SELECT * FROM products WHERE is_active = 1"
    params = []
    if category:
        sql += " AND category = ?"
        params.append(category)
    sql += " ORDER BY name LIMIT ?"
    params.append(limit)
    return rows_to_dicts(conn.execute(sql, params).fetchall())


# --- Warehouses & inventory ---


def list_warehouses(conn: sqlite3.Connection) -> list[dict[str, Any]]:
    return rows_to_dicts(
        conn.execute(
            "SELECT * FROM warehouses WHERE is_active = 1 ORDER BY warehouse_id"
        ).fetchall()
    )


def list_inventory(
    conn: sqlite3.Connection,
    product_id: str | None = None,
    warehouse_id: str | None = None,
) -> list[dict[str, Any]]:
    sql = """
        SELECT i.*, w.name AS warehouse_name, w.city, w.province,
               p.name AS product_name
        FROM inventory i
        JOIN warehouses w ON w.warehouse_id = i.warehouse_id
        JOIN products p ON p.product_id = i.product_id
        WHERE 1=1
    """
    params: list[Any] = []
    if product_id:
        sql += " AND i.product_id = ?"
        params.append(product_id)
    if warehouse_id:
        sql += " AND i.warehouse_id = ?"
        params.append(warehouse_id)
    sql += " ORDER BY i.product_id, i.warehouse_id"
    return rows_to_dicts(conn.execute(sql, params).fetchall())


# --- Returns ---


def list_returns(
    conn: sqlite3.Connection,
    order_id: str | None = None,
    status: str | None = None,
    skip: int = 0,
    limit: int = 50,
) -> list[dict[str, Any]]:
    sql = "SELECT * FROM returns WHERE 1=1"
    params: list[Any] = []
    if order_id:
        sql += " AND order_id = ?"
        params.append(order_id)
    if status:
        sql += " AND status = ?"
        params.append(status)
    sql += " ORDER BY requested_at DESC LIMIT ? OFFSET ?"
    params.extend([limit, skip])
    return rows_to_dicts(conn.execute(sql, params).fetchall())


def get_return_by_id(conn: sqlite3.Connection, return_id: str) -> dict[str, Any] | None:
    row = conn.execute(
        "SELECT * FROM returns WHERE return_id = ?", (return_id,)
    ).fetchone()
    return dict(row) if row else None


def has_pending_return(
    conn: sqlite3.Connection, order_id: str, product_id: str
) -> bool:
    row = conn.execute(
        """
        SELECT 1 FROM returns
        WHERE order_id = ? AND product_id = ? AND status = 'pending'
        """,
        (order_id, product_id),
    ).fetchone()
    return row is not None


def generate_return_id(conn: sqlite3.Connection) -> str:
    year = date.today().year
    rows = conn.execute(
        "SELECT return_id FROM returns WHERE return_id LIKE ?",
        (f"RET-{year}-%",),
    ).fetchall()
    max_seq = 0
    for row in rows:
        match = re.match(rf"RET-{year}-(\d+)$", row["return_id"])
        if match:
            max_seq = max(max_seq, int(match.group(1)))
    return f"RET-{year}-{max_seq + 1:03d}"


def create_return(conn: sqlite3.Connection, data: dict[str, Any]) -> dict[str, Any]:
    return_id = data.get("return_id") or generate_return_id(conn)
    conn.execute(
        """
        INSERT INTO returns (
            return_id, order_id, product_id, reason, status,
            requested_at, resolved_at, refund_amount, notes
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            return_id,
            data["order_id"],
            data["product_id"],
            data["reason"],
            data.get("status", "pending"),
            data.get("requested_at", date.today().isoformat()),
            data.get("resolved_at"),
            data.get("refund_amount"),
            data.get("notes"),
        ),
    )
    return get_return_by_id(conn, return_id)  # type: ignore[return-value]


def update_return(
    conn: sqlite3.Connection, return_id: str, updates: dict[str, Any]
) -> dict[str, Any] | None:
    allowed = {"status", "resolved_at", "refund_amount", "notes", "reason"}
    fields = {k: v for k, v in updates.items() if k in allowed and v is not None}
    if not fields:
        return get_return_by_id(conn, return_id)
    set_clause = ", ".join(f"{k} = ?" for k in fields)
    values = list(fields.values()) + [return_id]
    conn.execute(f"UPDATE returns SET {set_clause} WHERE return_id = ?", values)
    return get_return_by_id(conn, return_id)


# --- Coupons ---


def list_coupons(
    conn: sqlite3.Connection, active_only: bool = False
) -> list[dict[str, Any]]:
    if active_only:
        return rows_to_dicts(
            conn.execute(
                "SELECT * FROM coupons WHERE is_active = 1 ORDER BY code"
            ).fetchall()
        )
    return rows_to_dicts(
        conn.execute("SELECT * FROM coupons ORDER BY code").fetchall()
    )


def get_coupon_by_code(conn: sqlite3.Connection, code: str) -> dict[str, Any] | None:
    row = conn.execute(
        "SELECT * FROM coupons WHERE upper(code) = upper(?)", (code,)
    ).fetchone()
    return dict(row) if row else None
