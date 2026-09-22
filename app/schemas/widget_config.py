from pydantic import BaseModel


class WidgetConfigResponse(BaseModel):
    id: int
    widget_type: str
    title: str
    description: str | None
    form_fields: dict
    button_text: str
    display_options: dict
    version: int
    is_active: bool