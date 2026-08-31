from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


# ==========================================================
# Single Analysis
# ==========================================================


class AnalysisDecisionResponse(BaseModel):
    risk_level: str | None = None
    action: str | None = None
    confidence: float | None = None


class AnalysisEvidenceResponse(BaseModel):
    ml_risk_score: float | None = None
    anomaly_detected: bool | None = None
    velocity_risk: float | None = None
    customer_risk: float | None = None
    transaction_risk: float | None = None
    triggered_rules: list[Any] = []


class AnalysisResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True
    )

    id: int
    transaction_id: str
    customer_id: str
    success: bool

    decision: AnalysisDecisionResponse

    evidence: AnalysisEvidenceResponse

    explanation: str | None = None

    metadata: dict[str, Any] = {}

    created_at: datetime
    updated_at: datetime


class AnalysisDetailResponse(BaseModel):
    success: bool
    analysis: AnalysisResponse


# ==========================================================
# Single Analysis List Item
# ==========================================================


class AnalysisListItemResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True
    )

    id: int
    transaction_id: str
    customer_id: str
    success: bool

    risk_level: str | None = None
    action: str | None = None

    confidence: float | None = None
    ml_risk_score: float | None = None

    created_at: datetime
    updated_at: datetime


class AnalysisListResponse(BaseModel):
    success: bool
    count: int
    analyses: list[AnalysisListItemResponse]


# ==========================================================
# Batch Analysis
# ==========================================================


class BatchAnalysisSummaryResponse(BaseModel):
    total_transactions: int | None = None
    fraud_transactions: int | None = None
    legitimate_transactions: int | None = None

    fraud_rate: float | None = None
    average_fraud_probability: float | None = None
    production_threshold: float | None = None


class BatchAnalysisModelResponse(BaseModel):
    name: str | None = None
    alias: str | None = None
    version: int | None = None
    type: str | None = None

    xgb_weight: float | None = None
    nn_weight: float | None = None


class BatchAnalysisArtifactsResponse(BaseModel):
    result_download_url: str | None = None
    report_download_url: str | None = None


class BatchAnalysisResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True
    )

    id: int
    batch_id: str
    job_id: str | None = None

    transaction_count: int

    success: bool
    status: str | None = None

    summary: BatchAnalysisSummaryResponse

    model: BatchAnalysisModelResponse

    input_s3_location: str | None = None

    artifacts: BatchAnalysisArtifactsResponse

    metadata: dict[str, Any] = {}

    created_at: datetime
    updated_at: datetime


class BatchAnalysisDetailResponse(BaseModel):
    success: bool
    analysis: BatchAnalysisResponse


# ==========================================================
# Batch Analysis List Item
# ==========================================================


class BatchAnalysisListItemResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True
    )

    id: int
    batch_id: str
    job_id: str | None = None

    transaction_count: int

    success: bool
    status: str | None = None

    fraud_transactions: int | None = None
    legitimate_transactions: int | None = None

    fraud_rate: float | None = None
    average_fraud_probability: float | None = None

    model_name: str | None = None
    model_alias: str | None = None
    model_version: int | None = None

    created_at: datetime
    updated_at: datetime


class BatchAnalysisListResponse(BaseModel):
    success: bool
    count: int
    analyses: list[BatchAnalysisListItemResponse]