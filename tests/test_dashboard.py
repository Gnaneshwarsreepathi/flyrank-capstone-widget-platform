from fastapi.testclient import TestClient

from app.core.security import create_access_token
from app.main import app
from app.models.submission import Submission
from app.models.tenant import Tenant
from app.models.widget import Widget


client = TestClient(app)


def test_dashboard_returns_current_tenant_submissions(db_session):
    tenant = db_session.query(Tenant).filter(
        Tenant.email == "pytest@example.com"
    ).first()

    assert tenant is not None

    widget = db_session.query(Widget).filter(
        Widget.id == 2,
        Widget.tenant_id == tenant.id,
    ).first()

    assert widget is not None

    submission = Submission(
        widget_id=widget.id,
        tenant_id=tenant.id,
        idempotency_key="dashboard-pytest-001",
        payload={
            "name": "Dashboard Test User",
            "email": "dashboard-test@example.com",
        },
        ip_address="127.0.0.1",
        country="Ireland",
        city="Dublin",
    )

    db_session.add(submission)
    db_session.commit()
    db_session.refresh(submission)

    token = create_access_token(str(tenant.id))

    response = client.get(
        "/dashboard",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total_submissions"] >= 1
    assert any(
        item["id"] == submission.id
        for item in data["submissions"]
    )


def test_dashboard_is_tenant_isolated(db_session):
    tenant_one = db_session.query(Tenant).filter(
        Tenant.email == "pytest@example.com"
    ).first()

    assert tenant_one is not None

    tenant_two = Tenant(
        name="Dashboard Tenant Two",
        email="dashboard-tenant-two@example.com",
        password_hash="test-password-hash",
    )

    db_session.add(tenant_two)
    db_session.commit()
    db_session.refresh(tenant_two)

    widget_two = Widget(
        tenant_id=tenant_two.id,
        widget_type="lead_capture",
        title="Tenant Two Test Widget",
        description="Tenant isolation test",
        form_fields={},
        button_text="Submit",
        display_options={},
        version=1,
        is_active=True,
    )

    db_session.add(widget_two)
    db_session.commit()
    db_session.refresh(widget_two)

    submission = Submission(
        widget_id=widget_two.id,
        tenant_id=tenant_two.id,
        idempotency_key="tenant-isolation-dashboard-001",
        payload={
            "name": "Tenant Two User",
            "email": "tenant-two@example.com",
        },
    )

    db_session.add(submission)
    db_session.commit()
    db_session.refresh(submission)

    token = create_access_token(str(tenant_one.id))

    response = client.get(
        "/dashboard",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200

    data = response.json()

    assert all(
        item["id"] != submission.id
        for item in data["submissions"]
    )


def test_dashboard_requires_authentication():
    response = client.get("/dashboard")

    assert response.status_code == 401
