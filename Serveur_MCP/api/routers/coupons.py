from fastapi import APIRouter, Query

from api.dependencies import DbConn
from api.schemas.coupon import (
    CouponOut,
    CouponValidateRequest,
    CouponValidateResponse,
)
from api.services import coupon_service

router = APIRouter(prefix="/coupons", tags=["coupons"])


@router.get("", response_model=list[CouponOut])
def list_coupons(db: DbConn, active_only: bool = Query(False)):
    return coupon_service.list_coupons(db, active_only)


@router.post("/validate", response_model=CouponValidateResponse)
def validate_coupon(db: DbConn, body: CouponValidateRequest):
    return coupon_service.validate_coupon(
        db, body.code, body.client_id, body.order_subtotal
    )


@router.get("/{code}", response_model=CouponOut)
def get_coupon(db: DbConn, code: str):
    return coupon_service.get_coupon(db, code)
