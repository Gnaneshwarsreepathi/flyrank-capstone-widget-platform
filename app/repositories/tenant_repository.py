from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.tenant import Tenant


def get_tenant_by_email(
    db: Session,
    email: str,
) -> Tenant | None:
    statement = select(Tenant).where(Tenant.email == email)

    return db.execute(statement).scalar_one_or_none()


def get_tenant_by_id(
    db: Session,
    tenant_id: int,
) -> Tenant | None:
    statement = select(Tenant).where(Tenant.id == tenant_id)

    return db.execute(statement).scalar_one_or_none()


def create_tenant(
    db: Session,
    name: str,
    email: str,
    password_hash: str,
) -> Tenant:
    tenant = Tenant(
        name=name,
        email=email,
        password_hash=password_hash,
    )

    db.add(tenant)
    db.commit()
    db.refresh(tenant)

    return tenant