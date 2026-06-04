"""Pytest fixtures — isolated seeded database per test."""

from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

SERVEUR_MCP_ROOT = Path(__file__).resolve().parents[1]
if str(SERVEUR_MCP_ROOT) not in sys.path:
    sys.path.insert(0, str(SERVEUR_MCP_ROOT))

TEST_DB_PATH = SERVEUR_MCP_ROOT / "database" / "nordtrail_test.db"


def _reseed_database() -> None:
    import database.seed_database as seed_module

    seed_module.DB_PATH = TEST_DB_PATH
    if TEST_DB_PATH.exists():
        TEST_DB_PATH.unlink()
    seed_module.main()


@pytest.fixture(scope="session", autouse=True)
def _setup_test_database() -> None:
    os.environ["NORDTRAIL_DB_PATH"] = str(TEST_DB_PATH)
    _reseed_database()
    yield
    if TEST_DB_PATH.exists():
        try:
            TEST_DB_PATH.unlink()
        except OSError:
            pass


@pytest.fixture
def client() -> TestClient:
    _reseed_database()
    from api.main import app

    with TestClient(app) as test_client:
        yield test_client
