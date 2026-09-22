from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    Header,
    HTTPException,
    Request,
    status,
)
from sqlalchemy.orm import Session
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.db.session import get_db
from app.models.widget import Widget
from app.schemas.submission import SubmissionCreate, SubmissionResponse
from app.services.geo_service import enrich_ip_address
from app.services.submission_service import process_submission
from app.workers.side_effects import dispatch_submission_side_effects


router = APIRouter(
    prefix="/submissions",
    tags=["Submissions"],
)

limiter = Limiter(
    key_func=get_remote_address,
)


@router.post(
    "",
    response_model=SubmissionResponse,
    status_code=status.HTTP_201_CREATED,
)
@limiter.limit("5/minute")
def create_public_submission(
    request: Request,
    background_tasks: BackgroundTasks,
    submission: SubmissionCreate,
    idempotency_key: str | None = Header(default=None),
    db: Session = Depends(get_db),
):
    # ---------------------------------------------------------
    # 1. Validate Idempotency-Key
    # ---------------------------------------------------------
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

    # ---------------------------------------------------------
    # 2. Honeypot spam protection
    # ---------------------------------------------------------
    if submission.honeypot:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Spam detected",
        )

    # ---------------------------------------------------------
    # 3. Validate widget
    # ---------------------------------------------------------
    widget = (
        db.query(Widget)
        .filter(
            Widget.id == submission.widget_id,
            Widget.is_active.is_(True),
        )
        .first()
    )

    if not widget:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Widget not found or inactive",
        )

    # ---------------------------------------------------------
    # 4. Get client IP
    # ---------------------------------------------------------
    client_ip = (
        request.client.host
        if request.client
        else None
    )

    # ---------------------------------------------------------
    # 5. Geo enrichment
    #
    # Provider A is attempted first.
    # Provider B is used as fallback.
    # If both fail, (None, None) is returned and the
    # submission continues normally.
    # ---------------------------------------------------------
    country, city = enrich_ip_address(client_ip)

    # ---------------------------------------------------------
    # 6. Persist submission
    #
    # Idempotency is handled inside the submission service.
    # ---------------------------------------------------------
    saved_submission, created = process_submission(
        db=db,
        widget_id=widget.id,
        tenant_id=widget.tenant_id,
        idempotency_key=idempotency_key,
        payload=submission.payload,
        ip_address=client_ip,
        country=country,
        city=city,
    )

    # ---------------------------------------------------------
    # 7. Idempotent retry
    #
    # If this idempotency key already exists, return the
    # existing submission without triggering side effects again.
    # ---------------------------------------------------------
    if not created:
        return saved_submission

    # ---------------------------------------------------------
    # 8. Non-critical side effects
    #
    # Email/webhook processing happens after persistence.
    # Any failure is isolated inside the worker and therefore
    # cannot undo the saved submission.
    # ---------------------------------------------------------
    background_tasks.add_task(
        dispatch_submission_side_effects,
        saved_submission.id,
        saved_submission.payload,
    )

    # ---------------------------------------------------------
    # 9. Return successful submission
    # ---------------------------------------------------------
    return saved_submission