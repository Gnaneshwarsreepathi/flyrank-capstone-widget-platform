import logging

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)


def send_submission_webhook(submission_id: int, payload: dict) -> None:
    if not settings.webhook_url:
        return

    try:
        response = httpx.post(
            settings.webhook_url,
            json={
                "submission_id": submission_id,
                "payload": payload,
            },
            timeout=5.0,
        )
        response.raise_for_status()
    except Exception as exc:
        logger.warning(
            "Submission webhook failed for submission %s: %s",
            submission_id,
            exc,
        )


def send_submission_email(submission_id: int, payload: dict) -> None:
    """
    Email notification placeholder.

    The capstone requires email failures to be isolated from
    submission persistence. Email delivery can be configured later
    without changing the submission transaction.
    """
    try:
        logger.info(
            "Email notification queued for submission %s: %s",
            submission_id,
            payload,
        )
    except Exception as exc:
        logger.warning(
            "Submission email failed for submission %s: %s",
            submission_id,
            exc,
        )


def dispatch_submission_side_effects(
    submission_id: int,
    payload: dict,
) -> None:
    """
    Run non-critical submission side effects.

    Failures are deliberately caught so they never affect the
    already-persisted submission.
    """
    try:
        send_submission_email(
            submission_id=submission_id,
            payload=payload,
        )
    except Exception as exc:
        logger.warning(
            "Email side effect crashed for submission %s: %s",
            submission_id,
            exc,
        )

    try:
        send_submission_webhook(
            submission_id=submission_id,
            payload=payload,
        )
    except Exception as exc:
        logger.warning(
            "Webhook side effect crashed for submission %s: %s",
            submission_id,
            exc,
        )
