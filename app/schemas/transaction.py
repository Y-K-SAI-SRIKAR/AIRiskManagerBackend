from datetime import datetime
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class TransactionCreate(BaseModel):

    model_config = ConfigDict(
        extra="forbid"
    )

    transaction_id: str = Field(
        ...,
        min_length=1,
        max_length=100,
    )

    customer_id: str = Field(
        ...,
        min_length=1,
        max_length=100,
    )

    amount: float = Field(
        ...,
        gt=0,
    )

    currency: str = Field(
        default="INR",
        min_length=3,
        max_length=3,
    )

    merchant_id: str | None = None

    merchant_category: str | None = None

    transaction_type: str | None = None

    timestamp: datetime

    device_id: str | None = None

    ip_address: str | None = None

    location: str | None = None

    country: str | None = None

    channel: str | None = None

    features: dict[str, Any] = Field(
        default_factory=dict
    )

    metadata: dict[str, Any] = Field(
        default_factory=dict
    )


class TransactionResponse(BaseModel):

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
    )

    id: int

    transaction_id: str

    customer_id: str

    amount: float

    currency: str

    merchant_id: str | None

    merchant_category: str | None

    transaction_type: str | None

    timestamp: datetime

    device_id: str | None

    ip_address: str | None

    location: str | None

    country: str | None

    channel: str | None

    features: dict[str, Any]

    metadata: dict[str, Any] = Field(
        validation_alias="transaction_metadata",
        serialization_alias="metadata",
    )

    created_at: datetime

    updated_at: datetime