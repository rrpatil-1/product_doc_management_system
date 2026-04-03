"""
Pytest configuration and shared fixtures for testing.
"""
import os
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from app.main import app

# Load test environment
load_dotenv()

# Environment variables
MONGODB_HOST = os.getenv("MONGODB_HOST")


# ✅ REMOVE custom event_loop (pytest-asyncio handles it now)


# ✅ FIXED: async fixture must use pytest_asyncio
@pytest_asyncio.fixture
async def test_db():
    """Set up and tear down test database."""
    test_db_name = os.getenv("DATABASE_NAME", "document_management_system") + "_test"
    test_collection_name = "products_test"
    test_url = f"mongodb://{MONGODB_HOST}/{test_db_name}"

    client = AsyncIOMotorClient(test_url)
    test_database = client[test_db_name]
    test_collection = test_database[test_collection_name]

    yield test_collection

    # Cleanup
    await test_collection.drop()
    client.close()


# ✅ FIXED: async fixture decorator
@pytest_asyncio.fixture
async def mock_collection(test_db):
    """Mock collection to isolate DB operations."""
    import app.crud as crud_module

    original_collection = crud_module.collection
    crud_module.collection = test_db

    yield test_db

    crud_module.collection = original_collection


# ✅ FIXED: httpx AsyncClient (NEW WAY)
@pytest_asyncio.fixture
async def async_client():
    """Create a test client for API testing."""
    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url="http://test"
    ) as client:
        yield client


# ✅ These don't need to be async (no awaits inside)
@pytest.fixture
def sample_product():
    return {
        "id": "prod-001",
        "name": "Test Product",
        "category": "Electronics",
        "description": "A test product for unit testing",
        "thumbnail_url": "https://example.com/image.jpg",
        "price": 99.99,
        "discount": 10.00
    }


@pytest.fixture
def multiple_sample_products():
    return [
        {
            "id": "prod-001",
            "name": "Product A",
            "category": "Electronics",
            "description": "First product",
            "thumbnail_url": "https://example.com/image1.jpg",
            "price": 100.00,
            "discount": 5.00
        },
        {
            "id": "prod-002",
            "name": "Product B",
            "category": "Clothing",
            "description": "Second product",
            "thumbnail_url": "https://example.com/image2.jpg",
            "price": 50.00,
            "discount": 0.00
        },
        {
            "id": "prod-003",
            "name": "Product C",
            "category": "Electronics",
            "description": "Third product with electronics",
            "thumbnail_url": "https://example.com/image3.jpg",
            "price": 150.00,
            "discount": 20.00
        }
    ]