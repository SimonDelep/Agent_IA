from fastapi import APIRouter, Query, status

from api.dependencies import DbConn
from api.schemas.return_schema import ReturnCreate, ReturnOut, ReturnUpdate
from api.services import return_service

router = APIRouter(prefix="/returns", tags=["returns"])


@router.get("", response_model=list[ReturnOut])
def list_returns(
    db: DbConn,
    order_id: str | None = None,
    status: str | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
):
    return return_service.list_returns(db, order_id, status, skip, limit)


@router.get("/{return_id}", response_model=ReturnOut)
def get_return(db: DbConn, return_id: str):
    return return_service.get_return(db, return_id)


@router.post("", response_model=ReturnOut, status_code=status.HTTP_201_CREATED)
def create_return(db: DbConn, body: ReturnCreate):
    return return_service.create_return(
        db,
        body.order_id,
        body.product_id,
        body.reason,
        body.notes,
    )


@router.patch("/{return_id}", response_model=ReturnOut)
def update_return(db: DbConn, return_id: str, body: ReturnUpdate):
    return return_service.update_return(
        db,
        return_id,
        body.status,
        body.refund_amount,
        body.notes,
    )
