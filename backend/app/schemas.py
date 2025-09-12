# backend/app/schemas.py
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class FeedbackIn(BaseModel):
    subject: str = Field(..., example="Mathe")
    mood: str = Field(..., example="🙂")  # or 'good/neutral/bad'
    difficulty: str = Field(..., example="mittel")  # leicht/mittel/schwer
    comment: Optional[str] = Field(None, example="Mehr Beispiele wären gut")
    timestamp: Optional[datetime] = None

class FeedbackOut(FeedbackIn):
    id: str

class Stats(BaseModel):
    total: int
    by_difficulty: dict
    by_mood: dict
