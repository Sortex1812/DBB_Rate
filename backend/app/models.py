from datetime import datetime

from bson import ObjectId


def feedback_doc(payload: dict) -> dict:
    doc = payload.copy()
    doc["timestamp"] = payload.get("timestamp") or datetime.now()
    return doc


def serialize_feedback(doc: dict) -> dict:
    return {
        "id": str(doc.get("_id")),
        "teacher": doc.get("teacher"),
        "subject": doc.get("subject"),
        "mood": doc.get("mood"),
        "difficulty": doc.get("difficulty"),
        "comment": doc.get("comment"),
        "timestamp": t.isoformat() if (t := doc.get("timestamp")) else None,
    }
