import sqlite3

from api.exceptions import BusinessRuleError, NotFoundError
from api.repositories import orders as orders_repo

CANCELLABLE_STATUSES = {"en_attente", "en_preparation"}


def get_order(conn: sqlite3.Connection, order_id: str) -> dict:
    order = orders_repo.get_by_id(conn, order_id)
    if not order:
        raise NotFoundError(f"Commande {order_id} introuvable.")
    return order


def list_orders(
    conn: sqlite3.Connection,
    client_id: str | None,
    status: str | None,
    skip: int,
    limit: int,
) -> list[dict]:
    return orders_repo.list_orders(conn, client_id, status, skip, limit)


def cancel_order(
    conn: sqlite3.Connection, order_id: str, reason: str | None = None
) -> dict:
    order = orders_repo.get_by_id(conn, order_id)
    if not order:
        raise NotFoundError(f"Commande {order_id} introuvable.")

    status = order["status"]
    if status == "annulee":
        raise BusinessRuleError("Cette commande est déjà annulée.")
    if status not in CANCELLABLE_STATUSES:
        raise BusinessRuleError(
            f"Annulation impossible : la commande est au statut « {status} ». "
            "Seules les commandes en attente ou en préparation peuvent être annulées."
        )

    orders_repo.update_status(conn, order_id, "annulee")
    note_parts = ["[Annulation API]"]
    if reason:
        note_parts.append(reason)
    if order.get("payment_status") == "en_attente":
        note_parts.append("Paiement non capturé — aucun remboursement requis.")
    orders_repo.append_notes(conn, order_id, " ".join(note_parts))

    result = orders_repo.get_by_id(conn, order_id)
    if not result:
        raise NotFoundError(f"Commande {order_id} introuvable après mise à jour.")
    return result


def update_order_notes(
    conn: sqlite3.Connection, order_id: str, notes: str | None
) -> dict:
    order = orders_repo.get_by_id(conn, order_id)
    if not order:
        raise NotFoundError(f"Commande {order_id} introuvable.")
    updated = orders_repo.update_notes(conn, order_id, notes)
    if not updated:
        raise NotFoundError(f"Commande {order_id} introuvable.")
    return orders_repo.get_by_id(conn, order_id)  # type: ignore[return-value]
