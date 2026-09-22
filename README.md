# FlyRank Backend Internship Capstone

## Embeddable Widget & Lead-Capture Platform

A multi-tenant backend platform built with **Python, FastAPI and PostgreSQL** for creating embeddable lead-capture widgets, collecting public submissions, enriching submissions with geo information, and exposing tenant-scoped dashboard data.

## Features

### Authentication & Tenants

- Tenant registration and login
- JWT-based authentication
- Password hashing
- Tenant-scoped access to protected resources

### Widget Management

- Create widgets
- List tenant widgets
- Retrieve individual widgets
- Update widgets
- Delete widgets
- Widget versioning
- Configurable form fields
- Configurable button text
- Configurable display options
- Active/inactive widget state

### Public Widget Configuration

Public widget configuration is available through:

```text
GET /widgets/{widget_id}/config
```

The endpoint supports:

- Public access without tenant authentication
- Active widget validation
- ETag-based caching
- Conditional requests using `If-None-Match`
- HTTP `304 Not Modified`
- Cache-Control headers
- Widget version-based ETags

Example cache headers:

```text
Cache-Control: public, max-age=60, must-revalidate
ETag: "widget-1-v2"
```

### Embeddable JavaScript

The widget embed script is available at:

```text
GET /widget/embed.js
```

The embed script:

1. Loads the public widget configuration.
2. Builds the lead-capture form dynamically.
3. Renders configured fields.
4. Includes honeypot spam protection.
5. Generates an idempotency key for each submission.
6. Sends the submission to the public submission API.
7. Excludes the honeypot field from the normal submission payload.

### Public Submissions

Public submissions are handled through:

```text
POST /submissions
```

The submission flow includes:

- Widget validation
- Active-widget validation
- Pydantic payload validation
- Request-size protection
- Rate limiting
- Honeypot spam protection
- Idempotency
- PostgreSQL persistence
- IP address capture
- Geo enrichment
- Background side effects

### Abuse Protection

The public submission endpoint includes:

- `5/minute` rate limiting
- 64 KiB request-size protection
- Maximum payload field count
- Maximum field-name length
- Maximum text-value length
- Idempotency-key validation
- Honeypot spam protection

### Geo Enrichment

The platform supports two geo providers:

```text
Provider A → Provider B fallback
```

The enrichment flow is:

1. Attempt Provider A.
2. If Provider A fails, attempt Provider B.
3. If Provider B also fails, continue without geo information.
4. The submission remains eligible for persistence even when geo enrichment fails.

Geo information can populate:

- Country
- City

### Safe Side Effects

Submission side effects are dispatched after successful persistence.

Supported side effects include:

- Email handling
- Webhook delivery

Side-effect failures are caught and logged so they do not prevent the primary submission from being stored.

Webhook processing is performed using FastAPI background tasks.

### Dashboard

Tenant-authenticated dashboard endpoint:

```text
GET /dashboard
```

The dashboard provides:

- Total submission count
- Tenant-scoped submission records
- Configurable result limit

## Architecture

The project follows a layered architecture:

```text
app/
├── api/             # HTTP/API routes
├── core/            # Configuration and security
├── db/              # Database session and helpers
├── models/          # SQLAlchemy database models
├── repositories/    # Data-access layer
├── schemas/         # Pydantic request/response schemas
├── services/        # Business logic
└── workers/         # Background side effects

widget/
└── embed.js         # Embeddable widget script

migrations/          # Alembic database migrations
tests/               # Automated tests
```

### Layer Responsibilities

#### API

Handles:

- HTTP requests
- Authentication dependencies
- Request/response handling
- HTTP status codes

#### Services

Handles:

- Business logic
- Widget operations
- Submission processing
- Geo enrichment
- Dashboard aggregation

#### Repositories

Handles:

- Database queries
- Tenant-scoped data access
- Widget persistence
- Submission persistence

#### Models

Contains SQLAlchemy models for:

- Tenant
- Widget
- Submission

#### Schemas

Contains Pydantic models for:

- Authentication
- Widgets
- Widget configuration
- Submissions
- Dashboard responses

#### Workers

Contains background side-effect handling such as:

- Email processing
- Webhook delivery

## Database

PostgreSQL is used for persistent storage.

Main entities:

```text
tenants
widgets
submissions
```

### Tenant Isolation

Widgets and submissions are associated with a tenant.

Protected widget operations use the authenticated tenant ID when querying the database.

Dashboard submission queries are also scoped by tenant ID.

### Submission Idempotency

Submission idempotency is enforced at the database level using a unique constraint on:

```text
widget_id + idempotency_key
```

This prevents duplicate submissions for the same widget and idempotency key.

## Environment Configuration

Copy the example configuration:

```bash
cp .env.example .env
```

For local development on the host machine, configure the database URL to use:

```text
DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/flyrank
```

