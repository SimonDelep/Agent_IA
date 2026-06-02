from fastapi import APIRouter, Query

from api.dependencies import DbConn
from api.repositories import inventory as inventory_repo
from api.schemas.product import InventoryLineOut, WarehouseOut

router = APIRouter(tags=["inventory"])


@router.get("/warehouses", response_model=list[WarehouseOut])
def list_warehouses(db: DbConn):
    return inventory_repo.list_warehouses(db)


@router.get("/inventory", response_model=list[InventoryLineOut])
def list_inventory(
    db: DbConn,
    product_id: str | None = None,
    warehouse_id: str | None = None,
):
    return inventory_repo.list_inventory(db, product_id, warehouse_id)
