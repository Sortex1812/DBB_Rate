# backend/app/main.py
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from .schemas import FeedbackIn
from .crud import create_feedback, get_feedbacks, get_stats
from .db import ensure_indexes
import asyncio

app = FastAPI(title="Schueler Feedback API")

# CORS (damit Streamlit lokal Anfragen machen kann)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # für Schulprojekt ok; produktiv einschränken
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    # create indexes if desired
    try:
        await ensure_indexes()
    except Exception:
        pass

@app.post("/feedback", status_code=201)
async def post_feedback(payload: FeedbackIn):
    d = payload.dict()
    created = await create_feedback(d)
    return created

@app.get("/feedbacks")
async def list_feedbacks(limit: int = 100):
    return await get_feedbacks(limit=limit)

@app.get("/stats")
async def stats():
    return await get_stats()

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
