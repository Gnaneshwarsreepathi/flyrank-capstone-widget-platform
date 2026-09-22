from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_public_submission_is_created_and_idempotent():
    payload = {
        "widget_id": 2,
        "payload": {
            "name": "Test User",
            "email": "test@example.com",
        },
        "honeypot": "",
    }

    headers = {
        "Idempotency-Key": "pytest-submission-001",
    }

    first_response = client.post(
        "/submissions",
        json=payload,
        headers=headers,
    )

    assert first_response.status_code == 201

    first_data = first_response.json()

    assert first_data["widget_id"] == 2
    assert first_data["payload"] == payload["payload"]

    second_response = client.post(
        "/submissions",
        json=payload,
        headers=headers,
    )

    assert second_response.status_code == 201

    second_data = second_response.json()

    assert second_data["id"] == first_data["id"]


def test_submission_requires_idempotency_key():
    response = client.post(
        "/submissions",
        json={
            "widget_id": 2,
            "payload": {
                "name": "Test User",
                "email": "test@example.com",
            },
            "honeypot": "",
        },
    )

    assert response.status_code == 400
    assert "Idempotency-Key" in response.json()["detail"]


def test_honeypot_submission_is_rejected():
    response = client.post(
        "/submissions",
        json={
            "widget_id": 2,
            "payload": {
                "name": "Bot User",
                "email": "bot@example.com",
            },
            "honeypot": "https://spam.example.com",
        },
        headers={
            "Idempotency-Key": "pytest-honeypot-001",
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Spam detected"


def test_oversized_request_body_is_rejected():
    response = client.post(
        "/submissions",
        json={
            "widget_id": 2,
            "payload": {
                "message": "x" * 70000,
            },
            "honeypot": "",
        },
        headers={
            "Idempotency-Key": "pytest-oversized-body-001",
        },
    )

    assert response.status_code == 413
    assert response.json()["detail"] == "Request body is too large"


def test_oversized_payload_field_is_rejected():
    response = client.post(
        "/submissions",
        json={
            "widget_id": 2,
            "payload": {
                "message": "x" * 5001,
            },
            "honeypot": "",
        },
        headers={
            "Idempotency-Key": "pytest-oversized-field-001",
        },
    )

    assert response.status_code == 422