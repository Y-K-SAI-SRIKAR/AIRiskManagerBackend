import uuid
from datetime import datetime, timedelta
from typing import Any

from fastapi import (
    APIRouter,
    File,
    HTTPException,
    UploadFile,
    status,
)

from app.services.agent_service import agent_service
from app.services.csv_service import csv_service
from app.services.s3_service import s3_service


router = APIRouter(
    prefix="",
    tags=["Analysis"],
)


# ==========================================================
# Dataset-only Columns
# ==========================================================
#
# These columns may exist in the uploaded CSV dataset,
# but they are NOT required by the ML inference service.
#
# They are accepted by the Backend and ignored when
# constructing the Agent /analyze payload.
#

NON_INFERENCE_COLUMNS = {
    "isFraud",
    "TransactionAmt_Bin",
}


# ==========================================================
# Expected ML Features
# ==========================================================
#
# The deployed ML model expects exactly these 117
# inference features.
#
# The Backend uses this list to construct the features
# object sent to Agent /analyze.
#
# For /analyze/batch, the ORIGINAL CSV is forwarded
# directly to the Agent.
#

EXPECTED_ML_FEATURES = {
    "TransactionDT",
    "TransactionAmt",
    "ProductCD",
    "card1",
    "card2",
    "card3",
    "card4",
    "card5",
    "card6",
    "addr1",
    "addr2",
    "dist1",
    "P_emaildomain",
    "R_emaildomain",

    "C2",
    "C3",
    "C9",

    "D1",
    "D3",
    "D5",
    "D11",
    "D15",

    "M1",
    "M2",
    "M3",
    "M4",
    "M5",
    "M6",
    "M7",
    "M8",
    "M9",

    "V1",
    "V3",
    "V5",
    "V6",
    "V12",
    "V14",
    "V20",
    "V23",
    "V26",
    "V29",
    "V35",
    "V38",
    "V41",
    "V45",
    "V47",
    "V52",
    "V53",
    "V56",
    "V62",
    "V65",
    "V67",
    "V68",
    "V83",
    "V86",
    "V89",
    "V107",
    "V111",
    "V117",
    "V120",
    "V123",
    "V169",
    "V173",
    "V174",
    "V197",
    "V199",
    "V220",
    "V222",
    "V223",
    "V235",
    "V239",
    "V240",
    "V247",
    "V257",
    "V262",
    "V271",
    "V281",
    "V283",
    "V284",
    "V286",
    "V287",
    "V289",
    "V290",
    "V301",
    "V302",
    "V305",
    "V312",
    "V315",

    "id_01",
    "id_02",
    "id_05",
    "id_06",
    "id_11",
    "id_12",
    "id_13",
    "id_15",
    "id_16",
    "id_17",
    "id_19",
    "id_20",
    "id_28",
    "id_29",
    "id_31",
    "id_35",
    "id_36",
    "id_37",
    "id_38",

    "TransactionHour",
    "TransactionDay",
    "TransactionWeek",
    "TransactionWeekday",
    "TransactionAmt_Log",
    "card1_freq",
    "EmailDomainMatch",
    "P_email_Missing",
    "R_email_Missing",
    "CardType",
}


# ==========================================================
# Generic User-Facing Error
# ==========================================================
#
# Do not expose internal ML feature names to the frontend.
#

INVALID_CSV_FORMAT = (
    "CSV format is invalid. "
    "Please upload a CSV matching the supported "
    "transaction format."
)


# ==========================================================
# CSV Value Conversion
# ==========================================================

def _convert_value(
    value: Any,
) -> Any:
    """
    Convert a CSV string value into an appropriate
    Python value before sending it to the Agent.
    """

    if value is None:
        return None

    value = str(value).strip()

    if value == "":
        return None

    # Boolean values
    if value.lower() == "true":
        return True

    if value.lower() == "false":
        return False

    # Integer values
    try:
        if (
            value.isdigit()
            or (
                value.startswith("-")
                and value[1:].isdigit()
            )
        ):
            return int(value)

    except Exception:
        pass

    # Float values
    try:
        return float(value)

    except ValueError:
        return value


# ==========================================================
# Build ML Features
# ==========================================================

