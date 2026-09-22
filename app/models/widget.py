from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class Widget(Base):
    __tablename__ = "widgets"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    tenant_id: Mapped[int] = mapped_column(
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    widget_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="lead_capture",
    )

    title: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    form_fields: Mapped[dict] = mapped_column(
        JSON,
        nullable=False,
        default=dict,
    )

    button_text: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        default="Submit",
    )

    display_options: Mapped[dict] = mapped_column(
        JSON,
        nullable=False,
        default=dict,
    )

    version: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=1,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    tenant = relationship(
        "Tenant",
        back_populates="widgets",
    )

    submissions = relationship(
        "Submission",
        back_populates="widget",
        cascade="all, delete-orphan",
    )