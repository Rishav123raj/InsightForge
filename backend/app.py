from pathlib import Path
import logging

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from pydantic import BaseModel, Field

from backend.services.ingest import init_db
from backend.services.orchestrator import answer_question
from backend.services.security import require_user
from backend.services import tools


# -----------------------------------------------------------------------------
# Logging Configuration
# -----------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,

    format="%(asctime)s | %(levelname)s | %(message)s",

    handlers=[
        logging.FileHandler("insightforge.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("insightforge")


# -----------------------------------------------------------------------------
# App Setup
# -----------------------------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent


@asynccontextmanager
async def lifespan(app: FastAPI):

    logger.info("Starting InsightForge application")

    init_db()

    logger.info("Database initialized successfully")

    yield

    logger.info("Shutting down InsightForge application")


app = FastAPI(
    title="Secure AI Insights Assistant",
    version="1.0.0",
    lifespan=lifespan
)


# -----------------------------------------------------------------------------
# Middleware
# -----------------------------------------------------------------------------

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


# -----------------------------------------------------------------------------
# Request Models
# -----------------------------------------------------------------------------

class ChatRequest(BaseModel):
    question: str = Field(min_length=3, max_length=600)


class SqlRequest(BaseModel):
    sql: str = Field(min_length=8, max_length=1200)


# -----------------------------------------------------------------------------
# Routes
# -----------------------------------------------------------------------------

@app.get("/api/health")
def health() -> dict:

    logger.info("Health check endpoint called")

    return {"status": "ok"}


@app.post("/api/ingest")
def ingest(user: dict = Depends(require_user)) -> dict:

    logger.info(f"Ingest requested by user={user['user_id']} role={user['role']}")

    if user["role"] != "leadership":

        logger.warning(
            f"Unauthorized ingest attempt by user={user['user_id']}"
        )

        raise HTTPException(
            status_code=403,
            detail="Only leadership can re-ingest sources"
        )

    result = init_db()

    logger.info("Data ingestion completed successfully")

    return result


@app.post("/api/chat")
def chat(payload: ChatRequest, user: dict = Depends(require_user)) -> dict:

    logger.info(
        f"Chat request from user={user['user_id']} "
        f"role={user['role']} "
        f"question='{payload.question}'"
    )

    try:

        response = answer_question(payload.question, user)

        logger.info("AI response generated successfully")

        return response

    except Exception as e:

        logger.exception(f"Chat endpoint failed: {str(e)}")

        raise HTTPException(
            status_code=500,
            detail="Failed to generate AI response"
        )


@app.get("/api/analytics/best-titles")
def best_titles(
    year: int = 2025,
    user: dict = Depends(require_user)
) -> list[dict]:

    logger.info(
        f"Best titles requested by user={user['user_id']} "
        f"for year={year}"
    )

    return tools.best_titles(year)


@app.get("/api/analytics/city-engagement")
def city_engagement(
    month: str = "2025-12",
    user: dict = Depends(require_user)
) -> list[dict]:

    logger.info(
        f"City engagement requested by user={user['user_id']} "
        f"for month={month}"
    )

    return tools.city_engagement(month)


@app.post("/api/analytics/safe-sql")
def safe_sql(
    payload: SqlRequest,
    user: dict = Depends(require_user)
) -> list[dict]:

    logger.info(
        f"Safe SQL query requested by user={user['user_id']}"
    )

    try:

        result = tools.safe_sql(payload.sql)

        logger.info("Safe SQL executed successfully")

        return result

    except ValueError as exc:

        logger.warning(f"Blocked unsafe SQL query: {str(exc)}")

        raise HTTPException(
            status_code=400,
            detail=str(exc)
        ) from exc

    except Exception as e:

        logger.exception(f"SQL endpoint failed: {str(e)}")

        raise HTTPException(
            status_code=500,
            detail="SQL execution failed"
        )