import sqlite3

from database import db


def list_returns(
    conn: sqlite3.Connection,
    order_id: str | None,
    status: str | None,
    skip: int,
    limit: int,
):
    return db.list_returns(conn, order_id, status, skip, limit)


def get_by_id(conn: sqlite3.Connection, return_id: str):
    return db.get_return_by_id(conn, return_id)


def has_pending(conn: sqlite3.Connection, order_id: str, product_id: str) -> bool:
    return db.has_pending_return(conn, order_id, product_id)


def create(conn: sqlite3.Connection, data: dict):
    return db.create_return(conn, data)


def update(conn: sqlite3.Connection, return_id: str, data: dict):
    return db.update_return(conn, return_id, data)
