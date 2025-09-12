# backend/app/db.py
import os
from pymongo import MongoClient
from pymongo import AsyncMongoClient

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("MONGO_DB", "feedbackdb")

client = AsyncMongoClient(MONGO_URI)
db = client[DB_NAME]
feedback_collection = db["feedbacks"]

async def ensure_indexes():
    await feedback_collection.create_index("timestamp")
