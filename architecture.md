# Architecture Overview

## 1. System Context

This project is a document/product management application built on FastAPI and MongoDB. It provides:
- REST API endpoints for CRUD operations
- Web GUI using server-rendered templates (Jinja2) and frontend JavaScript
- Dockerized deployment with MongoDB service

Users interact with:
- Web UI at `/` for product listing, create, update, delete, and search
- REST API at `/api/v1/products` for programmatic access

## 2. Component Diagram

1. **Client (Browser / API client)**
   - Sends HTTP requests
   - Receives HTML or JSON responses

2. **FastAPI App** (`app/main.py`)
   - Defines endpoints and error handlers
   - Serves static files and templates
   - Wires routers from `app/routers/products.py`

3. **Data Layer**
   - `app/database.py` handles MongoDB connection using credentials from `.env`
   - `app/crud.py` provides db operations (create/read/update/delete)
   - `app/models.py` contains Pydantic model validation

4. **MongoDB**
   - Stores `products` collection
   - Access via Motor async client

## 3. Request Flow (API)

### Create Product
1. `POST /api/v1/products/` with JSON payload
2. FastAPI receives and validates payload with Pydantic model (`ProductCreate`)
3. `crud.create_product` writes to MongoDB
4. Returns `201 Created` + JSON of created document

### Get Products
1. `GET /api/v1/products/?skip=0&limit=5&sort_field=name&sort_order=asc`
2. FastAPI reads query params
3. `crud.get_products` performs Mongo query with pagination/sorting
4. Returns `200 OK` + list + `total`

### Read By ID
- `GET /api/v1/products/{id}`
- `404` when not found

### Update
- `PUT /api/v1/products/{id}` with JSON updates
- `200 OK` if success
- `404` or `400` on error

### Delete
- `DELETE /api/v1/products/{id}`
- `204 No Content` or `404` if missing

## 4. Web UI Flow
- `/` renders product inventory page
- `Load Products` triggers client-side fetch to `GET /api/v1/products/`
- Sorting is UI-side by clicking column arrows (calls API with query params)
- Pagination controls managed client-side and updated per API responses

## 5. Environment & Deployment

### Local dev
- `.env` contains:
  - `MONGODB_HOST`, `DATABASE_NAME`, `MONGO_INITDB_ROOT_USERNAME`, `MONGO_INITDB_ROOT_PASSWORD`
- Run:
  - `uv sync`
  - `uv run uvicorn app.main:app --reload`

### Docker compose
- `compose.yml` declares
  - `app` service (FastAPI)
  - `mongodb` service (authenticated MongoDB)
- Use `docker compose up --build`

## 6. DOs and DON'Ts

### DO
- Use strong env passwords and secrets
- Enable TLS for production MongoDB
- Use schema validation in models
- Monitor DB connection and app health

### DON'T
- Expose DB without auth
- Use root user in production
- Skip data validation or catch exceptions
- Keep static HTML response-only without API fallback for errors

## 7. Extension Points

- Add user authentication (JWT/OAuth)
- Add rate limiting and request throttling
- Add transaction support, audit logs, soft deletes
- Add CI/CD pipeline (build/test/deploy) with container scanning
