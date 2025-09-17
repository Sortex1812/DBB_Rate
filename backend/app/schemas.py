from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class FeedbackIn(BaseModel):
    teacher: str = Field(..., examples=["Herr Müller"])
    subject: str = Field(..., examples=["Mathe"])
    mood: str = Field(..., examples=["🙂"]) 
    difficulty: str = Field(..., examples=["mittel"])
    comment: Optional[str] = Field(..., examples=["Mehr Beispiele wären gut"])
    timestamp: Optional[datetime] = None

class FeedbackOut(FeedbackIn):
    id: str

class Stats(BaseModel):
    total: int
    by_difficulty: dict
    by_mood: dict
