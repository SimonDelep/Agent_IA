import sqlite3

from database import db


def get_by_id(conn: sqlite3.Connection, order_id: str):
    return db.get_order_by_id(conn, order_id)


def list_orders(
    conn: sqlite3.Connection,
    client_id: str | None,
    status: str | None,
    skip: int,
    limit: int,
):
    return db.list_orders(conn, client_id, status, skip, limit)


def update_status(conn: sqlite3.Connection, order_id: str, status: str):
    return db.update_order_status(conn, order_id, status)


def update_notes(conn: sqlite3.Connection, order_id: str, notes: str | None):
    return db.update_order_notes(conn, order_id, notes)


def append_notes(conn: sqlite3.Connection, order_id: str, extra: str):
    db.append_order_notes(conn, order_id, extra)


def has_product(conn: sqlite3.Connection, order_id: str, product_id: str) -> bool:
    return db.order_has_product(conn, order_id, product_id)


def get_item_line(conn: sqlite3.Connection, order_id: str, product_id: str):
    return db.get_order_item_line(conn, order_id, product_id)
