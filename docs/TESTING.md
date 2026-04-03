# Testing Guide — Product Management System

## Overview

This document provides comprehensive guidance on testing the Product Management System. The project includes unit tests, integration tests, and end-to-end tests using pytest and pytest-asyncio.

## Test Organization

```
tests/
├── conftest.py          # Pytest configuration and shared fixtures
├── test_models.py       # Model validation tests
├── test_crud.py         # CRUD operation tests
└── test_api.py          # API endpoint tests
```

## Quick Start

### Install Test Dependencies

Test dependencies are included in `requirements.txt`:

```bash
uv sync
```

### Run Tests

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_models.py

# Run specific test class
pytest tests/test_crud.py::TestCreateProduct

# Run specific test function
pytest tests/test_api.py::test_create_product_success

# Stop on first failure
pytest -x

# Show print statements
pytest -s

# Generate coverage report
pytest --cov=app --cov-report=html
```

## Test Suites

### 1. Model Validation Tests (`test_models.py`)

Tests Pydantic model validation, field constraints, and error handling.

#### Test Classes

**TestProductCreate**
- Valid product creation with all fields
- Custom ID assignment
- Missing required fields
- Empty strings for required fields
- Invalid price (zero or negative)
- Negative discount
- Invalid URLs
- Valid HTTP/HTTPS URLs
- None URL handling

```bash
pytest tests/test_models.py::TestProductCreate -v
```

**TestProductUpdate**
- Update all fields
- Update partial fields
- Empty update object
- Invalid price
- Invalid discount
- Invalid URL
- Empty string URL handling

```bash
pytest tests/test_models.py::TestProductUpdate -v
```

**TestProductInDB**
- Product creation
- Product without thumbnail

**TestPaginatedProducts**
- Paginated response with products
- Empty paginated response

**TestErrorResponse**
- Error response creation
- Error response with details

#### Running Model Tests

```bash
# All model tests
pytest tests/test_models.py

# Specific test class
pytest tests/test_models.py::TestProductCreate

# Specific test
pytest tests/test_models.py::TestProductCreate::test_create_valid_product -v
```

### 2. CRUD Operation Tests (`test_crud.py`)

Tests database operations: create, read, update, delete, search.

#### Setup

These tests use pytest fixtures for database mocking:
- `test_db`: Isolated test database collection
- `mock_collection`: Mocked MongoDB collection

#### Test Classes

**TestCreateProduct**
- Auto-generated IDs
- Custom IDs
- Minimal required fields

```bash
pytest tests/test_crud.py::TestCreateProduct -v
```

**TestReadProducts**
- Get count from empty collection
- Get products from empty collection
- Get products with sorting
- Get product by ID (not found, found)

```bash
pytest tests/test_crud.py::TestReadProducts -v
```

**TestUpdateProduct**
- Update non-existent product
- Update all fields
- Update partial fields
- Empty update

```bash
pytest tests/test_crud.py::TestUpdateProduct -v
```

**TestDeleteProduct**
- Delete non-existent product
- Successful deletion

```bash
pytest tests/test_crud.py::TestDeleteProduct -v
```

**TestSearchProducts**
- Search empty collection
- Search by name
- Search by category
- Search by description
- Case-insensitive search
- Multiple fields without specifying one

```bash
pytest tests/test_crud.py::TestSearchProducts -v
```

**TestCRUDIntegration**
- Full CRUD cycle: create → read → update → delete

```bash
pytest tests/test_crud.py::TestCRUDIntegration::test_full_crud_cycle -v
```

#### Running CRUD Tests

```bash
# All CRUD tests
pytest tests/test_crud.py

# Specific operation tests
pytest tests/test_crud.py::TestCreateProduct
pytest tests/test_crud.py::TestUpdateProduct

