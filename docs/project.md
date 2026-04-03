# Project Documentation — Product Management System

## Overview

This comprehensive Product/Document Management System is built with modern technologies and best practices. It provides a fully functional REST API with async operations, responsive web GUI, MongoDB persistence, Docker containerization, and extensive test coverage for quality assurance.

**Purpose**: Serve as a production-ready inventory/product management backend with an accompanying professional UI, suitable for demonstrations, prototyping, and small-to-medium production deployments.

**Version**: 1.0  
**Last Updated**: April 2, 2026

## Key Features

### Core Functionality
- ✅ Fully async REST API with FastAPI and Motor
- ✅ Complete CRUD operations (Create, Read, Update, Delete)
- ✅ Advanced pagination with configurable limits
- ✅ Multi-column sorting (ascending/descending)
- ✅ Regex-based search across multiple fields
- ✅ Comprehensive error handling with detailed responses
- ✅ Standard HTTP status codes and semantics

### Technology Features
- ✅ MongoDB async database integration
- ✅ Pydantic v2 request/response validation
- ✅ Server-side template rendering with Jinja2
- ✅ Optional Firebase authentication (client-side)
- ✅ Docker & Docker Compose for easy deployment
- ✅ Environment-driven configuration
- ✅ API documentation with Swagger UI & ReDoc

### Quality Assurance
- ✅ Comprehensive pytest test suite
- ✅ Unit tests for models and validation
- ✅ Integration tests for API endpoints
- ✅ CRUD operation tests with mocking
- ✅ Async test support with pytest-asyncio
- ✅ Test fixtures and reusable test utilities

## Tech Stack
- Python 3.12
- FastAPI
- Uvicorn (ASGI server)
- Motor (async MongoDB driver)
- Pydantic (models and validation)
- Jinja2 (templates)
- JavaScript, HTML, CSS for frontend
- MongoDB for persistence
- Docker & Docker Compose for containerization

## Project Structure
- `app/`
  - `main.py` — App startup, router registration, template/static mounting
  - `database.py` — MongoDB client setup (reads `.env` for credentials)
  - `models.py` — Pydantic models (request/response shapes)
  - `crud.py` — Database access functions (create/read/update/delete)
  - `routers/products.py` — API endpoints and input validation
  - `templates/` — Jinja2 HTML templates (including `index.html`)
  - `static/` — CSS and client JS
- `seed_db.py` — Script to seed demo products into MongoDB
- `compose.yml` — Docker Compose configuration for app + MongoDB
- `Dockerfile` — Container build instructions for app service
- `.env` — Environment variables (MONGODB_HOST, DATABASE_NAME, MONGO_INITDB_ROOT_USERNAME, MONGO_INITDB_ROOT_PASSWORD)
- `README.md`, `architecture.md`, `docs/` — Documentation

## Configuration
Set required environment variables in `.env` (or supply via docker-compose):

```
MONGODB_HOST=localhost:27017
DATABASE_NAME=document_management_system
MONGO_INITDB_ROOT_USERNAME=admin
MONGO_INITDB_ROOT_PASSWORD=secret123
```

`app/database.py` reads these variables and constructs an authenticated MongoDB URI.

## Installation & Run (Docker)
1. Build and start services:

```bash
docker compose up --build
```

2. Seed demo data (in another shell):

```bash
uv run python seed_db.py
```

3. Open the GUI: `http://localhost:8000`
4. API docs: `http://localhost:8000/docs`

## Installation & Run (Local)
1. Ensure Python 3.12 is installed.
2. Install dependencies (UV package manager):

```bash
uv sync
```

3. Set `.env` values and run MongoDB locally or via Docker.
4. Seed the DB:

```bash
uv run python seed_db.py
```

5. Start the server:

```bash
uv run uvicorn app.main:app --reload
```

## API Reference (summary)
Base path: `/api/v1/products`

1. Create product
- Method: `POST /api/v1/products/`
- Request body (application/json):
  ```json
  {
    "name": "SSD 1TB",
    "category": "Storage",
    "description": "Fast NVMe SSD",
    "price": 109.99,
    "discount": 10
  }
  ```
- Success Response: `201 Created`
  ```json
  {
    "id": "643...",
    "name": "SSD 1TB",
    "category": "Storage",
    "description": "Fast NVMe SSD",
    "price": 109.99,
    "discount": 10
  }
  ```
- Error Responses:
  - `400 Bad Request` — invalid payload
  - `409 Conflict` — duplicate (if applicable)

2. List products
- Method: `GET /api/v1/products/?skip=0&limit=5&sort_field=name&sort_order=asc`
- Success Response: `200 OK`
  ```json
  {
    "total": 12,
    "skip": 0,
    "limit": 5,
    "products": [ { /* product objects */ } ]
  }
  ```

3. Get single product
- Method: `GET /api/v1/products/{id}`
- Success: `200 OK` with product object
- Not found: `404 Not Found`

4. Update product
- Method: `PUT /api/v1/products/{id}`
- Body: partial or full fields to update
- Success: `200 OK` + updated object
- Errors: `400 Bad Request`, `404 Not Found`

