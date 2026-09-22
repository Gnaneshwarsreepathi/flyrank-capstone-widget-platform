from sqlalchemy.orm import Session

from app.repositories.submission_repository import (
    create_submission,
    get_submission_by_idempotency_key,
)


def process_submission(
    db: Session,
    widget_id: int,
    tenant_id: int,
    idempotency_key: str,
    payload: dict,
    ip_address: str | None = None,
    country: str | None = None,
    city: str | None = None,
):
    # Idempotency: return the existing submission if this request
    # has already been processed.
    existing_submission = get_submission_by_idempotency_key(
        db=db,
        widget_id=widget_id,
        idempotency_key=idempotency_key,
    )

    if existing_submission:
        return existing_submission, False

    submission = create_submission(
        db=db,
        widget_id=widget_id,
        tenant_id=tenant_id,
        idempotency_key=idempotency_key,
        payload=payload,
        ip_address=ip_address,
        country=country,
        city=city,
    )

    return submission, True