import logging
import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

load_dotenv()

# Environment variables with defaults
MONGODB_HOST = os.getenv("MONGODB_HOST")
DATABASE_NAME = os.getenv("DATABASE_NAME")
COLLECTION_NAME = os.getenv("COLLECTION_NAME")

USERNAME = os.getenv("MONGO_INITDB_ROOT_USERNAME")
PASSWORD = os.getenv("MONGO_INITDB_ROOT_PASSWORD")

# Build MongoDB URL safely
if USERNAME and PASSWORD:
    MONGO_URL = f"mongodb://{USERNAME}:{PASSWORD}@{MONGODB_HOST}/{DATABASE_NAME}?authSource=admin"
else:
    logger.warning("MongoDB running without authentication")
    MONGO_URL = f"mongodb://{MONGODB_HOST}/{DATABASE_NAME}"

logger.info(f"Connecting to MongoDB at {MONGODB_HOST}")

# Create client
client = AsyncIOMotorClient(MONGO_URL)

# Access DB and collection
database = client[DATABASE_NAME]
collection = database[COLLECTION_NAME]


