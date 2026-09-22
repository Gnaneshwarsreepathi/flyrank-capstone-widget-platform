# FlyRank Capstone — Embeddable Widget & Lead-Capture Platform

## 1. Problem

The platform allows a customer to create an embeddable lead-capture widget
and install it on an external website using a JavaScript script tag.

Visitors can submit information through the widget. The backend validates,
protects, enriches and stores submissions, while the widget owner can access
their submissions and basic analytics.

## 2. Technology Stack

- Python
- FastAPI
- PostgreSQL
- SQLAlchemy
- Alembic
- Docker
- Docker Compose
- HTML
- JavaScript
- Pytest

## 3. Main Actors

### Widget Owner

An authenticated customer who can:

- Create widgets
- View widgets
- Update widgets
- Delete widgets
- View submissions
- View basic statistics

### Website Visitor

An unauthenticated visitor who can:

- Load a public widget
- Submit the widget form

## 4. Core Data Model

### Tenant

Represents a customer account.

Fields:

- id
- name
- email
- password_hash
- created_at

### Widget

Represents an embeddable widget owned by a tenant.

Fields:

- id
- tenant_id
- type
- title
- description
- fields
- button_text
- display_options
- version
- created_at
- updated_at

### Submission

Represents data submitted by a website visitor.

Fields:

- id
- widget_id
- tenant_id
- idempotency_key
- payload
- ip_address
- country
- city
- created_at

## 5. Tenant Isolation

Every widget and submission belongs to a tenant.

Authenticated APIs will identify the current tenant and every database query
will enforce tenant ownership.

Tenant A must never be able to read, update or delete Tenant B's widgets or
submissions.

## 6. Request Flows

### Owner Flow

Owner
→ Authentication
→ Widget Management API
→ Database
→ Embed Snippet

### Widget Loading Flow

Customer Website
→ widget.v1.js
→ Public Widget Config API
→ Render Widget

### Visitor Submission Flow

Website Visitor
→ Public Submission API
→ Validation
→ CORS
→ Rate Limit
→ Spam Protection
→ Geo Enrichment
→ Database
→ Background Side Effect

### Dashboard Flow

Widget Owner
→ Authenticated Dashboard API
→ Submission Data
→ Statistics

## 7. Public Submission Protection

The public submission endpoint will implement:

- Boundary validation
- Payload size validation
- CORS
- Rate limiting
- Honeypot spam protection
- Correct HTTP status codes
- Idempotency

Invalid requests will return appropriate 4xx responses.

Rate-limited requests will return HTTP 429.

## 8. Geo Enrichment

The submission IP address will be enriched using:

Provider A
→ if unavailable
→ Provider B
→ if both unavailable
→ store submission without geo information

Geo provider failure must never prevent a valid submission from being stored.

## 9. Safe Side Effects

After storing a submission, a background operation will perform the
confirmation email/webhook side effect.

If the side effect fails, the original submission must remain successfully
stored.

## 10. Caching

The public widget configuration endpoint will use HTTP Cache-Control headers.

The widget JavaScript will be served as a versioned asset.

Example:

    /widget.v1.js

A future release can use:

    /widget.v2.js

## 11. Explicit Non-Goal

This project will not implement a full visual form-builder interface.

The widget configuration will be managed through the backend API.

The focus is backend architecture, security, resilience and API behaviour.

## 12. Success Criteria

The project is considered complete when:

- Authenticated widget CRUD works
- Tenant isolation is demonstrated
- Embed snippet is generated
- Widget JavaScript loads
- Widget config is cached
- Cross-origin submissions work
- Invalid input returns 4xx
- Rate limiting returns 429
- Honeypot blocks spam
- Geo fallback works
- Submission succeeds when geo providers fail
- Side-effect failure does not fail the submission
- Dashboard APIs expose submissions and statistics
- Required documentation and evidence are included