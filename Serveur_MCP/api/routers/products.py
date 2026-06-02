from fastapi import APIRouter, Query

from api.dependencies import DbConn
from api.exceptions import NotFoundError
from api.repositories import products as products_repo
from api.schemas.product import ProductOut, StockLineOut

router = APIRouter(prefix="/products", tags=["products"])


@router.get("", response_model=list[ProductOut])
def list_products(
    db: DbConn,
    search: str | None = None,
    category: str | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
):
    if search:
        return products_repo.search(db, search, category, limit)
    return products_repo.list_all(db, skip, limit)


@router.get("/{product_id}", response_model=ProductOut)
def get_product(db: DbConn, product_id: str):
    product = products_repo.get_by_id(db, product_id)
    if not product:
        raise NotFoundError(f"Produit {product_id} introuvable.")
    return product


@router.get("/{product_id}/stock", response_model=list[StockLineOut])
def get_product_stock(db: DbConn, product_id: str):
    product = products_repo.get_by_id(db, product_id)
    if not product:
        raise NotFoundError(f"Produit {product_id} introuvable.")
    return products_repo.get_stock(db, product_id)
