from fastapi import APIRouter, Query, status

from api.dependencies import DbConn
from api.schemas.order import (
    OrderCancelRequest,
    OrderNotesUpdate,
    OrderOut,
    OrderSummaryOut,
)
from api.services import order_service

router = APIRouter(prefix="/orders", tags=["orders"])


@router.get("", response_model=list[OrderSummaryOut])
def list_orders(
    db: DbConn,
    client_id: str | None = None,
    status: str | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
):
    return order_service.list_orders(db, client_id, status, skip, limit)


@router.get("/{order_id}", response_model=OrderOut)
def get_order(db: DbConn, order_id: str):
    return order_service.get_order(db, order_id)


@router.post("/{order_id}/cancel", response_model=OrderOut)
def cancel_order(db: DbConn, order_id: str, body: OrderCancelRequest | None = None):
    reason = body.reason if body else None
    return order_service.cancel_order(db, order_id, reason)


@router.patch("/{order_id}", response_model=OrderSummaryOut)
def patch_order_notes(db: DbConn, order_id: str, body: OrderNotesUpdate):
    result = order_service.update_order_notes(db, order_id, body.notes)
    return {k: v for k, v in result.items() if k != "items" and k != "client"}
