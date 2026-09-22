from unittest.mock import patch

from app.workers.side_effects import (
    dispatch_submission_side_effects,
    send_submission_webhook,
)


def test_webhook_failure_is_swallowed():
    with patch(
        "app.workers.side_effects.settings.webhook_url",
        "http://127.0.0.1:9999/failing-webhook",
    ), patch(
        "app.workers.side_effects.httpx.post",
        side_effect=RuntimeError("Webhook unavailable"),
    ):
        # Must not raise even when the webhook fails.
        send_submission_webhook(
            submission_id=123,
            payload={"name": "Test User"},
        )


def test_email_failure_does_not_block_other_side_effects():
    with patch(
        "app.workers.side_effects.send_submission_email",
        side_effect=RuntimeError("Email service unavailable"),
    ), patch(
        "app.workers.side_effects.send_submission_webhook",
    ) as mock_webhook:
        dispatch_submission_side_effects(
            submission_id=123,
            payload={"name": "Test User"},
        )

    mock_webhook.assert_called_once_with(
        submission_id=123,
        payload={"name": "Test User"},
    )


def test_webhook_failure_does_not_crash_dispatch():
    with patch(
        "app.workers.side_effects.send_submission_email",
    ) as mock_email, patch(
        "app.workers.side_effects.send_submission_webhook",
        side_effect=RuntimeError("Webhook service unavailable"),
    ):
        # Must complete without raising.
        dispatch_submission_side_effects(
            submission_id=123,
            payload={"name": "Test User"},
        )

    mock_email.assert_called_once_with(
        submission_id=123,
        payload={"name": "Test User"},
    )
