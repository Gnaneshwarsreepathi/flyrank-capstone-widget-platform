from datetime import datetime
from typing import Any

from pydantic import BaseModel


class DashboardSubmission(BaseModel):
    id: int
    widget_id: int
    idempotency_key: str
    payload: dict[str, Any]
    ip_address: str | None = None
    country: str | None = None
    city: str | None = None
    created_at: datetime


class DashboardResponse(BaseModel):
    total_submissions: int
    submissions: list[DashboardSubmission]