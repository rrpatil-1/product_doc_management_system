# Contributing Guide — Product Management System

Thank you for contributing to the Product Management System! This guide explains how to set up your development environment, follow our coding standards, and contribute effectively.

## Table of Contents

1. [Getting Started](#getting-started)
2. [Development Environment](#development-environment)
3. [Project Structure](#project-structure)
4. [Coding Standards](#coding-standards)
5. [Testing](#testing)
6. [Git Workflow](#git-workflow)
7. [Pull Request Process](#pull-request-process)
8. [Writing Documentation](#writing-documentation)
9. [Common Tasks](#common-tasks)
10. [Troubleshooting](#troubleshooting)

---

## Getting Started

### Prerequisites

- Python 3.12+
- Git
- Docker and Docker Compose
- MongoDB knowledge (basic)
- VS Code or preferred IDE

### Initial Setup (5 minutes)

```bash
# 1. Clone repository
git clone <repo-url>
cd Doc_Management_System

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt  # Development dependencies

# 4. Set up environment
cp .env.example .env
# Edit .env with your settings

# 5. Start services
docker-compose up -d

# 6. Run tests
pytest

# 7. Start development server
uvicorn app.main:app --reload
```

### Verify Installation

```bash
# Check Python version
python --version  # Should be 3.12+

# Check MongoDB connection
python -c "from app.database import get_db_connection; print('✓ DB connection OK')"

# Run quick test
pytest tests/test_api.py::TestProductEndpoints::test_create_product -v

# Check API
curl http://localhost:8000/docs  # Should show Swagger UI
```

---

## Development Environment

### VS Code Extensions (Recommended)

Install these extensions for optimal development:

```json
{
  "recommendations": [
    "ms-python.python",
    "ms-python.vscode-pylance",
    "ms-python.black-formatter",
    "charliermarsh.ruff",
    "ms-python.flake8",
    "ms-python.pylint",
    "ms-python.pytest",
    "eamodio.gitlens",
    "GitHub.copilot"
  ]
}
```

### VS Code Settings

Create `.vscode/settings.json`:

```json
{
  "[python]": {
    "editor.formatOnSave": true,
    "editor.defaultFormatter": "ms-python.black-formatter",
    "editor.codeActionsOnSave": {
      "source.organizeImports": "explicit"
    }
  },
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": true,
  "python.testing.pytestEnabled": true,
  "python.testing.pytestArgs": [
    "tests"
  ]
}
```

### Development Commands

```bash
# Format code
black app/ tests/

# Sort imports
isort app/ tests/

# Lint code
pylint app/
flake8 app/
ruff check app/

# Type checking
mypy app/

# All checks at once
make lint  # If Makefile exists
```

### Environment Variables for Development

`.env.development`:
```bash
ENVIRONMENT=development
DEBUG=True
LOG_LEVEL=DEBUG
DATABASE_URL=mongodb://admin:secret123@mongo:27017/product_db
PYTHONUNBUFFERED=1
```

---

## Project Structure

Understanding the directory layout:

```
Doc_Management_System/
├── app/                      # Main application
│   ├── __init__.py
│   ├── main.py              # FastAPI app initialization
│   ├── database.py          # MongoDB connection
│   ├── models.py            # Pydantic models
│   ├── crud.py              # Database operations
│   ├── routers/
│   │   ├── products.py      # Product API routes
│   │   └── gui.py           # Web UI routes
│   └── templates/           # Jinja2 templates
│       ├── base.html
│       ├── index.html
│       ├── create.html
│       └── update.html
├── tests/                    # Test suite
│   ├── __init__.py
│   ├── conftest.py          # Pytest configuration & fixtures
│   ├── test_models.py       # Model validation tests
│   ├── test_crud.py         # CRUD operation tests
│   └── test_api.py          # API endpoint tests
├── docs/                     # Documentation
│   ├── API_REFERENCE.md     # API documentation
│   ├── DEPLOYMENT.md        # Deployment guide
│   ├── TESTING.md           # Testing guide
│   ├── CONTRIBUTING.md      # This file
│   ├── arch.md              # Architecture
│   └── project.md           # Project details
├── docker-compose.yml       # Multi-container setup
├── Dockerfile               # Container image
├── requirements.txt         # Production dependencies
├── requirements-dev.txt     # Development dependencies
├── pytest.ini              # Pytest configuration
├── .env.example            # Environment template
├── .gitignore              # Git ignore rules
└── README.md               # README
```

---

## Coding Standards

### Python Style Guide

Follow **PEP 8** with these specific rules:

```python
# ✓ Good
def create_product(name: str, price: float) -> ProductInDB:
    """Create a new product.
    
    Args:
        name: Product name
        price: Product price in USD
        
    Returns:
        Created product document
    """
    pass

# ✗ Bad
def create_product(name,price):
    # no docstring, no type hints
    pass
```

### Type Hints

Always use type hints:

```python
from typing import Optional, List, Dict, Tuple

# ✓ Good
async def search_products(
    query: str,
    limit: int = 10
) -> List[ProductInDB]:
    """Search products by query."""
    pass

# ✗ Bad
async def search_products(query, limit=10):
    """Search products by query."""
    pass
```

### Docstring Format

Use Google-style docstrings:

```python
def calculate_discount(price: float, discount_percent: float) -> float:
    """Calculate final price after discount.
    
    Args:
        price: Base price in USD
        discount_percent: Discount percentage (0-100)
        
    Returns:
        Final price after discount
        
    Raises:
        ValueError: If price is negative or discount is out of range
        
    Examples:
        >>> calculate_discount(100.0, 10.0)
        90.0
    """
    if price < 0:
        raise ValueError("Price cannot be negative")
    if not 0 <= discount_percent <= 100:
        raise ValueError("Discount must be between 0-100")
    return price * (1 - discount_percent / 100)
```

### Naming Conventions

```python
# Constants
MAX_PRODUCTS_PER_PAGE = 100
DATABASE_CONNECTION_TIMEOUT = 30

# Variables and functions (snake_case)
product_name = ""
def get_product_by_id():
    pass

# Classes (PascalCase)
class ProductInDB:
    pass

class ProductController:
    pass

# Private methods (leading underscore)
def _parse_query_string(query: str) -> Dict:
    pass
```

### Import Organization

```python
# Standard library
import os
import json
from pathlib import Path
from typing import Optional, List

# Third-party
from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

# Local imports
from app.database import get_db_connection
from app.models import ProductCreate
```

### Error Handling

```python
# ✓ Good
async def get_product(product_id: str) -> ProductInDB:
    """Get product by ID.
    
    Raises:
        HTTPException(404): Product not found
    """
    try:
        product = await db.find_one({"_id": product_id})
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        return ProductInDB(**product)
    except Exception as e:
        logger.error(f"Error retrieving product {product_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

# ✗ Bad
def get_product(product_id):
    product = db.find_one(product_id)  # Silent failure
    return product
```

---

## Testing

### Testing Philosophy

- Write tests as you code
- Aim for >80% code coverage
- Test happy path AND edge cases
- Use fixtures for common data

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_models.py

# Run specific test class
pytest tests/test_api.py::TestProductEndpoints

# Run specific test
pytest tests/test_api.py::TestProductEndpoints::test_create_product

# Verbose output
pytest -v

# Show print statements
pytest -s

# Stop on first failure
pytest -x

# Show slowest tests
pytest --durations=10

# Coverage report
pytest --cov=app --cov-report=html
# Open htmlcov/index.html in browser
```

### Writing Tests

```python
# tests/test_example.py
import pytest
from app.models import ProductCreate
from app.crud import create_product

class TestExample:
    """Test example functionality."""
    
    @pytest.mark.asyncio
    async def test_create_product_success(self, mock_collection):
        """Test successful product creation."""
        # Arrange
        product_data = ProductCreate(
            name="Test Product",
            category="Test",
            description="Test description",
            price=99.99
        )
        
        # Act
        result = await create_product(product_data)
        
        # Assert
        assert result.id is not None
        assert result.name == "Test Product"
        assert result.price == 99.99
    
    @pytest.mark.asyncio
    async def test_create_product_invalid_price(self, mock_collection):
        """Test product creation with invalid price."""
        with pytest.raises(ValueError):
            ProductCreate(
                name="Test",
                category="Test",
                description="Test",
                price=-10.00  # Invalid
            )
```

### Test Coverage

```bash
# Generate HTML coverage report
pytest --cov=app --cov-report=html --cov-report=term-missing

# Show coverage for specific file
pytest --cov=app/models --cov-report=term-missing tests/test_models.py

# Set minimum coverage threshold
pytest --cov=app --cov-fail-under=80
```

---

## Git Workflow

### Branch Naming

```
feature/description      # New feature
fix/description         # Bug fix
docs/description        # Documentation
refactor/description    # Code refactoring
test/description        # Tests
chore/description       # Maintenance
```

Examples:
```bash
feature/search-pagination
fix/database-timeout
docs/api-reference
refactor/crud-operations
test/product-validation
```

### Commit Messages

Follow **Conventional Commits**:

```
<type>(<scope>): <subject>

<body>

<footer>
```

Examples:

```
# Feature
feat(api): add product search endpoint
Added full-text search with pagination support

# Fix
fix(models): validate price is positive
- Changed gte to gt in ProductCreate
- Added validation test

# Docs
docs(readme): update installation instructions
```

### Git Workflow Steps

```bash
# 1. Create feature branch from main
git checkout -b feature/new-feature

# 2. Make changes and commit
git add app/models.py
git commit -m "feat(models): add new field validation"

# 3. Push branch
git push origin feature/new-feature

# 4. Create pull request on GitHub
# (GitHub web interface)

# 5. After merge, clean up
git checkout main
git pull
git branch -d feature/new-feature
```

### Keeping Branch Updated

```bash
# Rebase on latest main
git fetch origin
git rebase origin/main

# If conflicts arise
git rebase --abort  # Start over
# Or manually resolve conflicts, then:
git add .
git rebase --continue
```

---

## Pull Request Process

### Before Creating PR

- [ ] Code follows style guide (run `black`, `isort`)
- [ ] All tests pass (`pytest`)
- [ ] Code coverage maintained (>80%)
- [ ] No new warnings or errors
- [ ] Updated relevant documentation
- [ ] Commit messages are descriptive
- [ ] Branch is up-to-date with `main`

### PR Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix (fixes #issue)
- [ ] New feature (related to #issue)
- [ ] Breaking change
- [ ] Documentation

## Testing
- [ ] Unit tests added
- [ ] Integration tests updated
- [ ] Manual testing done

## Checklist
- [ ] Code follows style guide
- [ ] Tests pass
- [ ] Coverage maintained
- [ ] Documentation updated
- [ ] No new linting errors

## Screenshots
(If applicable)
```

### Code Review Guidelines

Reviewers should check:

- ✓ Code quality and style
- ✓ Test coverage
- ✓ Documentation completeness
- ✓ Performance implications
- ✓ Security considerations
- ✓ Backward compatibility

---

## Writing Documentation

### Documentation Standards

All public functions, classes, and modules need documentation:

```python
"""Module for database operations.

This module provides CRUD operations for MongoDB collections.
Async functions are used throughout for non-blocking I/O.

Example:
    >>> product = await get_product("123")
    >>> print(product.name)
"""

async def create_product(product: ProductCreate) -> ProductInDB:
    """Create a new product in the database.
    
    Args:
        product: Product creation data
        
    Returns:
        Created product with auto-generated ID
        
    Raises:
        ValueError: If product data is invalid
        
    Example:
        >>> product = ProductCreate(name="Mouse", price=29.99)
        >>> created = await create_product(product)
    """
    pass
```

### Markdown Guide

```markdown
# Main Heading

## Section
### Subsection

**Bold text** and *italic text*

- Bullet point
- Another point

1. Numbered item
2. Another item

> Blockquote for important info

```code
code block
```

[Link text](url)

| Header 1 | Header 2 |
|----------|----------|
| Cell 1   | Cell 2   |
```

### README Updates

When making changes that affect users:

1. Update feature list if adding/removing features
2. Update installation instructions if dependencies change
3. Update API examples if endpoints change
4. Add new section in "Features" if major addition

---

## Common Tasks

### Adding a New Endpoint

```python
# 1. Define model in app/models.py
from pydantic import BaseModel, Field

class NewResourceCreate(BaseModel):
    """New resource creation request."""
    name: str = Field(..., min_length=1)
    description: str = Field(...)

class NewResourceInDB(NewResourceCreate):
    """New resource in database."""
    id: str

# 2. Add CRUD function in app/crud.py
async def create_new_resource(resource: NewResourceCreate) -> NewResourceInDB:
    """Create new resource."""
    doc = resource.model_dump()
    result = await collection.insert_one(doc)
    doc["id"] = str(result.inserted_id)
    return NewResourceInDB(**doc)

# 3. Add route in app/routers/resources.py
from fastapi import APIRouter

router = APIRouter(prefix="/resources", tags=["resources"])

@router.post("/", status_code=201)
async def create_resource(resource: NewResourceCreate) -> NewResourceInDB:
    """Create new resource."""
    return await create_new_resource(resource)

# 4. Write tests in tests/test_resources.py
@pytest.mark.asyncio
async def test_create_resource(mock_collection):
    """Test resource creation."""
    resource = NewResourceCreate(name="Test", description="Test")
    result = await create_new_resource(resource)
    assert result.id is not None
    assert result.name == "Test"

# 5. Update documentation in docs/API_REFERENCE.md
# (Add endpoint description and examples)
```

### Fixing a Bug

```bash
# 1. Create branch
git checkout -b fix/bug-description

# 2. Write failing test first
# tests/test_bug.py - demonstrates the bug

# 3. Make minimal changes to fix
# app/file.py - fix the bug

# 4. Ensure test passes
pytest tests/test_bug.py -v

# 5. Commit and create PR
git commit -m "fix(module): description of fix"
git push origin fix/bug-description
```

### Updating Dependencies

```bash
# 1. Check for updates
pip list --outdated

# 2. Update specific package
pip install --upgrade fastapi

# 3. Test everything works
pytest

# 4. Save to requirements.txt
pip freeze > requirements.txt

# 5. Commit
git commit -m "chore: update dependencies"
```

---

## Troubleshooting

### Common Issues

#### Tests Fail in CI But Pass Locally

```bash
# Check Python version matches
python --version

# Clear cache
rm -rf .pytest_cache __pycache__
pip cache purge

# Reinstall from requirements
pip install -r requirements-dev.txt

# Run tests again
pytest
```

#### Import Errors

```bash
# Ensure virtual environment is active
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Reinstall packages
pip install -e .
pip install -r requirements-dev.txt

# Check PYTHONPATH
echo $PYTHONPATH
```

#### Database Connection Issues

```bash
# Check if MongoDB is running
docker-compose ps nano

# Restart MongoDB
docker-compose restart mongo

# Check connection string
echo $DATABASE_URL

# Test connection directly
mongosh "mongodb://admin:secret123@localhost:27017/product_db"
```

#### Port Already in Use

```bash
# Check what's using port 8000
lsof -i :8000
sudo lsof -i :8000

# Kill process
kill -9 <PID>

# Or use different port
uvicorn app.main:app --port 8001
```

---

## Questions or Need Help?

- Check existing GitHub Issues
- Review documentation in `docs/`
- Look at similar existing code
- Ask in project discussions

## Code of Conduct

- Be respectful and inclusive
- No harassment or discrimination
- Welcome diverse perspectives
- Help other contributors

---

**Last Updated**: April 2, 2024  
**Version**: 1.0

Thank you for contributing! 🙏