def _build_ml_features(
    row: dict[str, Any],
) -> dict[str, Any]:
    """
    Extract the 117 ML inference features from one CSV row.

    Accepted dataset-only columns:

        isFraud
        TransactionAmt_Bin

    are ignored.

    Missing or unexpected columns are converted into a
    generic CSV validation error so internal ML schema
    details are not exposed to the client.
    """

    actual_columns = set(row.keys())

    # ------------------------------------------------------
    # Check required ML features
    # ------------------------------------------------------

    missing = (
        EXPECTED_ML_FEATURES
        - actual_columns
    )

    if missing:
        raise ValueError(
            INVALID_CSV_FORMAT
        )

    # ------------------------------------------------------
    # Check unexpected columns
    # ------------------------------------------------------

    unexpected = (
        actual_columns
        - EXPECTED_ML_FEATURES
        - NON_INFERENCE_COLUMNS
    )

    if unexpected:
        raise ValueError(
            INVALID_CSV_FORMAT
        )

    # ------------------------------------------------------
    # Convert feature values
    # ------------------------------------------------------

    features: dict[str, Any] = {}

    for feature in EXPECTED_ML_FEATURES:
        features[feature] = _convert_value(
            row[feature]
        )

    return features


# ==========================================================
# Build Agent Transaction
# ==========================================================

def _build_agent_transaction(
    row: dict[str, Any],
    row_index: int,
) -> dict[str, Any]:
    """
    Convert one model CSV row into the JSON structure
    expected by Agent /analyze.

    The uploaded CSV contains the ML model features.

    The Backend creates the surrounding transaction
    structure required by Agent /analyze.
    """

    features = _build_ml_features(row)

    # ------------------------------------------------------
    # Transaction Amount
    # ------------------------------------------------------

    amount = features.get(
        "TransactionAmt"
    )

    if amount is None:
        raise ValueError(
            INVALID_CSV_FORMAT
        )

    try:
        amount = float(amount)

    except (TypeError, ValueError) as exc:
        raise ValueError(
            INVALID_CSV_FORMAT
        ) from exc

    if amount <= 0:
        raise ValueError(
            INVALID_CSV_FORMAT
        )

    # ------------------------------------------------------
    # Transaction ID
    # ------------------------------------------------------
    #
    # The model CSV does not contain transaction_id.
    # Generate one for the transaction being analyzed.
    #

    transaction_id = (
        f"TXN-{uuid.uuid4().hex[:12].upper()}"
    )

    # ------------------------------------------------------
    # Customer ID
    # ------------------------------------------------------
    #
    # The model CSV does not contain customer_id.
    # Generate one for this analysis.
    #

    customer_id = (
        f"CUSTOMER-{uuid.uuid4().hex[:12].upper()}"
    )

    # ------------------------------------------------------
    # Timestamp
    # ------------------------------------------------------
    #
    # TransactionDT is a relative timestamp from the
    # model dataset.
    #
    # Convert it into a valid datetime expected by
    # TransactionRequest.
    #

    transaction_dt = features.get(
        "TransactionDT"
    )

    if transaction_dt is None:
        raise ValueError(
            INVALID_CSV_FORMAT
        )

    try:
        transaction_dt = float(
            transaction_dt
        )

    except (TypeError, ValueError) as exc:
        raise ValueError(
            INVALID_CSV_FORMAT
        ) from exc

    base_datetime = datetime(
        2026,
        1,
        1,
        0,
        0,
        0,
    )

    timestamp = (
        base_datetime
        + timedelta(
            seconds=transaction_dt
        )
    )

    # ------------------------------------------------------
    # Agent Transaction Payload
    # ------------------------------------------------------

    return {
        "transaction_id": transaction_id,

        "customer_id": customer_id,

        "amount": amount,

        "currency": "INR",

        "merchant_id": None,

        "merchant_category": None,

        "transaction_type": None,

        "timestamp": timestamp.isoformat(),

        "device_id": None,

        "ip_address": None,

        "location": None,

        "country": "IN",

        "channel": None,

        "features": features,

        "metadata": {
            "source": "csv",
            "row_index": row_index,
        },
    }


# ==========================================================
# Single Transaction Analysis
# ==========================================================

