from sqlalchemy.exc import IntegrityError
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
    # Fast path:
    # If this idempotency key has already been processed,
    # return the original submission instead of creating another one.
    existing_submission = get_submission_by_idempotency_key(
        db=db,
        widget_id=widget_id,
        idempotency_key=idempotency_key,
    )

    if existing_submission:
        return existing_submission, False

    try:
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

    except IntegrityError:
        # A concurrent request may have inserted the same
        # widget_id + idempotency_key between our initial
        # lookup and the insert.
        #
        # Roll back the failed transaction so the SQLAlchemy
        # session can be used again.
        db.rollback()

        existing_submission = get_submission_by_idempotency_key(
            db=db,
            widget_id=widget_id,
            idempotency_key=idempotency_key,
        )

        if existing_submission:
            return existing_submission, False

        # If the IntegrityError was caused by something other
        # than the idempotency constraint, do not hide it.
        raise