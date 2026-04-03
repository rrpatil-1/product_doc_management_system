# Architecture & Design — Product Management System

## Purpose
This document describes the architecture, components, data flow, operational considerations, and extension points for the Product/Document Management System.

## High-level Components

1. Client (Browser / API Consumer)
   - Browser loads HTML pages and fetches JSON endpoints for product data
   - API clients (curl, Postman, mobile apps) call the REST endpoints

2. FastAPI Application (`app/`)
   - Entrypoint: `app/main.py`
   - Responsibilities:
     - Route handling and validation
     - Error handling and HTTP responses
     - Template rendering for the server-side UI
     - Static assets serving

3. Business Logic Layer
   - `routers/products.py` exposes endpoints and maps requests to CRUD operations
   - `models.py` defines Pydantic models and validation
   - `crud.py` implements database interactions

4. Persistence: MongoDB
   - Accessed via Motor (async)
   - Collections: `documents` or `products` (as configured in `database.py`)
   - Indexing: add indexes on `name`, `category`, and any frequently searched fields for performance

5. DevOps / Infrastructure
   - Docker Compose orchestrates `app` and `mongodb` services for local/staging deployments
   - Production should run on orchestrators (Kubernetes, ECS) or managed services

## Data Model (Example)
A product document shape (MongoDB) — fields validated by Pydantic models:

```json
{
  "_id": "ObjectId",
  "name": "SSD 1TB",
  "category": "Storage",
  "description": "Fast NVMe SSD",
  "price": 109.99,
  "discount": 10,
  "created_at": "ISO8601",
  "updated_at": "ISO8601"
}
```

Pydantic models map to API request/response shapes with `id` serialized as string.

## Request / Response Flow

1. Client issues HTTP request (browser or API client).
2. FastAPI receives request and performs parameter/body validation with Pydantic.
3. Router calls into `crud.py` for DB operations.
4. `crud.py` uses Motor to asynchronously query MongoDB.
5. Result is returned to router, converted to response model, and returned to client with appropriate HTTP status code.

## Error Handling
- Use HTTP status codes rigorously and return JSON errors:
  - Validation errors -> `400`
  - Not found -> `404`
  - Permission -> `401`/`403`
  - Conflict -> `409`
  - Server error -> `500`
- Add central exception handlers in `app/main.py` (FastAPI `exception_handler`) to ensure consistent responses.

## Concurrency & Performance
- FastAPI + Uvicorn provides async handling for many concurrent requests.
- Motor (async MongoDB driver) prevents blocking I/O.
- Tune MongoDB connection pool and server resources for production load.
- Use pagination and limit queries to avoid huge payloads.
- Add indexes for frequently sorted/searched fields.

## Scalability
- Horizontal scaling: multiple app replicas behind a load balancer.
- Ensure MongoDB is configured for replication or use a managed cluster for availability and scaling.
- Use a CDN for static assets in high-scale scenarios.

## Security
- Store credentials securely (secrets manager, environment variables). Do not check `.env` into VCS.
- Use TLS for all external traffic and enable TLS for MongoDB connections.
- Add authentication and authorization to APIs before public release.
- Rate-limit endpoints if exposing to untrusted networks.

## Observability & Monitoring
- Logging: structured logs with correlation IDs per request.
- Metrics: export Prometheus metrics for request rates, latencies, DB pool usage.
- Tracing: instrument key flows for distributed tracing (OpenTelemetry)
- Error tracking: Sentry or equivalent for exception aggregation

## Testing & Quality Assurance

### Test Architecture
The test suite is organized in three tiers reflecting the testing pyramid:

#### Unit Tests (60%)
- **Location**: `tests/test_models.py`
- **Focus**: Pydantic model validation
- **Coverage**: 
  - Field constraints (min_length, gt, ge, etc.)
  - Validator functions (URLs, prices)
  - Type enforcement
  - Default values
- **Why**: Fast execution, no external dependencies, easy debugging

#### Integration Tests (30%)
- **Location**: `tests/test_crud.py`
- **Focus**: CRUD operations against test database
- **Coverage**:
  - Create operations (auto ID, custom ID)
  - Read operations (single, list, search)
  - Update operations (full, partial)
  - Delete operations
  - Full CRUD cycles
- **Why**: Verify database interactions, ensure data consistency

#### API/E2E Tests (10%)
- **Location**: `tests/test_api.py`
- **Focus**: HTTP endpoints and response formats
- **Coverage**:
  - Status codes (200, 201, 204, 400, 404, etc.)
  - Request/response validation
  - GUI route availability
  - Error scenarios
- **Why**: Full request-response cycle, ensures API contract

### Test Infrastructure
- **Framework**: pytest with pytest-asyncio
- **Async Support**: @pytest.mark.asyncio for async test functions
- **Fixtures**: Reusable test data and mock objects in `conftest.py`
- **Mocking**: MongoDB collection mocking to avoid test database pollution
- **Coverage**: pytest-cov integration for coverage reports

### Running Tests
```bash
# All tests
pytest

# Specific suite
pytest tests/test_models.py

# With coverage
pytest --cov=app --cov-report=html

# Verbose + show output
pytest -v -s
```

### Continuous Integration
- Run tests on every PR and commit
- Require tests to pass before merge
- Maintain coverage above 80%
- Fail on lint errors

## Backups & Disaster Recovery
- Schedule regular MongoDB backups (snapshots or logical dumps).
- Test restores regularly.
- Consider point-in-time recovery for critical data.

## Deployment Topology (suggested)
- Staging: replicate Docker Compose but with separate DB instance or managed cluster.
- Production: app replicas behind a load balancer; MongoDB replica set or managed service; secure VPC networking.

## Operational Runbook (quick)
- Start service: `docker compose up --build`
- Seed data: `uv run python seed_db.py`
- Check app logs: `docker compose logs -f app`
- Check DB connectivity issues: confirm `MONGODB_HOST` and credentials

## Extension Points
- Add authentication (OAuth2/JWT)
- Add multi-tenant support (owner/organization fields)
- Integrate file storage for attachments
- Add analytics endpoints and dashboards

## Diagram (textual)
Client -> Load balancer -> App replicas -> MongoDB replica set

## Notes & Recommendations
- Use connection strings with credentials: `mongodb://<user>:<pass>@host:port` and prefer SRV format for cloud providers.
- Keep models strictly validated and make optional fields explicit.
- Move business logic into service layer for complex rules (avoid controllers becoming fat).

## Conclusion
The application is intentionally minimal and modular: swapping components (e.g., DB, auth) is straightforward. Follow DOs/DON'Ts in docs for safe production operation.  

