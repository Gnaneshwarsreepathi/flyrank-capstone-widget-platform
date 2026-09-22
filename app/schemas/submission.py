from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class SubmissionCreate(BaseModel):
    widget_id: int = Field(..., gt=0)
    payload: dict = Field(default_factory=dict)
    honeypot: str = ""


class SubmissionResponse(BaseModel):
    id: int
    widget_id: int
    tenant_id: int
    idempotency_key: str
    payload: dict
    ip_address: str | None = None
    country: str | None = None
    city: str | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)