# Integration tests only
pytest tests/test_crud.py::TestCRUDIntegration
```

### 3. API Endpoint Tests (`test_api.py`)

Tests HTTP endpoints, status codes, and response formats.

#### Setup

Uses `async_client` fixture (AsyncClient from httpx) for testing FastAPI endpoints.

#### Test Classes

**TestProductEndpoints**
- Create product (success, custom ID, validation errors)
- List products (default params, skip/limit, invalid sort)
- Get product (not found)
- Search products (missing query, with query, invalid field)
- Update product (not found, invalid price)
- Delete product (not found)

```bash
pytest tests/test_api.py::TestProductEndpoints -v
```

**TestGUIRoutes**
- Home page (`/`)
- Create page (`/create`)
- Search page (`/search`)
- Login page (`/login`)
- Update page (`/update/{product_id}`)

```bash
pytest tests/test_api.py::TestGUIRoutes -v
```

**TestErrorHandling**
- Invalid JSON body
- API response format
- Invalid HTTP methods

```bash
pytest tests/test_api.py::TestErrorHandling -v
```

#### Running API Tests

```bash
# All API tests
pytest tests/test_api.py

# Specific endpoint tests
pytest tests/test_api.py::TestProductEndpoints

# GUI route tests
pytest tests/test_api.py::TestGUIRoutes

# Error handling tests
pytest tests/test_api.py::TestErrorHandling
```

## Test Fixtures

Fixtures are defined in `conftest.py` and provide reusable test data and context.

### Common Fixtures

**event_loop**
- Scope: session
- Purpose: Async event loop for test session
- Usage: Automatic (provided by pytest-asyncio)

**test_db**
- Scope: function
- Purpose: Isolated test database collection
- Cleanup: Drops collection after each test
- Usage: Pass to test function parameter

```python
async def test_example(test_db):
    await test_db.insert_one({"name": "test"})
```

**mock_collection**
- Scope: function
- Purpose: Mocked MongoDB collection for CRUD testing
- Patches: `app.crud.collection` with test collection
- Cleanup: Restores original collection
- Usage: Pass to test function parameter

```python
async def test_create_product(mock_collection):
    product = await create_product(...)
    assert product.id is not None
```

**async_client**
- Scope: function
- Purpose: FastAPI test client for endpoint testing
- Usage: Pass to test function parameter

```python
async def test_api_endpoint(async_client):
    response = await async_client.get("/api/v1/products/")
    assert response.status_code == 200
```

**sample_product**
- Scope: function
- Purpose: Example product data
- Usage: Pass to test function parameter

```python
async def test_with_sample(sample_product):
    assert sample_product["name"] == "Test Product"
```

**multiple_sample_products**
- Scope: function
- Purpose: Multiple products for batch testing
- Usage: Pass to test function parameter

```python
async def test_with_products(multiple_sample_products):
    assert len(multiple_sample_products) == 3
```

## Writing New Tests

### Adding a New Unit Test

1. **Identify the component** to test (model, CRUD, or API)
2. **Choose the appropriate file** (test_models.py, test_crud.py, or test_api.py)
3. **Create a test class** if it doesn't exist:

```python
class TestNewFeature:
    """Tests for new feature."""
    
    def test_specific_behavior(self):
        """Test description."""
        # Arrange
        data = {"field": "value"}
        
        # Act
        result = some_function(data)
        
        # Assert
        assert result == expected_value
```

4. **Follow naming conventions**:
   - Test files: `test_*.py`
   - Test classes: `Test*`
   - Test functions: `test_*`

5. **Write descriptive docstrings**:

```python
def test_create_product_with_custom_id(self):
    """Test creating a product with user-provided ID."""
    # test body
```

### Adding an Async Test

Use `@pytest.mark.asyncio` decorator:

```python
@pytest.mark.asyncio
async def test_async_operation(self, mock_collection):
    """Test async CRUD operation."""
    product = await create_product(...)
    assert product.id is not None
