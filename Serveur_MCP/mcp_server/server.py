"""
Serveur MCP NordTrail Gear (stdio).

Prérequis : API FastAPI démarrée sur NORDTRAIL_API_URL (défaut http://127.0.0.1:8000).

Usage (depuis Serveur_MCP):
    python -m mcp_server.server
"""

from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from mcp.server.fastmcp import FastMCP

from mcp_server import api_client

mcp = FastMCP(
    "nordtrail-gear",
    instructions=(
        "Outils service client NordTrail Gear (e-commerce trail, CAD). "
        "Utilisez get_order_status et get_client_by_email pour identifier une demande, "
        "puis create_return_request ou cancel_order selon le cas. "
        "Validez les coupons avec validate_coupon."
    ),
)


@mcp.tool()
def check_api_health() -> str:
    """Vérifie que l'API NordTrail Gear répond (GET /health)."""
    return api_client.request("GET", "/health")


@mcp.tool()
def get_order_status(order_id: str) -> str:
    """
    Récupère le statut d'une commande, ses articles, le client et le suivi.

    Args:
        order_id: Identifiant commande, ex. NTG-2026-000201
    """
    return api_client.request("GET", f"/orders/{order_id}")


@mcp.tool()
def list_client_orders(client_id: str, status: str | None = None) -> str:
    """
    Liste les commandes d'un client, optionnellement filtrées par statut.

    Args:
        client_id: Identifiant client, ex. CL-004
        status: Filtre optionnel : en_attente, en_preparation, expediee, livree, annulee, retour_demande
    """
    params: dict[str, str] = {"client_id": client_id}
    if status:
        params["status"] = status
    return api_client.request("GET", "/orders", params=params)


@mcp.tool()
def cancel_order(order_id: str, reason: str | None = None) -> str:
    """
    Annule une commande (uniquement en_attente ou en_preparation).

    Args:
        order_id: Identifiant commande
        reason: Motif d'annulation optionnel
    """
    body = {"reason": reason} if reason else {}
    return api_client.request("POST", f"/orders/{order_id}/cancel", json_body=body)


@mcp.tool()
def get_client_by_email(email: str) -> str:
    """
    Trouve un client par adresse courriel (insensible à la casse).

    Args:
        email: Adresse courriel du client
    """
    return api_client.request("GET", "/clients/by-email", params={"email": email})


@mcp.tool()
def get_client(client_id: str) -> str:
    """
    Récupère le profil d'un client (fidélité, risk_flags, notes).

    Args:
        client_id: Identifiant client, ex. CL-004
    """
    return api_client.request("GET", f"/clients/{client_id}")


@mcp.tool()
def search_products(query: str, category: str | None = None, limit: int = 10) -> str:
    """
    Recherche des produits actifs par nom, SKU ou catégorie.

    Args:
        query: Texte de recherche
        category: Catégorie optionnelle (chaussures, vestes, etc.)
        limit: Nombre max de résultats (défaut 10)
    """
    params: dict[str, str | int] = {"search": query, "limit": limit}
    if category:
        params["category"] = category
    return api_client.request("GET", "/products", params=params)


@mcp.tool()
def get_product(product_id: str) -> str:
    """
    Fiche produit (prix, garantie, éligibilité retour).

    Args:
        product_id: SKU, ex. NTG-SHOE-001
    """
    return api_client.request("GET", f"/products/{product_id}")


@mcp.tool()
def get_product_stock(product_id: str) -> str:
    """
    Stock d'un produit par entrepôt (MTL, Québec, Vancouver).

    Args:
        product_id: SKU produit
    """
    return api_client.request("GET", f"/products/{product_id}/stock")


@mcp.tool()
def create_return_request(
    order_id: str,
    product_id: str,
    reason: str,
    notes: str | None = None,
) -> str:
    """
    Crée une demande de retour SAV (statut pending).

    La commande doit être livree ou expediee; le produit doit être dans la commande
    et éligible au retour; pas de doublon pending pour le même article.

    Args:
        order_id: Identifiant commande
        product_id: SKU de l'article à retourner
        reason: Motif (ex. inconfort_taille, defaut_batterie)
        notes: Notes internes optionnelles
    """
    body: dict[str, str] = {
        "order_id": order_id,
        "product_id": product_id,
        "reason": reason,
    }
    if notes:
        body["notes"] = notes
    return api_client.request("POST", "/returns", json_body=body)


@mcp.tool()
def get_return(return_id: str) -> str:
    """
    Détail d'une demande de retour existante.

    Args:
        return_id: ex. RET-2026-001
    """
    return api_client.request("GET", f"/returns/{return_id}")


@mcp.tool()
def list_returns(order_id: str | None = None, status: str | None = None) -> str:
    """
    Liste les retours, filtrés par commande ou statut.

    Args:
        order_id: Filtrer par commande
        status: pending, approved, rejected, refunded
    """
    params = {}
    if order_id:
        params["order_id"] = order_id
    if status:
        params["status"] = status
    return api_client.request("GET", "/returns", params=params or None)


@mcp.tool()
def update_return_status(
    return_id: str,
    status: str,
    refund_amount: float | None = None,
    notes: str | None = None,
) -> str:
    """
    Met à jour un retour pending vers approved, rejected ou refunded.

    Args:
        return_id: Identifiant retour
        status: approved | rejected | refunded
        refund_amount: Montant remboursement optionnel (sinon calcul automatique)
        notes: Notes optionnelles
    """
    body: dict[str, str | float] = {"status": status}
    if refund_amount is not None:
        body["refund_amount"] = refund_amount
    if notes:
        body["notes"] = notes
    return api_client.request("PATCH", f"/returns/{return_id}", json_body=body)


@mcp.tool()
def validate_coupon(code: str, client_id: str, order_subtotal: float) -> str:
    """
    Valide un code promo pour un client et un sous-total de commande.

    Args:
        code: Code coupon, ex. TRAIL20, VIP15
        client_id: Identifiant client
        order_subtotal: Sous-total avant rabais (CAD)
    """
    return api_client.request(
        "POST",
        "/coupons/validate",
        json_body={
            "code": code,
            "client_id": client_id,
            "order_subtotal": order_subtotal,
        },
    )


if __name__ == "__main__":
    mcp.run()
