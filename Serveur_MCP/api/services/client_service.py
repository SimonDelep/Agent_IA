import sqlite3

from api.exceptions import BusinessRuleError, NotFoundError
from api.repositories import clients as clients_repo


def list_clients(conn: sqlite3.Connection, skip: int, limit: int) -> list[dict]:
    return clients_repo.list_clients(conn, skip, limit)


def get_client(conn: sqlite3.Connection, client_id: str) -> dict:
    client = clients_repo.get_by_id(conn, client_id)
    if not client:
        raise NotFoundError(f"Client {client_id} introuvable.")
    return client


def get_client_by_email(conn: sqlite3.Connection, email: str) -> dict:
    client = clients_repo.get_by_email(conn, email)
    if not client:
        raise NotFoundError(f"Aucun client avec l'email {email}.")
    return client


def create_client(conn: sqlite3.Connection, data: dict) -> dict:
    existing = clients_repo.get_by_email(conn, data["email"])
    if existing:
        raise BusinessRuleError(
            f"Un client existe déjà avec l'email {data['email']} ({existing['client_id']})."
        )
    return clients_repo.create(conn, data)


def update_client(conn: sqlite3.Connection, client_id: str, updates: dict) -> dict:
    if not clients_repo.get_by_id(conn, client_id):
        raise NotFoundError(f"Client {client_id} introuvable.")
    payload = {k: v for k, v in updates.items() if v is not None}
    if "email" in payload:
        other = clients_repo.get_by_email(conn, payload["email"])
        if other and other["client_id"] != client_id:
            raise BusinessRuleError(
                f"L'email {payload['email']} est déjà utilisé par {other['client_id']}."
            )
    result = clients_repo.update(conn, client_id, payload)
    if not result:
        raise NotFoundError(f"Client {client_id} introuvable.")
    return result


def delete_client(conn: sqlite3.Connection, client_id: str) -> None:
    if not clients_repo.get_by_id(conn, client_id):
        raise NotFoundError(f"Client {client_id} introuvable.")
    if clients_repo.count_orders(conn, client_id) > 0:
        raise BusinessRuleError(
            f"Suppression impossible : le client {client_id} a des commandes associées."
        )
    clients_repo.delete(conn, client_id)
