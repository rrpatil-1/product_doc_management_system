import asyncio
import logging
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os
from uuid import uuid4

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "document_management_system")

# Sample products data
SAMPLE_PRODUCTS = [
    {
        "id": str(uuid4()),
        "name": "Laptop Pro 15",
        "category": "Electronics",
        "description": "High-performance laptop with Intel i7 processor, 16GB RAM, 512GB SSD",
        "thumbnail_url": "https://via.placeholder.com/300x200?text=Laptop+Pro+15",
        "price": 1299.99,
        "discount": 0
    },
    {
        "id": str(uuid4()),
        "name": "Wireless Mouse",
        "category": "Accessories",
        "description": "Ergonomic wireless mouse with 1000DPI precision and long battery life",
        "thumbnail_url": "https://via.placeholder.com/300x200?text=Wireless+Mouse",
        "price": 29.99,
        "discount": 5.00
    },
    {
        "id": str(uuid4()),
        "name": "USB-C Cable",
        "category": "Cables",
        "description": "High-speed USB-C cable with 100W power delivery support",
        "thumbnail_url": "https://via.placeholder.com/300x200?text=USB-C+Cable",
        "price": 15.99,
        "discount": 2.00
    },
    {
        "id": str(uuid4()),
        "name": "Mechanical Keyboard",
        "category": "Peripherals",
        "description": "RGB backlit mechanical keyboard with Cherry MX switches and aluminum frame",
        "thumbnail_url": "https://via.placeholder.com/300x200?text=Mechanical+Keyboard",
        "price": 149.99,
        "discount": 15.00
    },
    {
        "id": str(uuid4()),
        "name": "Monitor 4K Ultra HD",
        "category": "Electronics",
        "description": "27-inch 4K Ultra HD display with 60Hz refresh rate and HDR support",
        "thumbnail_url": "https://via.placeholder.com/300x200?text=Monitor+4K",
        "price": 499.99,
        "discount": 50.00
    },
    {
        "id": str(uuid4()),
        "name": "Webcam 1080p",
        "category": "Accessories",
        "description": "Full HD 1080p webcam with auto-focus and built-in microphone",
        "thumbnail_url": "https://via.placeholder.com/300x200?text=Webcam+1080p",
        "price": 79.99,
        "discount": 0
    },
    {
        "id": str(uuid4()),
        "name": "Portable SSD 1TB",
        "category": "Storage",
        "description": "Ultra-fast portable SSD with 1TB capacity and USB 3.1 interface",
        "thumbnail_url": "https://via.placeholder.com/300x200?text=Portable+SSD",
        "price": 129.99,
        "discount": 10.00
    },
    {
        "id": str(uuid4()),
        "name": "Desk Lamp LED",
        "category": "Lighting",
        "description": "Adjustable LED desk lamp with 5 brightness levels and USB charging port",
        "thumbnail_url": "https://via.placeholder.com/300x200?text=Desk+Lamp",
        "price": 39.99,
        "discount": 0
    },
]

async def seed_database():
    logger.info("Starting database seeding")
    client = AsyncIOMotorClient(MONGODB_URL)
    db = client[DATABASE_NAME]
    collection = db["documents"]
    
    try:
        # Check if collection has documents
        existing_count = await collection.count_documents({})
        if existing_count > 0:
            logger.info(f"Collection already contains {existing_count} documents. Skipping seeding.")
            logger.info("To reset and reseed, run: uv run python seed_db.py --reset")
            return
        
        # Insert sample products
        result = await collection.insert_many(SAMPLE_PRODUCTS)
        logger.info(f"Successfully inserted {len(result.inserted_ids)} sample products!")
        logger.debug("Sample Products:")
        for i, product in enumerate(SAMPLE_PRODUCTS, 1):
            logger.debug(f"{i}. {product['name']} - ${product['price']}")
    except Exception as e:
        logger.error(f"Error seeding database: {str(e)}")
    finally:
        client.close()
        logger.info("Database connection closed")

async def reset_database():
    logger.info("Starting database reset")
    client = AsyncIOMotorClient(MONGODB_URL)
    db = client[DATABASE_NAME]
    collection = db["documents"]
    
    try:
        result = await collection.delete_many({})
        logger.info(f"Deleted {result.deleted_count} documents from collection.")
        
        # Reseed
        result = await collection.insert_many(SAMPLE_PRODUCTS)
        logger.info(f"Successfully inserted {len(result.inserted_ids)} sample products!")
        logger.debug("Sample Products:")
        for i, product in enumerate(SAMPLE_PRODUCTS, 1):
            logger.debug(f"{i}. {product['name']} - ${product['price']}")
    except Exception as e:
        logger.error(f"Error resetting database: {str(e)}")
    finally:
        client.close()
        logger.info("Database connection closed")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--reset":
        logger.info("Resetting database and reseeding...")
        asyncio.run(reset_database())
    else:
        logger.info("Seeding database with sample products...")
        asyncio.run(seed_database())