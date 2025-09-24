from datetime import datetime
from typing import List

from .db import db, feedback_collection, subject_collection, user_collection
from .models import feedback_doc, serialize_feedback


async def create_feedback(payload: dict) -> dict:
    payload["timestamp"] = datetime.now()
    res = await feedback_collection.insert_one(payload)
    created = await feedback_collection.find_one({"_id": res.inserted_id})
    if created:
        created["id"] = str(created["_id"])
        del created["_id"]
        return created
    else:
        return {}


async def get_feedbacks(limit: int = 100) -> List[dict]:
    cursor = feedback_collection.find().sort("timestamp", -1).limit(limit)
    results = []
    async for doc in cursor:
        results.append(serialize_feedback(doc))
    return results


async def get_stats() -> dict:
    total = await feedback_collection.count_documents({})
    pipeline = [{"$group": {"_id": "$difficulty", "count": {"$sum": 1}}}]
    cursor = await feedback_collection.aggregate(pipeline)
    by_difficulty = {
        doc["_id"]: doc["count"] for doc in await cursor.to_list(length=100)
    }

    pipeline2 = [{"$group": {"_id": "$mood", "count": {"$sum": 1}}}]
    cursor2 = await feedback_collection.aggregate(pipeline2)
    by_mood = {doc["_id"]: doc["count"] for doc in await cursor2.to_list(length=100)}
    return {"total": total, "by_difficulty": by_difficulty, "by_mood": by_mood}


async def get_subjects() -> List[str]:
    subjects = await subject_collection.distinct("subject")
    return subjects


async def get_teachers_by_subject(subject: str):
    teachers = await subject_collection.find_one({"subject": subject})
    return teachers


async def login_user(username: str, password: str) -> dict:
    user = await user_collection.find_one({"username": username, "password": password})
    if user:
        return {"username": user["username"], "role": user["role"]}
    else:
        return {}
