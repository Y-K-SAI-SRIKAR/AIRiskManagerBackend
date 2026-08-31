import uuid
from datetime import datetime, timedelta
from typing import Any

from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    Query,
    UploadFile,
    status,
)
from sqlalchemy.orm import Session

from app.database.connection import get_db

from app.services.agent_service import agent_service
from app.services.analysis_service import analysis_service
from app.services.csv_service import csv_service
from app.services.s3_service import s3_service
from app.services.transaction_service import create_transaction

from app.schemas.transaction import TransactionCreate


router = APIRouter(
    prefix="",
    tags=["Analysis"],
)


# ==========================================================
# Dataset-only Columns
# ==========================================================

NON_INFERENCE_COLUMNS = {
    "isFraud",
    "TransactionAmt_Bin",
}


# ==========================================================
# Expected ML Features
# ==========================================================

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

    if value is None:
        return None

    value = str(value).strip()

    if value == "":
        return None

    if value.lower() == "true":
        return True

    if value.lower() == "false":
        return False

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

    actual_columns = set(row.keys())

    missing = (
        EXPECTED_ML_FEATURES
        - actual_columns
    )

    if missing:
        raise ValueError(
            INVALID_CSV_FORMAT
        )

    unexpected = (
        actual_columns
        - EXPECTED_ML_FEATURES
        - NON_INFERENCE_COLUMNS
    )

    if unexpected:
        raise ValueError(
            INVALID_CSV_FORMAT
        )

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

    features = _build_ml_features(row)

    # ------------------------------------------------------
    # Amount
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
    # Generated identifiers
    # ------------------------------------------------------

    transaction_id = (
        f"TXN-{uuid.uuid4().hex[:12].upper()}"
    )

    customer_id = (
        f"CUSTOMER-{uuid.uuid4().hex[:12].upper()}"
    )

    # ------------------------------------------------------
    # Timestamp
    # ------------------------------------------------------

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
    # Agent payload
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
# SINGLE TRANSACTION ANALYSIS
# ==========================================================

