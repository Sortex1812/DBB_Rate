# backend/app/db.py
import os
from motor.motor_asyncio import AsyncIOMotorClient

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("MONGO_DB", "feedbackdb")

client = AsyncIOMotorClient(MONGO_URI)
db = client[DB_NAME]
feedback_collection = db["feedbacks"]

# optional create indexes at startup
async def ensure_indexes():
    await feedback_collection.create_index("timestamp")
