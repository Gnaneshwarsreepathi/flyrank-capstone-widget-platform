# EVIDENCE

## 1. Widget Management

Status: Complete

Evidence:
- Tenant-authenticated widget CRUD endpoints are implemented under `/widgets`.
- Widget records are isolated by `tenant_id`.
- Widget creation, retrieval, update and deletion are implemented.
- Widget updates increment the widget `version`.
- Automated tests cover widget creation, retrieval, update, deletion and tenant isolation.
- Test result: `3 passed` for `tests/test_widgets.py`.

## 2. Embed Snippet

Status: Complete

Evidence:
- Embeddable JavaScript is provided at `/widget/embed.js`.
- The embed script loads the public widget configuration.
- The script dynamically renders the configured lead-capture form.
- Form submission uses the public submission API.
- The embed script generates an `Idempotency-Key` for submissions.
- The honeypot field is included in the client-side form but excluded from the submitted payload.

## 3. Cached Widget Delivery

Status: Complete

Evidence:
- Public widget configuration is available through:
  `/widgets/{widget_id}/config`
- Public configuration responses include an `ETag`.
- The ETag is derived from the widget ID and version.
- Responses include:
  `Cache-Control: public, max-age=60, must-revalidate`
- Matching `If-None-Match` requests return HTTP `304 Not Modified`.
- Widget configuration is available without tenant authentication.

## 4. Public Submission API

Status: Complete

Evidence:
- Public submissions are handled by `/submissions`.
- Active widgets are validated before accepting submissions.
- Submission payloads are validated using Pydantic.
- Idempotency is enforced using the `Idempotency-Key` header.
- Submission persistence uses PostgreSQL through SQLAlchemy.
- Submission records store widget, tenant, payload, IP address and geo-enrichment fields.
- Duplicate idempotency keys return the existing submission rather than creating another record.
- Automated submission tests are included in `tests/test_submissions.py`.

## 5. Abuse Protection

Status: Complete

Evidence:
- Public submission rate limiting is implemented with SlowAPI.
- The submission endpoint is limited to 5 requests per minute per client address.
- Oversized HTTP requests are rejected using a 64 KiB request-size boundary.
- Payload validation limits the number of fields and field/value sizes.
- Idempotency keys are required and length-limited.
- Honeypot submissions are rejected.
- Automated tests cover rate limiting and validation behaviour.

## 6. Geo Enrichment & Safe Side Effects

Status: Complete

Evidence:
- IP-based geo enrichment is implemented in `app/services/geo_service.py`.
- Provider A is attempted first.
- Provider B is used as a fallback when Provider A fails.
- If both providers fail, the submission can still be stored with unavailable geo fields.
- Geo provider behaviour is covered by `tests/test_geo_service.py`.
- Email and webhook side effects are separated from submission persistence.
- Side-effect failures are caught and logged instead of causing the stored submission to fail.
- Webhook delivery is performed as a background task after successful persistence.
- Safe side-effect behaviour is covered by `tests/test_side_effects.py`.

## 7. Dashboard API

Status: Complete

Evidence:
- Tenant-authenticated dashboard endpoint is available at `/dashboard`.
- Dashboard data is scoped to the authenticated tenant.
- The dashboard returns total submission count and submission records.
- A configurable result limit is supported.
- Automated dashboard tests are included in `tests/test_dashboard.py`.

# Shared Requirements

## Layered Architecture

Status: Complete

Evidence:
- HTTP/API routes are separated under `app/api`.
- Business logic is separated under `app/services`.
- Data access is separated under `app/repositories`.
- Database models are separated under `app/models`.
- Request/response schemas are separated under `app/schemas`.
- Authentication and application configuration are separated under `app/core`.
- Background side-effect handling is separated under `app/workers`.

## Boundary Validation

Status: Complete

Evidence:
- Pydantic schemas validate authentication, widget and submission requests.
- Submission payloads enforce field-count and field-size limits.
- Widget fields have length and type validation.
- Invalid or oversized requests are rejected with 4xx responses.

## Background Job

Status: Complete

Evidence:
- Submission side effects are dispatched using FastAPI `BackgroundTasks`.
- Email/webhook failures are isolated from the primary submission persistence path.
- The submission is committed before side effects are dispatched.

## Real Persistence and Migrations

Status: Complete

Evidence:
- PostgreSQL is used for persistent application data.
- SQLAlchemy models define tenants, widgets and submissions.
- Alembic migrations create and evolve the database schema.
- Current migration:
  `a7f82c05cda9 (head)`
- `alembic check` result:
  `No new upgrade operations detected.`

## Idempotency

Status: Complete

Evidence:
- Public submissions require an `Idempotency-Key`.
- A database-level unique constraint exists on:
  `widget_id + idempotency_key`
- Duplicate submission requests reuse the existing stored submission.
- Idempotency behaviour is covered by submission tests.

## Secrets

Status: Complete

Evidence:
- Local secrets are stored in `.env`.
- `.env` is excluded through `.gitignore`.
- `.env.example` documents the required environment variables.
- No real credentials are included in the repository.

# Acceptance Probe Evidence

## Valid Cross-Origin Submission

Status: Complete

Evidence:
- CORS middleware is configured in the FastAPI application.
- The configured development origins include `http://localhost:8000` and `http://localhost:5500`.
- The public submission endpoint is available without tenant authentication.
- Submission tests verify successful public submission behaviour.

## Invalid or Oversized Request

Status: Complete

Evidence:
- Request-size middleware rejects requests exceeding 64 KiB with HTTP 413.
- Pydantic submission validation rejects oversized payload fields and excessive field counts.
- Invalid request data produces HTTP 4xx responses.

## Burst Requests / Rate Limiting

Status: Complete

Evidence:
- SlowAPI rate limiting is applied to the public submission endpoint.
- Limit configured:
  `5/minute`
- Automated rate-limit tests are included in `tests/test_rate_limit.py`.
- Rate-limit state is reset between automated tests.

## Geo Provider A Failure

Status: Complete

Evidence:
- Geo enrichment attempts Provider A first.
- Provider A failure triggers Provider B fallback.
- Automated test coverage is included in `tests/test_geo_service.py`.
- Test suite result includes successful geo fallback tests.

## Both Geo Providers Failure

Status: Complete

Evidence:
- If Provider A and Provider B both fail, geo enrichment returns unavailable location values rather than raising an error.
- Submission processing continues without requiring successful geo enrichment.
- Geo failure behaviour is covered by the geo service tests.

## Email/Webhook Failure

Status: Complete

Evidence:
- Email and webhook failures are caught and logged.
- Side effects do not replace or roll back the primary database persistence path.
- Webhook delivery is configured through `WEBHOOK_URL`.
- Automated safe-side-effect tests are included in `tests/test_side_effects.py`.

## Honeypot Spam

Status: Complete

Evidence:
- Public submissions include a honeypot field.
- Non-empty honeypot values are rejected as spam.
- The embed script includes the honeypot field while keeping it out of the normal submission payload.
- Honeypot behaviour is covered by submission tests.

# Automated Test Summary

Command:

```text
pytest -q