@router.post(
    "/analyze",
    status_code=status.HTTP_200_OK,
)
async def analyze_single(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):

    # ------------------------------------------------------
    # Validate file
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

    file_content = await file.read()

    if not file_content:
        raise HTTPException(
            status_code=400,
            detail="Uploaded CSV file is empty.",
        )

    try:

        # --------------------------------------------------
        # Validate exactly one transaction
        # --------------------------------------------------

        row = csv_service.validate_single(
            file_content
        )

        # --------------------------------------------------
        # Build Agent transaction
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
        # Save original CSV to S3
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
        # Call Agent
        # --------------------------------------------------

        result = await agent_service.analyze(
            transaction=agent_transaction
        )

        # --------------------------------------------------
        # Persist transaction
        # --------------------------------------------------

        transaction_data = TransactionCreate(
            **agent_transaction
        )

        create_transaction(
            db=db,
            transaction_data=transaction_data,
        )

        # --------------------------------------------------
        # Persist analysis
        # --------------------------------------------------

        analysis_service.save_analysis(
            db=db,
            result=result,
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

        db.rollback()

        raise HTTPException(
            status_code=502,
            detail=f"Analysis failed: {exc}",
        ) from exc


# ==========================================================
# BATCH TRANSACTION ANALYSIS
# ==========================================================

@router.post(
    "/analyze/batch",
    status_code=status.HTTP_200_OK,
)
async def analyze_batch(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):

    # ------------------------------------------------------
    # Validate file
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
        # Validate ML schema
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
        # Upload original CSV
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
        # Call Agent batch endpoint
        # --------------------------------------------------

        result = (
            await agent_service.analyze_batch(
                file_content=file_content,
                filename=file.filename,
            )
        )

        # --------------------------------------------------
        # Persist batch analysis
        # --------------------------------------------------

        analysis_service.save_batch_analysis(
            db=db,
            batch_id=batch_id,
            transaction_count=len(
                transactions
            ),
            input_s3_location=s3_location,
            result=result,
        )

        # --------------------------------------------------
        # Return response
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

        db.rollback()

        raise HTTPException(
            status_code=502,
            detail=f"Batch analysis failed: {exc}",
        ) from exc


# ==========================================================
# LIST SINGLE ANALYSES
# ==========================================================

@router.get(
    "/analysis",
    tags=["Analysis"],
)
def list_analyses(
    skip: int = Query(
        default=0,
        ge=0,
    ),
    limit: int = Query(
        default=100,
        ge=1,
        le=500,
    ),
    db: Session = Depends(get_db),
):

    analyses = analysis_service.get_analyses(
        db=db,
        skip=skip,
        limit=limit,
    )

    return {
        "success": True,
        "count": len(analyses),

        "analyses": [
            {
                "id": analysis.id,
                "transaction_id": analysis.transaction_id,
                "customer_id": analysis.customer_id,
                "success": analysis.success,
                "risk_level": analysis.risk_level,
                "action": analysis.action,

                "confidence": (
                    float(analysis.confidence)
                    if analysis.confidence is not None
                    else None
                ),

                "ml_risk_score": (
                    float(analysis.ml_risk_score)
                    if analysis.ml_risk_score is not None
                    else None
                ),

                "created_at": analysis.created_at,
                "updated_at": analysis.updated_at,
            }
            for analysis in analyses
        ],
    }


# ==========================================================
# LIST BATCH ANALYSES
# ==========================================================

@router.get(
    "/analysis/batches",
    tags=["Analysis"],
)
def list_batch_analyses(
    skip: int = Query(
        default=0,
        ge=0,
    ),
    limit: int = Query(
        default=100,
        ge=1,
        le=500,
    ),
    db: Session = Depends(get_db),
):

    analyses = analysis_service.get_batch_analyses(
        db=db,
        skip=skip,
        limit=limit,
    )

    return {
        "success": True,
        "count": len(analyses),

        "analyses": [
            {
                "id": analysis.id,
                "batch_id": analysis.batch_id,
                "job_id": analysis.job_id,

                "transaction_count": (
                    analysis.transaction_count
                ),

                "success": analysis.success,
                "status": analysis.status,

                "fraud_transactions": (
                    analysis.fraud_transactions
                ),

                "legitimate_transactions": (
                    analysis.legitimate_transactions
                ),

                "fraud_rate": (
                    float(analysis.fraud_rate)
                    if analysis.fraud_rate is not None
                    else None
                ),

                "average_fraud_probability": (
                    float(
                        analysis.average_fraud_probability
                    )
                    if analysis.average_fraud_probability
                    is not None
                    else None
                ),

                "model_name": analysis.model_name,
                "model_alias": analysis.model_alias,
                "model_version": analysis.model_version,

                "created_at": analysis.created_at,
                "updated_at": analysis.updated_at,
            }
            for analysis in analyses
        ],
    }


# ==========================================================
# GET BATCH ANALYSIS
# ==========================================================

@router.get(
    "/analysis/batches/{batch_id}",
    tags=["Analysis"],
)
def get_batch_analysis(
    batch_id: str,
    db: Session = Depends(get_db),
):

    analysis = analysis_service.get_batch_analysis(
        db=db,
        batch_id=batch_id,
    )

    if analysis is None:

        raise HTTPException(
            status_code=404,
            detail=(
                f"Batch analysis not found for "
                f"'{batch_id}'."
            ),
        )

    return {
        "success": True,

        "analysis": {
            "id": analysis.id,

            "batch_id": analysis.batch_id,

            "job_id": analysis.job_id,

            "transaction_count": (
                analysis.transaction_count
            ),

            "success": analysis.success,

            "status": analysis.status,

            "summary": {
                "total_transactions": (
                    analysis.total_transactions
                ),

                "fraud_transactions": (
                    analysis.fraud_transactions
                ),

                "legitimate_transactions": (
                    analysis.legitimate_transactions
                ),

                "fraud_rate": (
                    float(analysis.fraud_rate)
                    if analysis.fraud_rate is not None
                    else None
                ),

                "average_fraud_probability": (
                    float(
                        analysis.average_fraud_probability
                    )
                    if analysis.average_fraud_probability
                    is not None
                    else None
                ),

                "production_threshold": (
                    float(
                        analysis.production_threshold
                    )
                    if analysis.production_threshold
                    is not None
                    else None
                ),
            },

            "model": {
                "name": analysis.model_name,

                "alias": analysis.model_alias,

                "version": analysis.model_version,

                "type": analysis.model_type,

                "xgb_weight": (
                    float(analysis.xgb_weight)
                    if analysis.xgb_weight is not None
                    else None
                ),

                "nn_weight": (
                    float(analysis.nn_weight)
                    if analysis.nn_weight is not None
                    else None
                ),
            },

            "input_s3_location": (
                analysis.input_s3_location
            ),

            "artifacts": {
                "result_download_url": (
                    analysis.result_download_url
                ),

                "report_download_url": (
                    analysis.report_download_url
                ),
            },

            "metadata": analysis.analysis_metadata,

            "created_at": analysis.created_at,

            "updated_at": analysis.updated_at,
        },
    }


# ==========================================================
# GET SINGLE ANALYSIS
# ==========================================================

@router.get(
    "/analysis/{transaction_id}",
    tags=["Analysis"],
)
def get_single_analysis(
    transaction_id: str,
    db: Session = Depends(get_db),
):

    analysis = analysis_service.get_analysis(
        db=db,
        transaction_id=transaction_id,
    )

    if analysis is None:

        raise HTTPException(
            status_code=404,
            detail=(
                f"Analysis not found for transaction "
                f"'{transaction_id}'."
            ),
        )

    return {
        "success": True,

        "analysis": {
            "id": analysis.id,

            "transaction_id": (
                analysis.transaction_id
            ),

            "customer_id": (
                analysis.customer_id
            ),

            "success": analysis.success,

            "decision": {
                "risk_level": (
                    analysis.risk_level
                ),

                "action": (
                    analysis.action
                ),

                "confidence": (
                    float(analysis.confidence)
                    if analysis.confidence is not None
                    else None
                ),
            },

            "evidence": {
                "ml_risk_score": (
                    float(
                        analysis.ml_risk_score
                    )
                    if analysis.ml_risk_score
                    is not None
                    else None
                ),

                "anomaly_detected": (
                    analysis.anomaly_detected
                ),

                "velocity_risk": (
                    float(
                        analysis.velocity_risk
                    )
                    if analysis.velocity_risk
                    is not None
                    else None
                ),

                "customer_risk": (
                    float(
                        analysis.customer_risk
                    )
                    if analysis.customer_risk
                    is not None
                    else None
                ),

                "transaction_risk": (
                    float(
                        analysis.transaction_risk
                    )
                    if analysis.transaction_risk
                    is not None
                    else None
                ),

                "triggered_rules": (
                    analysis.triggered_rules
                ),
            },

            "explanation": (
                analysis.explanation
            ),

            "metadata": (
                analysis.analysis_metadata
            ),

            "created_at": (
                analysis.created_at
            ),

            "updated_at": (
                analysis.updated_at
            ),
        },
    }