import sqlite3

from database import db


def get_by_id(conn: sqlite3.Connection, product_id: str):
    return db.get_product_by_id(conn, product_id)


def list_all(conn: sqlite3.Connection, skip: int, limit: int):
    return db.list_all_products(conn, skip, limit)


def search(
    conn: sqlite3.Connection,
    query: str | None,
    category: str | None,
    limit: int,
):
    return db.search_products(conn, query, category, limit)


def get_stock(conn: sqlite3.Connection, product_id: str):
    return db.get_product_stock(conn, product_id)
