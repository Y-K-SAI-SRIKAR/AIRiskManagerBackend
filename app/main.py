from fastapi import FastAPI
from sqlalchemy import text

from app.config import (
    APP_NAME,
    APP_VERSION,
)
from app.database.connection import engine
from app.api.transactions import router as transactions_router


app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
)


app.include_router(
    transactions_router,
    prefix="/api/v1",
)


@app.get(
    "/health",
    tags=["Health"],
)
def health():

    return {
        "status": "ok",
        "service": "AI Risk Manager Backend",
    }


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