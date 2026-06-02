import sqlite3
from datetime import date

from api.exceptions import BusinessRuleError, NotFoundError
from api.repositories import clients as clients_repo
from api.repositories import orders as orders_repo
from api.repositories import products as products_repo
from api.repositories import returns as returns_repo

RETURNABLE_ORDER_STATUSES = {"livree", "expediee"}


def _check_return_window(order: dict) -> None:
    window_end = order.get("return_window_end")
    if not window_end:
        return
    today = date.today().isoformat()
    if today > window_end:
        raise BusinessRuleError(
            f"Fenêtre de retour expirée le {window_end}. "
            "La demande doit être refusée ou escaladée au service client."
        )


def _client_warning(conn: sqlite3.Connection, client_id: str) -> str | None:
    client = clients_repo.get_by_id(conn, client_id)
    if not client:
        return None
    flags = client.get("risk_flags") or []
    if "retours_repetes" in flags:
        return (
            "Attention : client avec historique de retours répétés (retours_repetes). "
            "Vérification manuelle recommandée."
        )
    return None


def list_returns(
    conn: sqlite3.Connection,
    order_id: str | None,
    status: str | None,
    skip: int,
    limit: int,
) -> list[dict]:
    return returns_repo.list_returns(conn, order_id, status, skip, limit)


def get_return(conn: sqlite3.Connection, return_id: str) -> dict:
    row = returns_repo.get_by_id(conn, return_id)
    if not row:
        raise NotFoundError(f"Retour {return_id} introuvable.")
    return row


def create_return(
    conn: sqlite3.Connection,
    order_id: str,
    product_id: str,
    reason: str,
    notes: str | None = None,
) -> dict:
    order = orders_repo.get_by_id(conn, order_id)
    if not order:
        raise NotFoundError(f"Commande {order_id} introuvable.")

    if order["status"] not in RETURNABLE_ORDER_STATUSES:
        raise BusinessRuleError(
            f"Retour impossible : commande au statut « {order['status']} ». "
            "Seules les commandes livrées ou expédiées acceptent une demande de retour."
        )

    _check_return_window(order)

    if not orders_repo.has_product(conn, order_id, product_id):
        raise BusinessRuleError(
            f"Le produit {product_id} ne fait pas partie de la commande {order_id}."
        )

    product = products_repo.get_by_id(conn, product_id)
    if not product:
        raise NotFoundError(f"Produit {product_id} introuvable.")
    if not product.get("return_eligible"):
        raise BusinessRuleError(
            f"Le produit {product_id} n'est pas éligible au retour selon le catalogue."
        )

    if returns_repo.has_pending(conn, order_id, product_id):
        raise BusinessRuleError(
            f"Une demande de retour en attente existe déjà pour "
            f"{order_id} / {product_id}."
        )

    created = returns_repo.create(
        conn,
        {
            "order_id": order_id,
            "product_id": product_id,
            "reason": reason,
            "notes": notes,
            "status": "pending",
        },
    )

    if order["status"] != "retour_demande":
        orders_repo.update_status(conn, order_id, "retour_demande")

    warning = _client_warning(conn, order["client_id"])
    if warning:
        created["warning"] = warning
    return created


def update_return(
    conn: sqlite3.Connection,
    return_id: str,
    status: str,
    refund_amount: float | None = None,
    notes: str | None = None,
) -> dict:
    existing = returns_repo.get_by_id(conn, return_id)
    if not existing:
        raise NotFoundError(f"Retour {return_id} introuvable.")

    current = existing["status"]
    if current != "pending":
        raise BusinessRuleError(
            f"Transition impossible : le retour est déjà au statut « {current} »."
        )

    updates: dict = {"status": status}
    today = date.today().isoformat()
    updates["resolved_at"] = today

    if status == "rejected":
        updates["refund_amount"] = 0.0
    elif status in ("approved", "refunded"):
        if refund_amount is not None:
            updates["refund_amount"] = refund_amount
        else:
            line = orders_repo.get_item_line(
                conn, existing["order_id"], existing["product_id"]
            )
            if line:
                updates["refund_amount"] = float(line["unit_price"]) * int(
                    line["quantity"]
                )
            else:
                updates["refund_amount"] = 0.0

    if notes is not None:
        updates["notes"] = notes

    updated = returns_repo.update(conn, return_id, updates)
    if not updated:
        raise NotFoundError(f"Retour {return_id} introuvable après mise à jour.")

    order = orders_repo.get_by_id(conn, existing["order_id"])
    if order and status == "refunded":
        orders_repo.update_status(conn, existing["order_id"], "retour_demande")

    warning = None
    if order:
        warning = _client_warning(conn, order["client_id"])
    if warning:
        updated["warning"] = warning
    return updated
