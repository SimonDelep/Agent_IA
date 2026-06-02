import sqlite3

from database import db


def list_clients(conn: sqlite3.Connection, skip: int, limit: int):
    return db.list_clients(conn, skip, limit)


def get_by_id(conn: sqlite3.Connection, client_id: str):
    return db.get_client_by_id(conn, client_id)


def get_by_email(conn: sqlite3.Connection, email: str):
    return db.get_client_by_email(conn, email)


def count_orders(conn: sqlite3.Connection, client_id: str) -> int:
    return db.count_client_orders(conn, client_id)


def create(conn: sqlite3.Connection, data: dict):
    return db.create_client(conn, data)


def update(conn: sqlite3.Connection, client_id: str, data: dict):
    return db.update_client(conn, client_id, data)


def delete(conn: sqlite3.Connection, client_id: str) -> bool:
    return db.delete_client(conn, client_id)
