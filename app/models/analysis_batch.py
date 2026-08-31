from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, Integer, JSON, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database.connection import Base


class AnalysisBatch(Base):
    __tablename__ = "analysis_batches"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    batch_id: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
        index=True,
    )

    job_id: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        index=True,
    )

    transaction_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    success: Mapped[bool] = mapped_column(
        nullable=False,
    )

    status: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    total_transactions: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    fraud_transactions: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    legitimate_transactions: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    fraud_rate: Mapped[float | None] = mapped_column(
        Numeric,
        nullable=True,
    )

    average_fraud_probability: Mapped[float | None] = mapped_column(
        Numeric,
        nullable=True,
    )

    production_threshold: Mapped[float | None] = mapped_column(
        Numeric,
        nullable=True,
    )

    model_name: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    model_alias: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    model_version: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    model_type: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    xgb_weight: Mapped[float | None] = mapped_column(
        Numeric,
        nullable=True,
    )

    nn_weight: Mapped[float | None] = mapped_column(
        Numeric,
        nullable=True,
    )

    input_s3_location: Mapped[str | None] = mapped_column(
        String(1000),
        nullable=True,
    )

    result_download_url: Mapped[str | None] = mapped_column(
        String(3000),
        nullable=True,
    )

    report_download_url: Mapped[str | None] = mapped_column(
        String(3000),
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