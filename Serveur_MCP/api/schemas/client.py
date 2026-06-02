from typing import Literal

from pydantic import BaseModel, EmailStr, Field


class ClientOut(BaseModel):
    client_id: str
    first_name: str
    last_name: str
    email: str
    phone: str | None = None
    province: str
    country: str = "CA"
    loyalty_level: Literal["standard", "silver", "gold"]
    preferred_language: str = "fr"
    created_at: str
    risk_flags: list[str] = Field(default_factory=list)
    notes: str | None = None

    model_config = {"from_attributes": True}


class ClientCreate(BaseModel):
    client_id: str | None = None
    first_name: str
    last_name: str
    email: EmailStr
    phone: str | None = None
    province: str
    country: str = "CA"
    loyalty_level: Literal["standard", "silver", "gold"] = "standard"
    preferred_language: str = "fr"
    created_at: str | None = None
    risk_flags: list[str] = Field(default_factory=list)
    notes: str | None = None


class ClientUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    email: EmailStr | None = None
    phone: str | None = None
    province: str | None = None
    country: str | None = None
    loyalty_level: Literal["standard", "silver", "gold"] | None = None
    preferred_language: str | None = None
    risk_flags: list[str] | None = None
    notes: str | None = None
