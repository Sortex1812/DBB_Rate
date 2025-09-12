# backend/app/crud.py
from .db import feedback_collection
from .models import feedback_doc, serialize_feedback
from typing import List
from bson import ObjectId
import asyncio

async def create_feedback(payload: dict) -> dict:
    doc = feedback_doc(payload)
    res = await feedback_collection.insert_one(doc)
    created = await feedback_collection.find_one({"_id": res.inserted_id})
    return serialize_feedback(created)

async def get_feedbacks(limit: int = 100) -> List[dict]:
    cursor = feedback_collection.find().sort("timestamp", -1).limit(limit)
    results = []
    async for doc in cursor:
        results.append(serialize_feedback(doc))
    return results

async def get_stats() -> dict:
    total = await feedback_collection.count_documents({})
    # aggregation for difficulty
    pipeline = [
        {"$group": {"_id": "$difficulty", "count": {"$sum": 1}}}
    ]
    cursor = feedback_collection.aggregate(pipeline)
    by_difficulty = {doc["_id"]: doc["count"] for doc in await cursor.to_list(length=100)}
    # aggregation for mood
    pipeline2 = [{"$group": {"_id": "$mood", "count": {"$sum": 1}}}]
    cursor2 = feedback_collection.aggregate(pipeline2)
    by_mood = {doc["_id"]: doc["count"] for doc in await cursor2.to_list(length=100)}
    return {"total": total, "by_difficulty": by_difficulty, "by_mood": by_mood}
