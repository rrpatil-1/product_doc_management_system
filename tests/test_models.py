"""
Unit tests for Pydantic models and validation.
"""
import pytest
from pydantic import ValidationError
from app.models import (
    ProductBase, ProductCreate, ProductUpdate, ProductInDB,
    ErrorResponse, ErrorDetail, PaginatedProducts
)


class TestProductCreate:
    """Tests for ProductCreate model validation."""
    
    def test_create_valid_product(self):
        """Test creating a valid product."""
        product = ProductBase(
            name="Test Product",
            category="Electronics",
            description="A test product",
            price=99.99,
            discount=5.00
        )
        assert product.name == "Test Product"
        assert product.category == "Electronics"
        assert product.price == 99.99
        assert product.discount == 5.00
        assert product.id is not None  # Should auto-generate UUID
    
    def test_create_product_with_custom_id(self):
        """Test creating a product with a custom ID."""
        product = ProductCreate(
            id="custom-id-123",
            name="Product with ID",
            category="Books",
            description="Test product with custom ID",
            price=25.50
        )
        assert product.id == "custom-id-123"
    
    def test_create_product_missing_required_field(self):
        """Test that missing required fields raise validation error."""
        with pytest.raises(ValidationError) as exc_info:
            ProductCreate(
                name="Test Product",
                category="Electronics"
                # Missing description and price
            )
        assert "Field required" in str(exc_info.value) or "missing" in str(exc_info.value).lower()
    
    def test_create_product_empty_name(self):
        """Test that empty name raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            ProductCreate(
                name="",  # Empty name
                category="Electronics",
                description="Test",
                price=50.00
            )
        assert "at least 1 character" in str(exc_info.value).lower()
    
    def test_create_product_zero_price(self):
        """Test that price of 0 raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            ProductCreate(
                name="Test",
                category="Test",
                description="Test",
                price=0  # Invalid: must be > 0
            )
        assert "greater than 0" in str(exc_info.value).lower()
    
    def test_create_product_negative_discount(self):
        """Test that negative discount raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            ProductCreate(
                name="Test",
                category="Test",
                description="Test",
                price=50.00,
                discount=-5.00  # Invalid: must be >= 0
            )
        # Discount validation happens in ProductUpdate, not ProductCreate
        # But ProductCreate inherits from ProductBase which has validators
    
    def test_create_product_invalid_url(self):
        """Test that invalid URL raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            ProductCreate(
                name="Test",
                category="Test",
                description="Test",
                price=50.00,
                thumbnail_url="not-a-url"  # Invalid URL
            )
        assert "HTTP/HTTPS URL" in str(exc_info.value)
    
    def test_create_product_valid_https_url(self):
        """Test that HTTPS URL is valid."""
        product = ProductCreate(
            name="Test",
            category="Test",
            description="Test",
            price=50.00,
            thumbnail_url="https://example.com/image.jpg"
        )
        assert product.thumbnail_url == "https://example.com/image.jpg"
    
    def test_create_product_valid_http_url(self):
        """Test that HTTP URL is valid."""
        product = ProductCreate(
            name="Test",
            category="Test",
            description="Test",
            price=50.00,
            thumbnail_url="http://example.com/image.jpg"
        )
        assert product.thumbnail_url == "http://example.com/image.jpg"
    
    def test_create_product_none_url(self):
        """Test that None URL is allowed."""
        product = ProductCreate(
            name="Test",
            category="Test",
            description="Test",
            price=50.00,
            thumbnail_url=None
        )
        assert product.thumbnail_url is None


class TestProductUpdate:
    """Tests for ProductUpdate model validation."""
    
    def test_update_all_fields(self):
        """Test updating all fields."""
        update = ProductUpdate(
            name="Updated Name",
            category="Updated Category",
            description="Updated description",
            price=199.99,
            discount=25.00,
            thumbnail_url="https://example.com/new.jpg"
        )
        assert update.name == "Updated Name"
        assert update.price == 199.99
    
    def test_update_partial_fields(self):
        """Test updating partial fields."""
        update = ProductUpdate(
            name="Updated Name"
            # Other fields are None, which is allowed
        )
        assert update.name == "Updated Name"
        assert update.price is None
        assert update.category is None
    
    def test_update_empty_body(self):
        """Test that empty update body is allowed."""
        update = ProductUpdate()
        assert update.name is None
        assert update.price is None
    
    def test_update_invalid_price(self):
        """Test that invalid price raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            ProductUpdate(price=0)  # Must be > 0
        assert "greater than 0" in str(exc_info.value).lower()
    
    def test_update_invalid_discount(self):
        """Test that negative discount raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            ProductUpdate(discount=-5.00)  # Must be >= 0
        assert "non-negative" in str(exc_info.value).lower()
    
    def test_update_invalid_url(self):
        """Test that invalid URL raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            ProductUpdate(thumbnail_url="not-a-url")
        assert "HTTP/HTTPS URL" in str(exc_info.value)
    
    def test_update_empty_string_url(self):
        """Test that empty string URL is treated as None."""
        update = ProductUpdate(thumbnail_url="")
        assert update.thumbnail_url is None


class TestProductInDB:
    """Tests for ProductInDB model."""
    
    def test_product_in_db_creation(self):
        """Test creating a ProductInDB instance."""
        product = ProductInDB(
            id="prod-001",
            name="Test Product",
            category="Electronics",
            description="Test",
            price=50.00,
            discount=5.00,
            thumbnail_url="https://example.com/image.jpg"
        )
        assert product.id == "prod-001"
        assert product.name == "Test Product"
    
    def test_product_in_db_without_thumbnail(self):
        """Test ProductInDB without thumbnail URL."""
        product = ProductInDB(
            id="prod-002",
            name="Test",
            category="Test",
            description="Test",
            price=25.00
        )
        assert product.thumbnail_url is None
        assert product.discount == 0


class TestPaginatedProducts:
    """Tests for PaginatedProducts model."""
    
    def test_paginated_products_creation(self):
        """Test creating a PaginatedProducts instance."""
        products = [
            ProductInDB(id="1", name="Product 1", category="Cat1", description="Desc1", price=50.00),
            ProductInDB(id="2", name="Product 2", category="Cat2", description="Desc2", price=75.00),
        ]
        paginated = PaginatedProducts(
            products=products,
            total=10,
            skip=0,
            limit=2
        )
        assert len(paginated.products) == 2
        assert paginated.total == 10
        assert paginated.skip == 0
        assert paginated.limit == 2
    
    def test_paginated_products_empty(self):
        """Test PaginatedProducts with no products."""
        paginated = PaginatedProducts(
            products=[],
            total=0,
            skip=0,
            limit=10
        )
        assert len(paginated.products) == 0
        assert paginated.total == 0


class TestErrorResponse:
    """Tests for ErrorResponse model."""
    
    def test_error_response_creation(self):
        """Test creating an ErrorResponse."""
        error = ErrorResponse(
            error="validation_error",
            message="Invalid input",
            code="INVALID_INPUT",
            timestamp="2024-01-01T00:00:00"
        )
        assert error.error == "validation_error"
        assert error.message == "Invalid input"
    
    def test_error_response_with_details(self):
        """Test ErrorResponse with error details."""
        details = [
            ErrorDetail(field="name", message="Name is required", code="REQUIRED_FIELD"),
            ErrorDetail(field="price", message="Price must be positive", code="INVALID_VALUE")
        ]
        error = ErrorResponse(
            error="validation_error",
            message="Multiple validation errors",
            details=details
        )
        assert len(error.details) == 2
        assert error.details[0].field == "name"
