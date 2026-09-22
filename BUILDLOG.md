# BUILDLOG

## 2026-09-22

### Project setup

- Created a dedicated public GitHub repository for the FlyRank Backend Internship Capstone.
- Selected Python and FastAPI for the backend.
- Selected PostgreSQL for persistent storage.
- Added Docker and Docker Compose for local development.
- Designed a layered architecture separating API routes, services, repositories, models and schemas.
- Added environment configuration through `.env.example`.
- Added database migrations using Alembic.
- Added automated testing with pytest.

### Backend implementation

- Implemented tenant registration and authentication using JWT.
- Added password hashing and authentication dependencies.
- Implemented tenant-scoped widget CRUD operations.
- Added widget versioning.
- Implemented public widget configuration delivery.
- Added ETag-based conditional caching for widget configuration.
- Added the embeddable JavaScript widget.
- Added public lead submission handling.
- Added submission persistence in PostgreSQL.
- Added database-level idempotency using `widget_id` and `idempotency_key`.
- Added request and payload validation.
- Added request-size protection.
- Added public submission rate limiting.
- Added honeypot spam protection.

### Geo enrichment

- Implemented IP-based geo enrichment.
- Added Provider A as the primary geo provider.
- Added Provider B as the fallback provider.
- Ensured geo-provider failures do not prevent submission persistence.

### Side effects

- Added background processing for submission side effects.
- Added webhook delivery support.
- Added email-side-effect handling.
- Ensured webhook/email failures are caught and logged without blocking the primary submission persistence flow.

### Dashboard

- Implemented a tenant-authenticated dashboard endpoint.
- Added total submission counts.
- Added tenant-scoped submission listing.
- Added configurable dashboard result limits.

### Database and migrations

- Created PostgreSQL database models for:
  - tenants
  - widgets
  - submissions
- Added Alembic migrations.
- Added a database uniqueness constraint for submission idempotency.
- Verified the migration state with:

```text
a7f82c05cda9 (head)
No new upgrade operations detected.
```

### Automated testing

The project includes automated tests covering:

- health endpoint
- widget CRUD
- widget tenant isolation
- public widget configuration
- widget caching and ETag behaviour
- public submissions
- submission validation
- idempotency
- rate limiting
- geo-provider fallback
- safe side effects
- dashboard behaviour

Final test command:

```text
pytest -q
```

Final result:

```text
23 passed, 21 warnings in 0.26s
```

The warnings were dependency/runtime deprecation warnings and did not cause test failures.

### Documentation

- Added `DESIGN.md` describing the architecture, actors, data model, request flows, protection mechanisms and non-goals.
- Added `EVIDENCE.md` documenting implementation and acceptance-probe evidence.
- Added `.env.example` for environment configuration.
- Updated project documentation to describe setup, testing and architecture.

### AI assistance

AI assistance was used during development for:

- project planning
- architecture discussion
- code structure
- implementation assistance
- debugging
- test development
- documentation drafting

AI-generated or AI-assisted code was reviewed and tested during development. The implementation was manually validated through automated tests, migration checks and application-level verification.

The use of AI assistance is documented here as part of the project build history.

### Final status

Implementation and automated test suite completed.

Final verification:

- `pytest -q` → **23 passed**
- `alembic current` → **a7f82c05cda9 (head)**
- `alembic check` → **No new upgrade operations detected**
- Implementation checkpoint pushed to GitHub.
