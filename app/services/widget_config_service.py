from sqlalchemy.orm import Session

from app.models.widget import Widget
from app.repositories.widget_repository import get_widget_by_id


def get_public_widget_config(
    db: Session,
    widget_id: int,
) -> Widget | None:
    widget = db.query(Widget).filter(
        Widget.id == widget_id,
        Widget.is_active.is_(True),
    ).first()

    return widget