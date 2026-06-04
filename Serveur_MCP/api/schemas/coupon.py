from pydantic import BaseModel


class CouponOut(BaseModel):
    code: str
    description: str | None = None
    discount_percent: float | None = None
    discount_fixed: float | None = None
    min_order_amount: float
    valid_from: str
    valid_until: str
    applies_to_sale: int = 0
    loyalty_required: str | None = None
    is_active: int = 1


class CouponValidateRequest(BaseModel):
    code: str
    client_id: str
    order_subtotal: float


class CouponValidateResponse(BaseModel):
    valid: bool
    discount_amount: float = 0.0
    message: str
    code: str | None = None
