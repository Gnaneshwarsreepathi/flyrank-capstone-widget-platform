from fastapi.testclient import TestClient

from app.core.security import create_access_token
from app.main import app
from app.models.tenant import Tenant
from app.models.widget import Widget


client = TestClient(app)


def test_tenant_can_create_and_update_widget(db_session):
    tenant = db_session.query(Tenant).filter(
        Tenant.email == "pytest@example.com"
    ).first()

    assert tenant is not None

    token = create_access_token(str(tenant.id))

    create_response = client.post(
        "/widgets",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "widget_type": "lead_capture",
            "title": "CRUD Test Widget",
            "description": "Widget CRUD test",
            "form_fields": {
                "name": {
                    "type": "text",
                    "label": "Full Name",
                    "required": True,
                }
            },
            "button_text": "Submit",
            "display_options": {},
            "is_active": True,
        },
    )

    assert create_response.status_code == 201

    created = create_response.json()

    assert created["title"] == "CRUD Test Widget"
    assert created["version"] == 1
    assert created["tenant_id"] == tenant.id

    widget_id = created["id"]

    update_response = client.put(
        f"/widgets/{widget_id}",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "widget_type": "lead_capture",
            "title": "Updated CRUD Test Widget",
            "description": "Updated description",
            "form_fields": {
                "name": {
                    "type": "text",
                    "label": "Full Name",
                    "required": True,
                },
                "email": {
                    "type": "email",
                    "label": "Email",
                    "required": True,
                },
            },
            "button_text": "Send Enquiry",
            "display_options": {},
            "is_active": True,
        },
    )

    assert update_response.status_code == 200

    updated = update_response.json()

    assert updated["id"] == widget_id
    assert updated["title"] == "Updated CRUD Test Widget"
    assert updated["button_text"] == "Send Enquiry"
    assert updated["version"] == 2


def test_widget_is_tenant_isolated(db_session):
    tenant_one = db_session.query(Tenant).filter(
        Tenant.email == "pytest@example.com"
    ).first()

    assert tenant_one is not None

    widget = db_session.query(Widget).filter(
        Widget.id == 2,
        Widget.tenant_id == tenant_one.id,
    ).first()

    assert widget is not None

    tenant_two = Tenant(
        name="Widget Tenant Two",
        email="widget-tenant-two@example.com",
        password_hash="test-password-hash",
    )

    db_session.add(tenant_two)
    db_session.commit()
    db_session.refresh(tenant_two)

    token_two = create_access_token(str(tenant_two.id))

    get_response = client.get(
        f"/widgets/{widget.id}",
        headers={"Authorization": f"Bearer {token_two}"},
    )

    assert get_response.status_code == 404

    update_response = client.put(
        f"/widgets/{widget.id}",
        headers={"Authorization": f"Bearer {token_two}"},
        json={
            "widget_type": "lead_capture",
            "title": "Unauthorized Update",
            "description": "Should not update",
            "form_fields": {},
            "button_text": "Submit",
            "display_options": {},
            "is_active": True,
        },
    )

    assert update_response.status_code == 404


def test_tenant_can_delete_own_widget(db_session):
    tenant = db_session.query(Tenant).filter(
        Tenant.email == "pytest@example.com"
    ).first()

    assert tenant is not None

    token = create_access_token(str(tenant.id))

    create_response = client.post(
        "/widgets",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "widget_type": "lead_capture",
            "title": "Delete Test Widget",
            "description": "Widget to delete",
            "form_fields": {},
            "button_text": "Submit",
            "display_options": {},
            "is_active": True,
        },
    )

    assert create_response.status_code == 201

    widget_id = create_response.json()["id"]

    delete_response = client.delete(
        f"/widgets/{widget_id}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert delete_response.status_code == 204

    get_response = client.get(
        f"/widgets/{widget_id}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert get_response.status_code == 404
