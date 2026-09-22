from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class WidgetBase(BaseModel):
    widget_type: str = "lead_capture"
    title: str = Field(..., min_length=1, max_length=200)
    description: str | None = None
    form_fields: dict = {}
    button_text: str = "Submit"
    display_options: dict = {}
    is_active: bool = True


class WidgetCreate(WidgetBase):
    pass


class WidgetResponse(WidgetBase):
    id: int
    tenant_id: int
    version: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)