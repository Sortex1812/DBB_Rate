# backend/app/models.py
from datetime import datetime
from bson import ObjectId

def feedback_doc(payload: dict) -> dict:
    doc = payload.copy()
    doc["timestamp"] = payload.get("timestamp") or datetime.now()
    return doc

def serialize_feedback(doc: dict) -> dict:
    return {
        "id": str(doc.get("_id")),
        "subject": doc.get("subject"),
        "mood": doc.get("mood"),
        "difficulty": doc.get("difficulty"),
        "comment": doc.get("comment"),
        "timestamp": doc.get("timestamp").isoformat() if doc.get("timestamp") else None,
    }
