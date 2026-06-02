from fastapi import APIRouter, Query, Response, status

from api.dependencies import DbConn
from api.schemas.client import ClientCreate, ClientOut, ClientUpdate
from api.services import client_service

router = APIRouter(prefix="/clients", tags=["clients"])


@router.get("", response_model=list[ClientOut])
def list_clients(
    db: DbConn,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
):
    return client_service.list_clients(db, skip, limit)


@router.get("/by-email", response_model=ClientOut)
def get_client_by_email(db: DbConn, email: str = Query(..., min_length=3)):
    return client_service.get_client_by_email(db, email)


@router.get("/{client_id}", response_model=ClientOut)
def get_client(db: DbConn, client_id: str):
    return client_service.get_client(db, client_id)


@router.post("", response_model=ClientOut, status_code=status.HTTP_201_CREATED)
def create_client(db: DbConn, body: ClientCreate):
    return client_service.create_client(db, body.model_dump())


@router.patch("/{client_id}", response_model=ClientOut)
def update_client(db: DbConn, client_id: str, body: ClientUpdate):
    return client_service.update_client(db, client_id, body.model_dump(exclude_unset=True))


@router.delete("/{client_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_client(db: DbConn, client_id: str):
    client_service.delete_client(db, client_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
