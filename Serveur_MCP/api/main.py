from fastapi import FastAPI

from api.exceptions import (
    BusinessRuleError,
    NotFoundError,
    business_rule_handler,
    not_found_handler,
)
from api.routers import clients, coupons, inventory, orders, products, returns

app = FastAPI(
    title="NordTrail Gear API",
    description="API REST service client — commandes, retours, catalogue (CAD)",
    version="1.0.0",
)

app.add_exception_handler(BusinessRuleError, business_rule_handler)
app.add_exception_handler(NotFoundError, not_found_handler)

app.include_router(clients.router)
app.include_router(orders.router)
app.include_router(products.router)
app.include_router(inventory.router)
app.include_router(returns.router)
app.include_router(coupons.router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "nordtrail-gear-api"}
