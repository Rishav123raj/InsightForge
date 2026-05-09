from pathlib import Path
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from pydantic import BaseModel, Field
from backend.services.ingest import init_db
from backend.services.orchestrator import answer_question
from backend.services.security import require_user
from backend.services import tools

BASE_DIR = Path(__file__).resolve().parent

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(title="Secure AI Insights Assistant", version="1.0.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    question: str = Field(min_length=3, max_length=600)


class SqlRequest(BaseModel):
    sql: str = Field(min_length=8, max_length=1200)

@app.get("/api/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/api/ingest")
def ingest(user: dict = Depends(require_user)) -> dict:
    if user["role"] != "leadership":
        raise HTTPException(status_code=403, detail="Only leadership can re-ingest sources")
    return init_db()


@app.post("/api/chat")
def chat(payload: ChatRequest, user: dict = Depends(require_user)) -> dict:
    return answer_question(payload.question, user)


@app.get("/api/analytics/best-titles")
def best_titles(year: int = 2025, user: dict = Depends(require_user)) -> list[dict]:
    return tools.best_titles(year)


@app.get("/api/analytics/city-engagement")
def city_engagement(month: str = "2025-12", user: dict = Depends(require_user)) -> list[dict]:
    return tools.city_engagement(month)


@app.post("/api/analytics/safe-sql")
def safe_sql(payload: SqlRequest, user: dict = Depends(require_user)) -> list[dict]:
    try:
        return tools.safe_sql(payload.sql)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc