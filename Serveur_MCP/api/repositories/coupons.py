import sqlite3

from database import db


def list_all(conn: sqlite3.Connection, active_only: bool = False):
    return db.list_coupons(conn, active_only)


def get_by_code(conn: sqlite3.Connection, code: str):
    return db.get_coupon_by_code(conn, code)
