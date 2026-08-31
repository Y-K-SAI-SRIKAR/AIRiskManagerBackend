from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, ForeignKey, Integer, JSON, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database.connection import Base


class AnalysisResult(Base):
    __tablename__ = "analysis_results"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    transaction_id: Mapped[str] = mapped_column(
        String(100),
        ForeignKey("transactions.transaction_id"),
        nullable=False,
        unique=True,
        index=True,
    )

    customer_id: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )

    success: Mapped[bool] = mapped_column(
        nullable=False,
    )

    risk_level: Mapped[str | None] = mapped_column(
        String(30),
        nullable=True,
        index=True,
    )

    action: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    confidence: Mapped[float | None] = mapped_column(
        Numeric,
        nullable=True,
    )

    ml_risk_score: Mapped[float | None] = mapped_column(
        Numeric,
        nullable=True,
    )

    anomaly_detected: Mapped[bool | None] = mapped_column(
        nullable=True,
    )

    velocity_risk: Mapped[float | None] = mapped_column(
        Numeric,
        nullable=True,
    )

    customer_risk: Mapped[float | None] = mapped_column(
        Numeric,
        nullable=True,
    )

    transaction_risk: Mapped[float | None] = mapped_column(
        Numeric,
        nullable=True,
    )

    triggered_rules: Mapped[list[Any]] = mapped_column(
        JSON,
        nullable=False,
        default=list,
    )

    explanation: Mapped[str | None] = mapped_column(
        String(2000),
        nullable=True,
    )

    analysis_metadata: Mapped[dict[str, Any]] = mapped_column(
        "metadata",
        JSON,
        nullable=False,
        default=dict,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )