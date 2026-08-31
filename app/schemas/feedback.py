from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class FeedbackCreate(BaseModel):
    transaction_id: str = Field(
        min_length=1,
        max_length=100,
    )

    customer_id: str = Field(
        min_length=1,
        max_length=100,
    )

    original_prediction: str = Field(
        min_length=1,
        max_length=50,
    )

    actual_outcome: str = Field(
        min_length=1,
        max_length=50,
    )

    feedback_type: str = Field(
        min_length=1,
        max_length=50,
    )

    reviewer_decision: str | None = Field(
        default=None,
        max_length=50,
    )

    reason: str | None = Field(
        default=None,
        max_length=2000,
    )


class FeedbackResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: int
    transaction_id: str
    customer_id: str
    original_prediction: str
    actual_outcome: str
    feedback_type: str
    reviewer_decision: str | None
    reason: str | None
    created_at: datetime
    updated_at: datetime