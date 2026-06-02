import sqlite3
from datetime import date

from api.exceptions import NotFoundError
from api.repositories import clients as clients_repo
from api.repositories import coupons as coupons_repo


def list_coupons(conn: sqlite3.Connection, active_only: bool = False) -> list[dict]:
    return coupons_repo.list_all(conn, active_only)


def get_coupon(conn: sqlite3.Connection, code: str) -> dict:
    coupon = coupons_repo.get_by_code(conn, code)
    if not coupon:
        raise NotFoundError(f"Coupon « {code} » introuvable.")
    return coupon


def validate_coupon(
    conn: sqlite3.Connection, code: str, client_id: str, order_subtotal: float
) -> dict:
    coupon = coupons_repo.get_by_code(conn, code)
    if not coupon:
        raise NotFoundError(f"Coupon « {code} » introuvable.")

    today = date.today().isoformat()

    if not coupon.get("is_active"):
        return {
            "valid": False,
            "discount_amount": 0.0,
            "message": f"Le coupon « {code} » est inactif.",
            "code": code,
        }

    if today < coupon["valid_from"] or today > coupon["valid_until"]:
        return {
            "valid": False,
            "discount_amount": 0.0,
            "message": (
                f"Le coupon « {code} » n'est pas valide pour la date du jour "
                f"(période : {coupon['valid_from']} — {coupon['valid_until']})."
            ),
            "code": code,
        }

    if order_subtotal < coupon["min_order_amount"]:
        return {
            "valid": False,
            "discount_amount": 0.0,
            "message": (
                f"Montant minimum non atteint : {coupon['min_order_amount']} CAD requis, "
                f"sous-total fourni : {order_subtotal} CAD."
            ),
            "code": code,
        }

    loyalty_required = coupon.get("loyalty_required")
    if loyalty_required:
        client = clients_repo.get_by_id(conn, client_id)
        if not client:
            return {
                "valid": False,
                "discount_amount": 0.0,
                "message": f"Client {client_id} introuvable.",
                "code": code,
            }
        if client["loyalty_level"] != loyalty_required:
            return {
                "valid": False,
                "discount_amount": 0.0,
                "message": (
                    f"Le coupon « {code} » est réservé aux membres "
                    f"« {loyalty_required} » (client : {client['loyalty_level']})."
                ),
                "code": code,
            }

    discount = 0.0
    if coupon.get("discount_percent"):
        discount = round(order_subtotal * coupon["discount_percent"] / 100.0, 2)
    elif coupon.get("discount_fixed"):
        discount = float(coupon["discount_fixed"])

    discount = min(discount, order_subtotal)

    return {
        "valid": True,
        "discount_amount": discount,
        "message": f"Coupon « {code} » applicable. Rabais estimé : {discount} CAD.",
        "code": code,
    }
