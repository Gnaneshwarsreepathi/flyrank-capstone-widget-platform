from sqlalchemy.orm import Session

from app.models.widget import Widget
from app.repositories.widget_repository import (
    create_widget,
    delete_widget,
    get_widget_by_id,
    get_widgets_by_tenant,
    update_widget,
)


def list_widgets(
    db: Session,
    tenant_id: int,
) -> list[Widget]:
    return get_widgets_by_tenant(
        db=db,
        tenant_id=tenant_id,
    )


def get_widget(
    db: Session,
    widget_id: int,
    tenant_id: int,
) -> Widget | None:
    return get_widget_by_id(
        db=db,
        widget_id=widget_id,
        tenant_id=tenant_id,
    )


def create_new_widget(
    db: Session,
    tenant_id: int,
    widget_type: str,
    title: str,
    description: str | None,
    form_fields: dict,
    button_text: str,
    display_options: dict,
    is_active: bool,
) -> Widget:
    return create_widget(
        db=db,
        tenant_id=tenant_id,
        widget_type=widget_type,
        title=title,
        description=description,
        form_fields=form_fields,
        button_text=button_text,
        display_options=display_options,
        is_active=is_active,
    )


def update_existing_widget(
    db: Session,
    widget: Widget,
    widget_type: str,
    title: str,
    description: str | None,
    form_fields: dict,
    button_text: str,
    display_options: dict,
    is_active: bool,
) -> Widget:
    return update_widget(
        db=db,
        widget=widget,
        widget_type=widget_type,
        title=title,
        description=description,
        form_fields=form_fields,
        button_text=button_text,
        display_options=display_options,
        is_active=is_active,
    )


def remove_widget(
    db: Session,
    widget: Widget,
) -> None:
    delete_widget(
        db=db,
        widget=widget,
    )