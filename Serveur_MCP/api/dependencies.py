from collections.abc import Generator
from typing import Annotated

import sqlite3
from fastapi import Depends

from api.config import get_database_path
from database.db import get_connection


def get_db() -> Generator[sqlite3.Connection, None, None]:
    conn = get_connection(get_database_path())
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


DbConn = Annotated[sqlite3.Connection, Depends(get_db)]
