from datetime import datetime

from pydantic import BaseModel, ConfigDict


class TenantBase(BaseModel):
    name: str
    email: str


class TenantCreate(TenantBase):
    password: str


class TenantResponse(TenantBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)