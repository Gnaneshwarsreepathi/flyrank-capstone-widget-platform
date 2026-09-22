from sqlalchemy.orm import Session

from app.core.security import (
    create_access_token,
    hash_password,
    verify_password,
)
from app.models.tenant import Tenant
from app.repositories.tenant_repository import (
    create_tenant,
    get_tenant_by_email,
)


def register_tenant(
    db: Session,
    name: str,
    email: str,
    password: str,
) -> Tenant:
    existing_tenant = get_tenant_by_email(db, email)

    if existing_tenant:
        raise ValueError("A tenant with this email already exists")

    password_hash = hash_password(password)

    return create_tenant(
        db=db,
        name=name,
        email=email,
        password_hash=password_hash,
    )


def authenticate_tenant(
    db: Session,
    email: str,
    password: str,
) -> str:
    tenant = get_tenant_by_email(db, email)

    if not tenant:
        raise ValueError("Invalid email or password")

    if not verify_password(password, tenant.password_hash):
        raise ValueError("Invalid email or password")

    return create_access_token(str(tenant.id))