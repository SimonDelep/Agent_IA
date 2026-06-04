from typing import Literal

from pydantic import BaseModel, Field


class ReturnOut(BaseModel):
    return_id: str
    order_id: str
    product_id: str
    reason: str
    status: Literal["pending", "approved", "rejected", "refunded"]
    requested_at: str
    resolved_at: str | None = None
    refund_amount: float | None = None
    notes: str | None = None
    warning: str | None = None


class ReturnCreate(BaseModel):
    order_id: str
    product_id: str
    reason: str
    notes: str | None = None


class ReturnUpdate(BaseModel):
    status: Literal["approved", "rejected", "refunded"]
    refund_amount: float | None = None
    notes: str | None = None
