from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.widget import Widget


def get_widgets_by_tenant(
    db: Session,
    tenant_id: int,
) -> list[Widget]:
    statement = (
        select(Widget)
        .where(Widget.tenant_id == tenant_id)
        .order_by(Widget.id)
    )
    return list(db.execute(statement).scalars().all())


def get_widget_by_id(
    db: Session,
    widget_id: int,
    tenant_id: int,
) -> Widget | None:
    statement = select(Widget).where(
        Widget.id == widget_id,
        Widget.tenant_id == tenant_id,
    )
    return db.execute(statement).scalar_one_or_none()


def create_widget(
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
    widget = Widget(
        tenant_id=tenant_id,
        widget_type=widget_type,
        title=title,
        description=description,
        form_fields=form_fields,
        button_text=button_text,
        display_options=display_options,
        is_active=is_active,
    )

    db.add(widget)
    db.commit()
    db.refresh(widget)

    return widget


def update_widget(
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
    widget.widget_type = widget_type
    widget.title = title
    widget.description = description
    widget.form_fields = form_fields
    widget.button_text = button_text
    widget.display_options = display_options
    widget.is_active = is_active

    # Increment the widget configuration version
    widget.version += 1

    db.commit()
    db.refresh(widget)

    return widget


def delete_widget(
    db: Session,
    widget: Widget,
) -> None:
    db.delete(widget)
    db.commit()