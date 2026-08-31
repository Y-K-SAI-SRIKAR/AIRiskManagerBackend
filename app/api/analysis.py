import uuid

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
# Single Transaction Analysis
# ==========================================================

@router.post("/analyze")
async def analyze_single(
    file: UploadFile = File(...),
):
    """
    Analyze a single transaction from a CSV file.

    Flow:
        Frontend
            ↓
        Backend
            ↓
        Validate CSV
            ↓
        Upload CSV to Backend S3
            ↓
        Generate presigned URL
            ↓
        Agent /analyze
            ↓
        Agent → ML /predict
            ↓
        Return Agent response
    """

    # ------------------------------------------------------
    # Validate filename
    # ------------------------------------------------------

    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File name is required.",
        )

    # ------------------------------------------------------
    # Validate file type
    # ------------------------------------------------------

    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only CSV files are supported.",
        )

    # ------------------------------------------------------
    # Read uploaded file
    # ------------------------------------------------------

    file_content = await file.read()

    if not file_content:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty.",
        )

    try:
        # --------------------------------------------------
        # Validate single transaction CSV
        # --------------------------------------------------

        transaction = csv_service.validate_single(
            file_content
        )

        transaction_id = transaction[
            "transaction_id"
        ]

        # --------------------------------------------------
        # Upload original CSV to S3
        # --------------------------------------------------

        (
            s3_location,
            download_url,
        ) = s3_service.upload_transaction_file(
            transaction_id=transaction_id,
            file_content=file_content,
            filename="transaction.csv",
            content_type="text/csv",
        )

        # --------------------------------------------------
        # Send S3 URL to Agent
        # --------------------------------------------------

        result = await agent_service.analyze(
            file_url=download_url,
        )

        # --------------------------------------------------
        # Return result
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
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    except Exception as exc:

        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Analysis failed: {str(exc)}",
        ) from exc


# ==========================================================
# Batch Transaction Analysis
# ==========================================================

@router.post("/analyze/batch")
async def analyze_batch(
    file: UploadFile = File(...),
):
    """
    Analyze multiple transactions from a CSV file.

    Flow:
        Frontend
            ↓
        Backend
            ↓
        Validate CSV
            ↓
        Generate batch ID
            ↓
        Upload CSV to Backend S3
            ↓
        Generate presigned URL
            ↓
        Agent /analyze/batch
            ↓
        Agent → ML /predict/batch
            ↓
        Agent Reports S3
            ↓
        Return report/prediction URLs
    """

    # ------------------------------------------------------
    # Validate filename
    # ------------------------------------------------------

    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File name is required.",
        )

    # ------------------------------------------------------
    # Validate file type
    # ------------------------------------------------------

    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only CSV files are supported.",
        )

    # ------------------------------------------------------
    # Read uploaded file
    # ------------------------------------------------------

    file_content = await file.read()

    if not file_content:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty.",
        )

    try:
        # --------------------------------------------------
        # Validate batch CSV
        # --------------------------------------------------

        transactions = csv_service.validate_batch(
            file_content
        )

        # --------------------------------------------------
        # Generate unique batch ID
        # --------------------------------------------------

        batch_id = (
            f"BATCH-{uuid.uuid4().hex}"
        )

        # --------------------------------------------------
        # Upload original CSV to S3
        # --------------------------------------------------

        (
            s3_location,
            download_url,
        ) = s3_service.upload_batch_file(
            batch_id=batch_id,
            file_content=file_content,
            filename="transactions.csv",
            content_type="text/csv",
        )

        # --------------------------------------------------
        # Send S3 URL to Agent
        # --------------------------------------------------

        result = await agent_service.analyze_batch(
            file_url=download_url,
        )

        # --------------------------------------------------
        # Return Agent response
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
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    except Exception as exc:

        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Batch analysis failed: {str(exc)}",
        ) from exc