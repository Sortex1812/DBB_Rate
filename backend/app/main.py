import asyncio
import os

import uvicorn
from fastapi import FastAPI, HTTPException, Path, Query
from fastapi.middleware.cors import CORSMiddleware

from .crud import (
    create_feedback,
    get_all_subjects,
    get_feedbacks,
    get_stats,
    get_teachers_by_subject,
    login_user,
)
from .db import ensure_indexes
from .schemas import FeedbackIn
from dotenv import load_dotenv
import logging

logger = logging.getLogger("uvicorn.info")

load_dotenv()

app = FastAPI(title="Schueler Feedback API")

PORT = int(os.getenv("PORT", 8080))
HOST = os.getenv("HOST", "0.0.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/feedback", status_code=201)
async def post_feedback(payload: FeedbackIn):
    d = payload.model_dump()
    created = await create_feedback(d)
    return created


@app.post("/login")
async def login(username: str = Query(...), password: str = Query(...)):
    logined_user = await login_user(username, password)
    if logined_user:
        return {"message": "Login successful", "role": logined_user["role"]}
    else:
        raise HTTPException(status_code=401, detail="Invalid credentials")


@app.get("/feedbacks/{teacher}")
async def list_feedbacks(teacher: str = Path(...), limit: int = 100):
    logger.info(f"Fetching feedbacks for teacher: {teacher}")
    return await get_feedbacks(teacher=teacher, limit=limit)


@app.get("/stats/{teacher}")
async def stats(teacher: str = Path(...)):
    logger.info(f"Fetching stats for teacher: {teacher}")
    return await get_stats(teacher)


@app.get("/subjects")
async def get_subjects():
    return await get_all_subjects()


@app.get("/subjects/{subject}")
async def get_teachers_for_subject(subject: str = Path(...)):
    return await get_teachers_by_subject(subject)


if __name__ == "__main__":
    uvicorn.run("app.main:app", host=HOST, port=PORT, reload=True)
