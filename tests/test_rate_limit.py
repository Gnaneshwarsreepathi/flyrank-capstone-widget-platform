from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_submission_rate_limit():
    responses = []

    for index in range(6):
        response = client.post(
            "/submissions",
            json={
                "widget_id": 2,
                "payload": {
                    "name": f"Rate Test {index}",
                    "email": f"rate{index}@example.com",
                },
                "honeypot": "",
            },
            headers={
                "Idempotency-Key": f"pytest-rate-limit-{index}",
            },
        )

        responses.append(response)

    assert any(
        response.status_code == 429
        for response in responses
    )
