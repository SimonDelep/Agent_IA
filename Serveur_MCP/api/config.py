import os
from pathlib import Path

SERVEUR_MCP_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DATABASE_PATH = SERVEUR_MCP_ROOT / "database" / "nordtrail.db"


def get_database_path() -> Path:
    return Path(os.getenv("NORDTRAIL_DB_PATH", str(DEFAULT_DATABASE_PATH)))
API_HOST = os.getenv("API_HOST", "127.0.0.1")
API_PORT = int(os.getenv("API_PORT", "8000"))
