from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator


class SubmissionCreate(BaseModel):
    widget_id: int = Field(..., gt=0)
    payload: dict[str, Any] = Field(default_factory=dict)
    honeypot: str = Field(default="", max_length=100)

    @field_validator("payload")
    @classmethod
    def validate_payload(cls, value: dict[str, Any]) -> dict[str, Any]:
        if len(value) > 50:
            raise ValueError("Payload cannot contain more than 50 fields")

        for key, field_value in value.items():
            if len(str(key)) > 100:
                raise ValueError("Payload field names cannot exceed 100 characters")

            if isinstance(field_value, str) and len(field_value) > 5000:
                raise ValueError(
                    "Payload text values cannot exceed 5000 characters"
                )

        return value


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