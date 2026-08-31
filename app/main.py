from fastapi import FastAPI
from sqlalchemy import text

from app.config import (
    APP_NAME,
    APP_VERSION,
)

from app.database.connection import engine

from app.api.transactions import (
    router as transactions_router,
)

from app.api.agent import (
    router as agent_router,
)

from app.api.analysis import (
    router as analysis_router,
)

from app.api.feedback import (
    router as feedback_router,
)

# ==========================================================
# FastAPI Application
# ==========================================================

app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
)


# ==========================================================
# API Routers
# ==========================================================

# Transaction CRUD
app.include_router(
    transactions_router,
    prefix="/api/v1",
)


# Agent health / integration
app.include_router(
    agent_router,
    prefix="/api/v1",
)


# Single + Batch analysis
app.include_router(
    analysis_router,
    prefix="/api/v1",
)

# Feedback persistence
app.include_router(
    feedback_router,
    prefix="/api/v1",
)

# ==========================================================
# Application Health
# ==========================================================

@app.get(
    "/health",
    tags=["Health"],
)
def health():

    return {
        "status": "ok",
        "service": "AI Risk Manager Backend",
    }


# ==========================================================
# Database Health
# ==========================================================

@app.get(
    "/health/db",
    tags=["Health"],
)
def database_health():

    try:

        with engine.connect() as connection:

            connection.execute(
                text("SELECT 1")
            )

        return {
            "status": "ok",
            "database": "connected",
        }

    except Exception as exc:

        return {
            "status": "error",
            "database": "disconnected",
            "detail": str(exc),
        }