5. Delete product
- Method: `DELETE /api/v1/products/{id}`
- Success: `204 No Content` (or `200 OK` with message if implemented)
- Error: `404 Not Found`

6. Search
- Method: `GET /api/v1/products/search/?q=keyword&field=name`
- Success: `200 OK` + results array

## Error Handling & Response Standard
- Use proper HTTP status codes for each outcome.
- Error body format (JSON):
  ```json
  { "detail": "Description of error" }
  ```
- Common statuses used by the API:
  - `200 OK` — successful read/update
  - `201 Created` — successful create
  - `204 No Content` — successful delete
  - `400 Bad Request` — request validation failed
  - `401 Unauthorized` — authentication required (if added)
  - `403 Forbidden` — authenticated but not allowed
  - `404 Not Found` — resource not found
  - `409 Conflict` — duplicate/conflict
  - `500 Internal Server Error` — unexpected server error

## Sample cURL Requests
Create product:

```bash
curl -X POST "http://localhost:8000/api/v1/products/" \
  -H "Content-Type: application/json" \
  -d '{"name":"SSD 1TB","category":"Storage","description":"Fast NVMe SSD","price":109.99,"discount":10}'
```

List products (paged):

```bash
curl "http://localhost:8000/api/v1/products/?skip=0&limit=5&sort_field=name&sort_order=asc"
```

Get product:

```bash
curl "http://localhost:8000/api/v1/products/<id>"
```

Update product:

```bash
curl -X PUT "http://localhost:8000/api/v1/products/<id>" \
  -H "Content-Type: application/json" \
  -d '{"price":99.99}'
```

Delete product:

```bash
curl -X DELETE "http://localhost:8000/api/v1/products/<id>"
```

## GUI Notes
- The homepage (`/`) contains a `Load Products` button that fetches products client-side.
- Pagination controls are hidden until data is loaded and appear below the table, right-aligned.
- Columns are sortable using small arrow buttons; clicking triggers API requests with `sort_field` and `sort_order`.

## Development & Testing

### Running Tests

The project includes comprehensive test coverage to ensure code quality and functionality:

#### Setup
```bash
uv sync  # Install all dependencies including test packages
```

#### Run All Tests
```bash
pytest
```

#### Run Specific Test Suites
```bash
pytest tests/test_models.py      # Model validation tests
pytest tests/test_crud.py        # CRUD operation tests  
pytest tests/test_api.py         # API endpoint tests
```

#### Run with Verbose Output
```bash
pytest -v
```

#### Generate Coverage Report
```bash
pytest --cov=app --cov-report=html
```

### Test Structure

The test suite is organized into three categories:

**1. Model Validation Tests** (`tests/test_models.py`)
- Pydantic field constraints (required fields, data types)
- Validator functions (URL format, price > 0, discount >= 0)
- Default values and optional fields
- Invalid input handling and error messages
- Edge cases and boundary conditions

**2. CRUD Operation Tests** (`tests/test_crud.py`)
- Create products (auto-generated IDs, custom IDs)
- Read operations (single product, paginated lists, sorting)
- Update products (full updates, partial updates, no-op updates)
- Delete operations (successful deletion, non-existent products)
- Search operations (case-insensitive, multi-field, specific field)
- Full CRUD integration cycle testing

**3. API Endpoint Tests** (`tests/test_api.py`)
- HTTP response status codes
- Request/response validation
- GUI route availability
- Error scenarios and error responses
- Parameter validation
- Edge cases (invalid sort fields, missing query parameters)

### Test Fixtures

Common test fixtures are defined in `conftest.py`:
- `event_loop`: Async event loop management
- `test_db`: Isolated test database collection
- `mock_collection`: Mocked MongoDB collection for CRUD testing
- `async_client`: FastAPI test client for endpoint testing
- `sample_product`: Example product data fixture
- `multiple_sample_products`: Multiple products for batch operation tests

### Running Tests During Development
```bash
# Use local development with test mode
uv run uvicorn app.main:app --reload

# In another terminal
pytest -v --tb=short  # Verbose with short traceback
```

### CI/CD Integration

For continuous integration, ensure:
- All tests pass before merging PRs
- Coverage maintained above threshold
- No warnings or linting errors
- Documentation updated for new features

## Production Guidance (DOs / DON'Ts)
### DOs
- Use environment variables and secret stores for credentials (avoid `.env` in VCS)
- Enable MongoDB authentication and TLS in production
- Run the app behind a reverse proxy (nginx) and use HTTPS
- Monitor metrics and errors (Prometheus + Grafana + Sentry)
- Run periodic DB backups

### DON'Ts
- Don't expose MongoDB directly to the internet without proper firewall/VPC rules
- Don't use weak or default passwords
- Don't run containers as root unless necessary
- Don't skip input validation or error handling

## Extensibility
- Add authentication (JWT) and per-user product scopes
- Add role-based access control
- Add file attachments and object storage integration
- Add CI pipeline (lint/test/build) and automated image publishing

## Contacts & Contribution
- Keep contribution guidelines in a `CONTRIBUTING.md` (not present yet)
- Use branches and PRs for changes; include tests and updated docs

## License
MIT
