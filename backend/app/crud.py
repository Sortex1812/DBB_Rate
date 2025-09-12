# backend/app/crud.py
from .db import feedback_collection
from datetime import datetime

async def create_feedback(payload: dict) -> dict:
    payload["timestamp"] = datetime.now()
    res = await feedback_collection.insert_one(payload)
    created = await feedback_collection.find_one({"_id": res.inserted_id})
    created["id"] = str(created["_id"])
    del created["_id"]
    return created
