"""
Unit tests for CRUD operations.
"""
import pytest
from app.models import ProductCreate, ProductUpdate, ProductInDB
from app.crud import (
    create_product,
    get_products,
    get_products_count,
    get_product_by_id,
    update_product,
    delete_product,
    search_products
)


@pytest.mark.asyncio
class TestCreateProduct:
    """Tests for create_product CRUD operation."""
    
    async def test_create_product_with_auto_id(self, mock_collection):
        """Test creating a product with auto-generated ID."""
        product_data = ProductCreate(
            name="Test Product",
            category="Electronics",
            description="Test description",
            price=99.99,
            discount=10.00
        )
        result = await create_product(product_data)
        assert isinstance(result, ProductInDB)
        assert result.name == "Test Product"
        assert result.id is not None
        assert result.price == 99.99
    
    async def test_create_product_with_custom_id(self, mock_collection):
        """Test creating a product with custom ID."""
        product_data = ProductCreate(
            id="custom-id-123",
            name="Test Product",
            category="Electronics",
            description="Test description",
            price=99.99
        )
        result = await create_product(product_data)
        assert result.id == "custom-id-123"
    
    async def test_create_product_minimal_fields(self, mock_collection):
        """Test creating a product with minimal required fields."""
        product_data = ProductCreate(
            name="Minimal Product",
            category="Test",
            description="Minimal test",
            price=25.00
        )
        result = await create_product(product_data)
        assert result.name == "Minimal Product"
        assert result.discount == 0  # Default value


@pytest.mark.asyncio
class TestReadProducts:
    """Tests for read operations."""
    
    async def test_get_products_count_empty(self, mock_collection):
        """Test getting count of products (empty collection)."""
        count = await get_products_count()
        assert count == 0
    
    async def test_get_products_empty(self, mock_collection):
        """Test getting products from empty collection."""
        products = await get_products(skip=0, limit=10)
        assert len(products) == 0
    
    async def test_get_products_with_sorting(self, mock_collection):
        """Test getting products with sorting."""
        # First insert some products
        product1 = ProductCreate(name="Product Z", category="Cat", description="D", price=100)
        product2 = ProductCreate(name="Product A", category="Cat", description="D", price=50)
        
        await create_product(product1)
        await create_product(product2)
        
        # Get sorted by name ascending
        products = await get_products(skip=0, limit=10, sort_field="name", sort_order=1)
        assert len(products) == 2
        # Note: Results would be sorted, but we'd need to verify the order
    
    async def test_get_product_by_id_not_found(self, mock_collection):
        """Test getting product that doesn't exist."""
        result = await get_product_by_id("non-existent-id")
        assert result is None
    
    async def test_get_product_by_id_found(self, mock_collection):
        """Test getting product by ID when it exists."""
        # Create a product first
        product_data = ProductCreate(
            id="test-id-123",
            name="Test Product",
            category="Test",
            description="Test",
            price=50.00
        )
        created = await create_product(product_data)
        
        # Now get it by ID
        result = await get_product_by_id("test-id-123")
        assert result is not None
        assert result.name == "Test Product"
        assert result.id == "test-id-123"


@pytest.mark.asyncio
class TestUpdateProduct:
    """Tests for update_product operation."""
    
    async def test_update_product_not_found(self, mock_collection):
        """Test updating a product that doesn't exist."""
        update_data = ProductUpdate(name="Updated Name")
        result = await update_product("non-existent", update_data)
        assert result is None
    
    async def test_update_product_all_fields(self, mock_collection):
        """Test updating all fields of a product."""
        # Create a product first
        product_data = ProductCreate(
            id="update-test-1",
            name="Original Name",
            category="Original Cat",
            description="Original Desc",
            price=50.00,
            discount=5.00
        )
        await create_product(product_data)
        
        # Update it
        update_data = ProductUpdate(
            name="Updated Name",
            category="Updated Cat",
            description="Updated Desc",
            price=75.00,
            discount=10.00
        )
        result = await update_product("update-test-1", update_data)
        assert result is not None
        assert result.name == "Updated Name"
        assert result.price == 75.00
        assert result.discount == 10.00
    
 