```

### Using Fixtures in Tests

Pass fixture names as function parameters:

```python
async def test_with_fixtures(self, mock_collection, async_client, sample_product):
    """Test using multiple fixtures."""
    # mock_collection is available in test
    # async_client is available for endpoint testing
    # sample_product contains example data
```

### Testing Error Conditions

```python
def test_example_raises_validation_error(self):
    """Test that invalid input raises ValidationError."""
    with pytest.raises(ValidationError) as exc_info:
        ProductCreate(price=-50.00)  # Invalid
    
    assert "greater than 0" in str(exc_info.value).lower()
```

## Test Configuration

Configuration is defined in `pytest.ini`:

```ini
[pytest]
asyncio_mode = auto
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
markers =
    asyncio: marks tests as async
```

## Coverage Reports

Generate an HTML coverage report:

```bash
pytest --cov=app --cov-report=html
```

This creates `htmlcov/index.html` with detailed coverage information.

### Coverage Targets
- **Minimum**: 80%
- **Target**: 90%+
- **Critical paths**: 100% (CRUD, validation, error handling)

View report:
```bash
# Open in browser
open htmlcov/index.html  # macOS
explorer htmlcov\index.html  # Windows
xdg-open htmlcov/index.html  # Linux
```

## Debugging Tests

### Run with Print Output

```bash
pytest -s  # Show print() statements
```

### Run with Detailed Output

```bash
pytest -vv  # Very verbose
pytest --tb=short  # Shorter traceback
pytest --tb=long  # Longer traceback
```

### Run Single Test

```bash
pytest tests/test_models.py::TestProductCreate::test_create_valid_product -v -s
```

### Drop into Debugger

Add breakpoint in test:

```python
def test_example(self):
    data = {"field": "value"}
    breakpoint()  # Execution stops here
    result = process(data)
```

Then run with:
```bash
pytest tests/test_models.py::test_example -s
```

## Common Issues & Solutions

### Issue: Tests fail with "MongoDB connection error"

**Solution**:
1. Ensure MongoDB is running
2. Check `.env` configuration
3. Verify `conftest.py` test_db setup

### Issue: Async tests fail with "RuntimeError: no running event loop"

**Solution**:
1. Ensure test is decorated with `@pytest.mark.asyncio`
2. Check `pytest.ini` has `asyncio_mode = auto`
3. Verify pytest-asyncio is installed: `pip show pytest-asyncio`

### Issue: Fixture not found error

**Solution**:
1. Check fixture is defined in `conftest.py`
2. Verify spelling matches fixture name
3. Place `conftest.py` in `tests/` directory

### Issue: Tests modify database

**Solution**:
1. Use `mock_collection` fixture instead of real collection
2. Ensure cleanup happens (test_db fixture drops collection)
3. Use test database instance, not production database

## Best Practices

✅ **DO:**
- Write descriptive test names
- Use fixtures for common setup
- Test one behavior per test
- Use `@pytest.mark.asyncio` for async tests
- Keep tests isolated (no dependencies between tests)
- Mock external dependencies
- Include error/edge case tests
- Update tests when code changes

❌ **DON'T:**
- Use global state in tests
- Make tests depend on execution order
- Use real database in tests (use mocks/fixtures)
- Skip error scenarios
- Write tests that are too broad
- Ignore test failures
- Leave debugging code (breakpoint(), print())

## Continuous Integration

For GitHub Actions or similar CI systems:

```yaml
- name: Run Tests
  run: pytest --cov=app --cov-report=xml

- name: Upload Coverage
  uses: codecov/codecov-action@v3
  with:
    files: ./coverage.xml
```

## Further Reading

- [pytest Documentation](https://docs.pytest.org/)
- [pytest-asyncio](https://pytest-asyncio.readthedocs.io/)
- [httpx Testing](https://www.python-httpx.org/async/#async-context-managers-and-client-instances)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)

---

**Last Updated**: April 2, 2026
