from fastapi import Request
from fastapi.responses import JSONResponse


class BusinessRuleError(Exception):
    def __init__(self, message: str, status_code: int = 409):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class NotFoundError(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


async def business_rule_handler(_request: Request, exc: BusinessRuleError) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message},
    )


async def not_found_handler(_request: Request, exc: NotFoundError) -> JSONResponse:
    return JSONResponse(status_code=404, content={"detail": exc.message})
