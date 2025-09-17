import uvicorn
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from .schemas import FeedbackIn
from .crud import (
    create_feedback,
    get_feedbacks,
    get_stats,
    get_teachers_by_subject,
    login_user,
)
from .db import ensure_indexes
import asyncio

app = FastAPI(title="Schueler Feedback API")

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
async def login(user: str = Query(...), password: str = Query(...)):
    logined_user = await login_user(user, password)
    if logined_user:
        return {"message": "Login successful", "role": logined_user["role"]}
    else:
        raise HTTPException(status_code=401, detail="Invalid credentials")

@app.get("/feedbacks")
async def list_feedbacks(limit: int = 100):
    return await get_feedbacks(limit=limit)


@app.get("/stats")
async def stats():
    return await get_stats()


@app.get("/teachers")
async def teachers(subject: str = Query(...)):
    return await get_teachers_by_subject(subject)


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
