import sqlite3

from database import db


def list_warehouses(conn: sqlite3.Connection):
    return db.list_warehouses(conn)


def list_inventory(
    conn: sqlite3.Connection,
    product_id: str | None,
    warehouse_id: str | None,
):
    return db.list_inventory(conn, product_id, warehouse_id)
