import os

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.api.submissions import limiter as submission_limiter
from app.db.session import Base, get_db
from app.main import app
from app.models.tenant import Tenant
from app.models.widget import Widget


TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql+psycopg2://postgres:postgres@localhost:5432/flyrank_test",
)

test_engine = create_engine(
    TEST_DATABASE_URL,
    pool_pre_ping=True,
)

TestingSessionLocal = sessionmaker(
    bind=test_engine,
    autoflush=False,
    autocommit=False,
)


@pytest.fixture(scope="session", autouse=True)
def prepare_test_database():
    Base.metadata.create_all(bind=test_engine)

    db = TestingSessionLocal()

    try:
        # Create the test tenant
        tenant = (
            db.query(Tenant)
            .filter(Tenant.email == "pytest@example.com")
            .first()
        )

        if not tenant:
            tenant = Tenant(
                name="Pytest Tenant",
                email="pytest@example.com",
                password_hash="pytest-password-hash",
            )
            db.add(tenant)
            db.commit()
            db.refresh(tenant)

        # Create the test widget with a fixed ID.
        # This widget is used by tenant-isolation tests.
        widget = (
            db.query(Widget)
            .filter(Widget.id == 2)
            .first()
        )

        if not widget:
            widget = Widget(
                id=2,
                tenant_id=tenant.id,
                widget_type="lead_capture",
                title="Pytest Widget",
                description="Widget used for automated tests",
                form_fields={
                    "name": {
                        "type": "text",
                        "label": "Full Name",
                        "required": True,
                    },
                    "email": {
                        "type": "email",
                        "label": "Email Address",
                        "required": True,
                    },
                },
                button_text="Submit",
                display_options={},
                version=1,
                is_active=True,
            )

            db.add(widget)
            db.commit()

        # IMPORTANT:
        # Because the test widget has a manually assigned ID (2),
        # synchronize PostgreSQL's sequence so the next generated
        # widget ID will be 3 instead of trying to reuse ID 2.
        db.execute(
            text(
                "SELECT setval("
                "pg_get_serial_sequence('widgets', 'id'), "
                "COALESCE((SELECT MAX(id) FROM widgets), 1), "
                "true)"
            )
        )
        db.commit()

    finally:
        db.close()

    yield

    # Clean up the test database after the complete test session.
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def db_session():
    db = TestingSessionLocal()

    try:
        yield db
    finally:
        db.close()


@pytest.fixture(autouse=True)
def override_database():
    def override_get_db():
        db = TestingSessionLocal()

        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    yield

    app.dependency_overrides.clear()


@pytest.fixture(autouse=True)
def reset_rate_limiter():
    submission_limiter._storage.reset()

    yield

    submission_limiter._storage.reset()