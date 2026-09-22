from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.submission import Submission


def get_submission_by_idempotency_key(
    db: Session,
    widget_id: int,
    idempotency_key: str,
) -> Submission | None:
    statement = select(Submission).where(
        Submission.widget_id == widget_id,
        Submission.idempotency_key == idempotency_key,
    )

    return db.execute(statement).scalar_one_or_none()


def create_submission(
    db: Session,
    widget_id: int,
    tenant_id: int,
    idempotency_key: str,
    payload: dict,
    ip_address: str | None = None,
    country: str | None = None,
    city: str | None = None,
) -> Submission:
    submission = Submission(
        widget_id=widget_id,
        tenant_id=tenant_id,
        idempotency_key=idempotency_key,
        payload=payload,
        ip_address=ip_address,
        country=country,
        city=city,
    )

    db.add(submission)
    db.commit()
    db.refresh(submission)

    return submission