from typing import Literal

from pydantic import BaseModel

from api.schemas.client import ClientOut


class OrderItemOut(BaseModel):
    id: int | None = None
    order_id: str
    product_id: str
    size: str
    quantity: int
    unit_price: float
    product_name: str | None = None
    category: str | None = None


class OrderOut(BaseModel):
    order_id: str
    client_id: str
    status: Literal[
        "en_attente",
        "en_preparation",
        "expediee",
        "livree",
        "annulee",
        "retour_demande",
    ]
    order_date: str
    payment_status: str
    shipping_province: str
    shipping_method: str
    tracking_number: str | None = None
    delivery_date: str | None = None
    subtotal_amount: float
    shipping_amount: float
    tax_amount: float
    total_amount: float
    currency: str = "CAD"
    return_window_end: str | None = None
    notes: str | None = None
    items: list[OrderItemOut] = []
    client: ClientOut | None = None


class OrderSummaryOut(BaseModel):
    order_id: str
    client_id: str
    status: str
    order_date: str
    payment_status: str
    shipping_province: str
    shipping_method: str
    tracking_number: str | None = None
    delivery_date: str | None = None
    subtotal_amount: float
    shipping_amount: float
    tax_amount: float
    total_amount: float
    currency: str = "CAD"
    return_window_end: str | None = None
    notes: str | None = None


class OrderCancelRequest(BaseModel):
    reason: str | None = None


class OrderNotesUpdate(BaseModel):
    notes: str | None = None