When running through Docker Compose, the API container uses the PostgreSQL service hostname:

```text
postgresql+psycopg2://postgres:postgres@db:5432/flyrank
```

Configure the required database, JWT, CORS and optional provider/webhook settings in `.env`.

The `.env` file is excluded from Git.

Do not commit real credentials, API keys or secrets.

## Running with Docker

Build and start the application:

```bash
docker compose up --build
```

The API will be available at:

```text
http://localhost:8000
```

Health endpoint:

```text
GET /health
```

Example:

```text
http://localhost:8000/health
```

Expected response:

```json
{
  "status": "ok",
  "service": "flyrank-capstone-api"
}
```

## Database Migrations

Apply all migrations:

```bash
alembic upgrade head
```

Check the current migration:

```bash
alembic current
```

Verify that the SQLAlchemy models and migrations are synchronized:

```bash
alembic check
```

The verified migration state is:

```text
a7f82c05cda9 (head)
```

The verified Alembic consistency check returned:

```text
No new upgrade operations detected.
```

## Testing

Run the complete automated test suite:

```bash
pytest -q
```

Final verified result:

```text
23 passed, 21 warnings in 0.26s
```

The warnings are dependency/runtime deprecation warnings and did not cause test failures.

### Test Coverage

The automated tests cover:

- Health endpoint
- Widget CRUD
- Widget tenant isolation
- Public widget configuration
- Widget caching and ETag behaviour
- Public submissions
- Submission validation
- Submission idempotency
- Rate limiting
- Geo-provider fallback
- Safe side effects
- Dashboard behaviour

Test files include:

```text
tests/
├── conftest.py
├── test_dashboard.py
├── test_geo_service.py
├── test_health_and_widget.py
├── test_rate_limit.py
├── test_side_effects.py
├── test_submissions.py
└── test_widgets.py
```

## API Endpoints

| Method | Endpoint | Authentication | Purpose |
|---|---|---|---|
| GET | `/health` | Public | Health check |
| POST | `/auth/register` | Public | Register tenant |
| POST | `/auth/login` | Public | Authenticate tenant |
| GET | `/widgets` | JWT | List tenant widgets |
| POST | `/widgets` | JWT | Create widget |
| GET | `/widgets/{widget_id}` | JWT | Get tenant widget |
| PUT | `/widgets/{widget_id}` | JWT | Update widget |
| DELETE | `/widgets/{widget_id}` | JWT | Delete widget |
| GET | `/widgets/{widget_id}/config` | Public | Get public widget configuration |
| POST | `/submissions` | Public | Create lead submission |
| GET | `/dashboard` | JWT | Get tenant dashboard data |
| GET | `/widget/embed.js` | Public | Get embeddable JavaScript |

## Interactive API Documentation

FastAPI provides interactive API documentation at:

```text
http://localhost:8000/docs
```

Alternative OpenAPI documentation:

```text
http://localhost:8000/redoc
```

## Example Workflow

### 1. Register a Tenant

```text
POST /auth/register
```

Example request:

```json
{
  "name": "Example Tenant",
  "email": "tenant@example.com",
  "password": "ExamplePassword123!"
}
```

### 2. Login

```text
POST /auth/login
```

Example request:

```json
{
  "email": "tenant@example.com",
  "password": "ExamplePassword123!"
}
```

The API returns a JWT access token.

### 3. Create a Widget

Use the returned JWT:

```text
Authorization: Bearer <access_token>
```

Then create a widget:

```text
POST /widgets
```

Example:

```json
{
  "widget_type": "lead_capture",
  "title": "Contact Us",
  "description": "Please provide your details.",
  "form_fields": {
    "name": {
      "type": "text",
      "label": "Full Name",
      "required": true
    },
    "email": {
      "type": "email",
      "label": "Email Address",
      "required": true
    }
  },
  "button_text": "Submit",
  "display_options": {},
  "is_active": true
}
```

### 4. Load Public Widget Configuration

Use the widget ID:

```text
GET /widgets/{widget_id}/config
```

No JWT is required for this endpoint.

### 5. Embed the Widget

Load:

```text
/widget/embed.js
```

The script retrieves the widget configuration and renders the configured lead-capture form.

### 6. Submit a Lead

The widget sends the submission to:

```text
POST /submissions
```

with an idempotency header:

```text
Idempotency-Key: <unique-key>
```

## Security and Protection

The platform includes several protection mechanisms at public boundaries.

### Request Size

Requests larger than the configured 64 KiB limit are rejected.

### Payload Validation

Submission payloads are limited by:

- Maximum number of fields
- Maximum field-name length
- Maximum text-value length

### Rate Limiting

The public submission endpoint is limited to:

```text
5 requests/minute/client
```

### Honeypot

The public form contains a honeypot field.

A non-empty honeypot value is treated as spam and rejected.

### Idempotency

Clients provide:

```text
Idempotency-Key
```

A database uniqueness constraint prevents duplicate persistence for the same widget and key.

### Tenant Isolation

Protected resources use the authenticated tenant ID when retrieving tenant-owned records.

## CORS

The FastAPI application includes CORS middleware.

Development origins are configured through:

```text
CORS_ORIGINS
```

The example configuration includes:

```text
http://localhost:8000
http://localhost:5500
```

This allows the embeddable widget to communicate with the API from configured development origins.

## Safe Failure Behaviour

### Geo Provider Failure

Geo enrichment follows:

```text
Provider A
    |
    | failure
    v
Provider B
    |
    | failure
    v
Continue without geo data
```

A geo-provider failure does not prevent the submission from being persisted.

### Webhook Failure

Webhook delivery is isolated from the primary persistence flow.

A failed webhook is logged and does not cause the submission itself to fail.

### Email Failure

Email-side-effect failures are also isolated and logged.

## Acceptance Verification

The implementation addresses the capstone acceptance areas:

- Valid public submissions
- Cross-origin access
- Invalid requests
- Oversized requests
- Burst request rate limiting
- Geo Provider A failure
- Geo Provider B fallback
- Both geo providers failing without blocking storage
- Email failure without blocking storage
- Webhook failure without blocking storage
- Honeypot spam rejection
- Tenant isolation
- Idempotent submissions
- PostgreSQL persistence
- Alembic migrations
- Widget versioning
- Cached widget configuration
- Dashboard access
- Embeddable widget delivery

Detailed evidence is documented in:

```text
EVIDENCE.md
```

## Project Documentation

Additional documentation:

- `DESIGN.md` — architecture, actors, data model, request flows, protection mechanisms and design decisions
- `EVIDENCE.md` — implementation and acceptance-probe evidence
- `BUILDLOG.md` — development history and AI assistance disclosure
- `.env.example` — environment configuration template
- `capstone.yaml` — capstone run and test configuration

## Project Configuration

The capstone configuration provides:

```yaml
run: docker compose up --build
seed: python -m app.db.seed
test: pytest
base_url: http://localhost:8000
```

Configured API areas include:

```text
/health
/auth
/widgets
/widgets/{widget_id}/config
/submissions
/dashboard
```

## Repository Structure

```text
flyrank-capstone-widget-platform/
│
├── app/
│   ├── api/
│   │   ├── auth.py
│   │   ├── dashboard.py
│   │   ├── deps.py
│   │   ├── submissions.py
│   │   └── widgets.py
│   │
│   ├── core/
│   │   ├── config.py
│   │   └── security.py
│   │
│   ├── db/
│   │   ├── database.py
│   │   ├── seed.py
│   │   └── session.py
│   │
│   ├── models/
│   │   ├── submission.py
│   │   ├── tenant.py
│   │   └── widget.py
│   │
│   ├── repositories/
│   │   ├── submission_repository.py
│   │   ├── tenant_repository.py
│   │   └── widget_repository.py
│   │
│   ├── schemas/
│   │   ├── auth.py
│   │   ├── dashboard.py
│   │   ├── submission.py
│   │   ├── tenant.py
│   │   ├── widget.py
│   │   └── widget_config.py
│   │
│   ├── services/
│   │   ├── auth_service.py
│   │   ├── dashboard_service.py
│   │   ├── geo_service.py
│   │   ├── submission_service.py
│   │   ├── widget_config_service.py
│   │   └── widget_service.py
│   │
│   └── workers/
│       └── side_effects.py
│
├── migrations/
│
├── tests/
│
├── widget/
│   └── embed.js
│
├── .env.example
├── .gitignore
├── BUILDLOG.md
├── DESIGN.md
├── EVIDENCE.md
├── Dockerfile
├── README.md
├── capstone.yaml
├── docker-compose.yml
├── pytest.ini
├── requirements.txt
└── alembic.ini
```

## AI Assistance

AI assistance was used during development for:

- Project planning
- Architecture discussion
- Code structure
- Implementation assistance
- Debugging
- Test development
- Documentation drafting

AI-assisted code was reviewed and tested during development.

The implementation was validated using:

```text
pytest -q
```

with the final verified result:

```text
23 passed, 21 warnings in 0.26s
```

Migration consistency was also verified using:

```text
alembic current
alembic check
```

with:

```text
a7f82c05cda9 (head)
No new upgrade operations detected.
```

Further details about AI assistance and development history are documented in `BUILDLOG.md`.

## Final Verification

The final implementation checkpoint was committed and pushed to the project's GitHub repository.

Verified checks:

```text
pytest -q
23 passed, 21 warnings in 0.26s
```

```text
alembic current
a7f82c05cda9 (head)
```

```text
alembic check
No new upgrade operations detected.
```

The project is structured to run locally using Docker Compose with PostgreSQL and FastAPI.