@router.post(
    "/analyze",
    status_code=status.HTTP_200_OK,
)
async def analyze_single(
    file: UploadFile = File(...),
):
    """
    Analyze exactly one transaction from a CSV file.

    Expected CSV:

        117 ML inference columns

    Optional:

        isFraud
        TransactionAmt_Bin

    The two optional dataset columns are ignored.
    """

    # ------------------------------------------------------
    # Validate filename
    # ------------------------------------------------------

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="File name is required.",
        )

    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(
            status_code=400,
            detail="Only CSV files are supported.",
        )

    # ------------------------------------------------------
    # Read uploaded file
    # ------------------------------------------------------

    file_content = await file.read()

    if not file_content:
        raise HTTPException(
            status_code=400,
            detail="Uploaded CSV file is empty.",
        )

    try:

        # --------------------------------------------------
        # Validate that exactly one row exists
        # --------------------------------------------------

        row = csv_service.validate_single(
            file_content
        )

        # --------------------------------------------------
        # Build Agent payload
        # --------------------------------------------------

        agent_transaction = (
            _build_agent_transaction(
                row=row,
                row_index=1,
            )
        )

        transaction_id = (
            agent_transaction[
                "transaction_id"
            ]
        )

        # --------------------------------------------------
        # Save ORIGINAL uploaded CSV to S3
        # --------------------------------------------------

        (
            s3_location,
            _download_url,
        ) = s3_service.upload_transaction_file(
            transaction_id=transaction_id,
            file_content=file_content,
            filename=file.filename,
            content_type="text/csv",
        )

        # --------------------------------------------------
        # Call Agent /analyze
        # --------------------------------------------------

        result = await agent_service.analyze(
            transaction=agent_transaction
        )

        # --------------------------------------------------
        # Return response
        # --------------------------------------------------

        return {
            "success": True,

            "transaction_id": transaction_id,

            "input_file": {
                "s3_location": s3_location,
            },

            "analysis": result,
        }

    except ValueError as exc:

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except Exception as exc:

        raise HTTPException(
            status_code=502,
            detail=f"Analysis failed: {exc}",
        ) from exc


# ==========================================================
# Batch Transaction Analysis
# ==========================================================

@router.post(
    "/analyze/batch",
    status_code=status.HTTP_200_OK,
)
async def analyze_batch(
    file: UploadFile = File(...),
):
    """
    Analyze multiple transactions from a CSV file.

    Expected CSV:

        117 ML inference columns

    Optional:

        isFraud
        TransactionAmt_Bin

    The original CSV is forwarded directly to:

        Agent /analyze/batch

    The Backend does NOT call the ML service directly.
    """

    # ------------------------------------------------------
    # Validate filename
    # ------------------------------------------------------

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="File name is required.",
        )

    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(
            status_code=400,
            detail="Only CSV files are supported.",
        )

    # ------------------------------------------------------
    # Read uploaded file
    # ------------------------------------------------------

    file_content = await file.read()

    if not file_content:
        raise HTTPException(
            status_code=400,
            detail="Uploaded CSV file is empty.",
        )

    try:

        # --------------------------------------------------
        # Validate batch CSV
        # --------------------------------------------------

        transactions = (
            csv_service.validate_batch(
                file_content
            )
        )

        # --------------------------------------------------
        # Validate ML schema for every row
        #
        # This happens BEFORE sending the file to Agent.
        #
        # Internal feature names are never returned to
        # the frontend.
        # --------------------------------------------------

        for row in transactions:

            _build_ml_features(row)

        # --------------------------------------------------
        # Generate batch ID
        # --------------------------------------------------

        batch_id = (
            f"BATCH-{uuid.uuid4().hex.upper()}"
        )

        # --------------------------------------------------
        # Store ORIGINAL CSV in S3
        # --------------------------------------------------

        (
            s3_location,
            _download_url,
        ) = s3_service.upload_batch_file(
            batch_id=batch_id,
            file_content=file_content,
            filename=file.filename,
            content_type="text/csv",
        )

        # --------------------------------------------------
        # Send ORIGINAL CSV to Agent
        # --------------------------------------------------
        #
        # Important:
        #
        # Backend does NOT:
        #
        #   - rebuild the CSV
        #   - convert it to JSON
        #   - call ML /predict
        #   - call ML /predict/batch
        #
        # Agent owns the complete batch workflow.
        # --------------------------------------------------

        result = (
            await agent_service.analyze_batch(
                file_content=file_content,
                filename=file.filename,
            )
        )

        # --------------------------------------------------
        # Return Agent response unchanged
        #
        # This preserves:
        #
        #   result_download_url
        #   report_download_url
        #
        # for the frontend.
        # --------------------------------------------------

        return {
            "success": True,

            "batch_id": batch_id,

            "transaction_count": len(
                transactions
            ),

            "input_file": {
                "s3_location": s3_location,
            },

            "analysis": result,
        }

    except ValueError as exc:

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except Exception as exc:

        raise HTTPException(
            status_code=502,
            detail=f"Batch analysis failed: {exc}",
        ) from exc