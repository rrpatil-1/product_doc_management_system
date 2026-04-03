import logging
from app.database import collection
from app.models import ProductCreate, ProductUpdate, ProductInDB
from motor.motor_asyncio import AsyncIOMotorCollection
from bson import ObjectId
from typing import List, Optional
import re

logger = logging.getLogger(__name__)

async def create_product(product: ProductCreate) -> ProductInDB:
    logger.info(f"Creating new product: {product.name}")
    product_dict = product.dict()
    if not product_dict.get("id"):
        # Auto-generate if not provided
        from uuid import uuid4
        product_dict["id"] = str(uuid4())
        logger.debug(f"Auto-generated ID: {product_dict['id']}")
    result = await collection.insert_one(product_dict)
    created_product = await collection.find_one({"_id": result.inserted_id})
    logger.info(f"Product created with ID: {created_product['id']}")
    return ProductInDB(**created_product)

async def get_products_count() -> int:
    logger.debug("Retrieving total products count")
    count = await collection.count_documents({})
    logger.debug(f"Total products count: {count}")
    return count

async def get_products(skip: int = 0, limit: int = 100, sort_field: str = "name", sort_order: int = 1) -> List[ProductInDB]:
    logger.info(f"Retrieving products with skip={skip}, limit={limit}, sort_field={sort_field}, sort_order={sort_order}")
    products = []
    cursor = collection.find().sort(sort_field, sort_order).skip(skip).limit(limit)
    async for product in cursor:
        products.append(ProductInDB(**product))
    logger.info(f"Retrieved {len(products)} products")
    return products

async def get_product_by_id(product_id: str) -> Optional[ProductInDB]:
    logger.debug(f"Retrieving product by ID: {product_id}")
    product = await collection.find_one({"id": product_id})
    if product:
        logger.debug(f"Product found: {product['name']}")
        return ProductInDB(**product)
    logger.debug(f"Product not found: {product_id}")
    return None

async def update_product(product_id: str, update_data: ProductUpdate) -> Optional[ProductInDB]:
    logger.info(f"Updating product {product_id}")
    update_dict = {k: v for k, v in update_data.dict().items() if v is not None}
    if update_dict:
        logger.debug(f"Update fields: {list(update_dict.keys())}")
        result = await collection.update_one({"id": product_id}, {"$set": update_dict})
        if result.modified_count == 1 or result.matched_count == 1:
            updated_product = await collection.find_one({"id": product_id})
            logger.info(f"Product {product_id} updated successfully")
            return ProductInDB(**updated_product)
    else:
        # No changes, return existing product
        logger.info(f"No changes for product {product_id}")
        return await get_product_by_id(product_id)
    logger.warning(f"Failed to update product {product_id}")
    return None

async def delete_product(product_id: str) -> bool:
    logger.info(f"Deleting product {product_id}")
    result = await collection.delete_one({"id": product_id})
    if result.deleted_count == 1:
        logger.info(f"Product {product_id} deleted successfully")
        return True
    logger.warning(f"Product {product_id} not found for deletion")
    return False

async def search_products(query: str, field: Optional[str] = None) -> List[ProductInDB]:
    logger.info(f"Searching products with query='{query}', field={field}")
    search_fields = ["name", "category", "description"] if not field else [field]
    regex = re.compile(query, re.IGNORECASE)
    search_query = {"$or": [{f: {"$regex": regex}} for f in search_fields]}
    logger.debug(f"Search query: {search_query}")
    products = []
    cursor = collection.find(search_query)
    async for product in cursor:
        products.append(ProductInDB(**product))
    logger.info(f"Search returned {len(products)} products")
    return products