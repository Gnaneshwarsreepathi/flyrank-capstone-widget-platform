from fastapi import APIRouter, Depends, Header, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.widget import Widget
from app.schemas.submission import SubmissionCreate, SubmissionResponse
from app.services.submission_service import process_submission

router = APIRouter(prefix="/submissions", tags=["Submissions"])


@router.post(
    "",
    response_model=SubmissionResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_public_submission(
    request: Request,
    submission: SubmissionCreate,
    idempotency_key: str | None = Header(default=None),
    db: Session = Depends(get_db),
):
    if not idempotency_key:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Idempotency-Key header is required",
        )

    if len(idempotency_key) > 255:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Idempotency-Key is too long",
        )

    if submission.honeypot:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Spam detected",
        )

    widget = db.query(Widget).filter(
        Widget.id == submission.widget_id,
        Widget.is_active.is_(True),
    ).first()

    if not widget:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Widget not found or inactive",
        )

    client_ip = request.client.host if request.client else None

    saved_submission, created = process_submission(
        db=db,
        widget_id=widget.id,
        tenant_id=widget.tenant_id,
        idempotency_key=idempotency_key,
        payload=submission.payload,
        ip_address=client_ip,
    )

    if not created:
        return saved_submission

    return saved_submission