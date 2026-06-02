from pydantic import BaseModel


class ProductOut(BaseModel):
    product_id: str
    name: str
    category: str
    price: float
    currency: str = "CAD"
    available_sizes: str | None = None
    colors: str | None = None
    warranty_months: int = 24
    weight_g: int | None = None
    recommended_use: str | None = None
    waterproof: str | None = None
    return_eligible: int = 1
    is_active: int = 1
    notes: str | None = None


class StockLineOut(BaseModel):
    product_id: str
    warehouse_id: str
    quantity: int
    reorder_threshold: int
    warehouse_name: str | None = None
    city: str | None = None
    province: str | None = None


class InventoryLineOut(BaseModel):
    product_id: str
    warehouse_id: str
    quantity: int
    reorder_threshold: int
    warehouse_name: str | None = None
    city: str | None = None
    province: str | None = None
    product_name: str | None = None


class WarehouseOut(BaseModel):
    warehouse_id: str
    name: str
    city: str
    province: str
    country: str = "CA"
    is_active: int = 1