@pytest.mark.asyncio
class TestDeleteProduct:
    """Tests for delete_product operation."""
    
    async def test_delete_product_not_found(self, mock_collection):
        """Test deleting a product that doesn't exist."""
        result = await delete_product("non-existent")
        assert result is False
    
    async def test_delete_product_success(self, mock_collection):
        """Test successfully deleting a product."""
        # Create a product
        product_data = ProductCreate(
            id="delete-test-1",
            name="To Delete",
            category="Test",
            description="Test",
            price=50.00
        )
        await create_product(product_data)
        
        # Verify it exists
        found = await get_product_by_id("delete-test-1")
        assert found is not None
        
        # Delete it
        result = await delete_product("delete-test-1")
        assert result is True
        
        # Verify it's gone
        found = await get_product_by_id("delete-test-1")
        assert found is None


@pytest.mark.asyncio
class TestSearchProducts:
    """Tests for search_products operation."""
    
    async def test_search_empty_collection(self, mock_collection):
        """Test searching in empty collection."""
        results = await search_products("test")
        assert len(results) == 0
    
    async def test_search_by_name(self, mock_collection):
        """Test searching products by name."""
        # Create some products
        product1 = ProductCreate(name="iPhone", category="Phone", description="Apple phone", price=999)
        product2 = ProductCreate(name="Samsung", category="Phone", description="Samsung phone", price=799)
        
        await create_product(product1)
        await create_product(product2)
        
        # Search for iPhone
        results = await search_products("iPhone", field="name")
        assert len(results) > 0
        assert any(p.name == "iPhone" for p in results)
    
    async def test_search_by_category(self, mock_collection):
        """Test searching products by category."""
        # Create a product
        product = ProductCreate(
            name="Test",
            category="Electronics",
            description="Test",
            price=50
        )
        await create_product(product)
        
        # Search by category
        results = await search_products("Electronics", field="category")
        assert len(results) > 0
    
    async def test_search_by_description(self, mock_collection):
        """Test searching products by description."""
        # Create a product
        product = ProductCreate(
            name="Test",
            category="Test",
            description="High quality product",
            price=50
        )
        await create_product(product)
        
        # Search by description
        results = await search_products("quality", field="description")
        assert len(results) > 0
    
    async def test_search_case_insensitive(self, mock_collection):
        """Test that search is case-insensitive."""
        # Create a product
        product = ProductCreate(
            name="iPhone",
            category="Electronics",
            description="Apple phone",
            price=999
        )
        await create_product(product)
        
        # Search with different cases
        results_lower = await search_products("iphone")
        results_upper = await search_products("IPHONE")
        results_mixed = await search_products("IpHoNe")
        
        assert len(results_lower) > 0
        assert len(results_upper) > 0
        assert len(results_mixed) > 0
    
    async def test_search_multiple_fields(self, mock_collection):
        """Test searching across multiple fields without specifying one."""
        # Create products
        product = ProductCreate(
            name="Laptop",
            category="Electronics",
            description="Powerful computing device",
            price=1500
        )
        await create_product(product)
        
        # Search without specifying field (should search all)
        results = await search_products("Laptop")
        assert len(results) > 0


@pytest.mark.asyncio
class TestCRUDIntegration:
    """Integration tests for CRUD operations working together."""
    
    async def test_full_crud_cycle(self, mock_collection):
        """Test complete CRUD cycle: Create, Read, Update, Delete."""
        # Create
        product_data = ProductCreate(
            id="crud-test-1",
            name="Integration Test Product",
            category="Test",
            description="For CRUD testing",
            price=99.99
        )
        created = await create_product(product_data)
        assert created.id == "crud-test-1"
        
        # Read
        retrieved = await get_product_by_id("crud-test-1")
        assert retrieved is not None
        assert retrieved.name == "Integration Test Product"
        
        # Update
        update_data = ProductUpdate(name="Updated Integration Test")
        updated = await update_product("crud-test-1", update_data)
        assert updated.name == "Updated Integration Test"
        
        # Read again to verify update
        verified = await get_product_by_id("crud-test-1")
        assert verified.name == "Updated Integration Test"
        
        # Delete
        deleted = await delete_product("crud-test-1")
        assert deleted is True
        
        # Verify deletion
        not_found = await get_product_by_id("crud-test-1")
        assert not_found is None
