from datetime import datetime
from uuid import uuid4

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


# ==========================================================
# Test Helpers
# ==========================================================

def unique_transaction_id() -> str:
    return (
        f"PYTEST-ANALYSIS-"
        f"{uuid4().hex[:12].upper()}"
    )


def unique_batch_id() -> str:
    return (
        f"PYTEST-BATCH-"
        f"{uuid4().hex[:12].upper()}"
    )


def make_analysis_result(
    transaction_id: str,
    customer_id: str = "PYTEST-CUSTOMER-001",
) -> dict:

    return {
        "transaction_id": transaction_id,
        "customer_id": customer_id,
        "success": True,
        "decision": {
            "risk_level": "LOW",
            "action": "APPROVE",
            "confidence": 0.01,
        },
        "evidence": {
            "ml_risk_score": 0.01,
            "anomaly_detected": False,
            "velocity_risk": 0.1,
            "customer_risk": 0.1,
            "transaction_risk": 0.1,
            "triggered_rules": [],
        },
        "explanation": (
            "Automated pytest analysis result."
        ),
        "metadata": {
            "source": "pytest",
        },
    }


def make_batch_result() -> dict:

    return {
        "success": True,
        "job_id": (
            f"PYTEST-JOB-"
            f"{uuid4().hex[:12].upper()}"
        ),
        "status": "completed",
        "summary": {
            "total_transactions": 10,
            "fraud_transactions": 1,
            "legitimate_transactions": 9,
            "fraud_rate": 0.1,
            "average_fraud_probability": 0.15,
            "production_threshold": 0.48,
        },
        "model": {
            "name": "AI-Risk-Manager-XGBoost",
            "alias": "champion",
            "version": 11,
            "type": "XGBoost + Neural Network",
            "xgb_weight": 1,
            "nn_weight": 0,
        },
        "artifacts": {
            "result_download_url": (
                "https://example.com/predictions.csv"
            ),
            "report_download_url": (
                "https://example.com/report.json"
            ),
        },
        "metadata": {
            "source": "pytest",
        },
    }


def create_test_transaction(
    db,
    transaction_id: str,
    customer_id: str = "PYTEST-CUSTOMER-001",
):
    from app.schemas.transaction import TransactionCreate
    from app.services.transaction_service import (
        create_transaction,
    )

    transaction_data = TransactionCreate(
        transaction_id=transaction_id,
        customer_id=customer_id,
        amount=100.0,
        currency="INR",
        merchant_id="PYTEST-MERCHANT-001",
        merchant_category="TEST",
        transaction_type="PURCHASE",
        timestamp=datetime.utcnow(),
        device_id="PYTEST-DEVICE-001",
        ip_address="127.0.0.1",
        location="TEST",
        country="IN",
        channel="ONLINE",
        features={},
        metadata={
            "source": "pytest",
        },
    )

    return create_transaction(
        db=db,
        transaction_data=transaction_data,
    )


# ==========================================================
# Single Analysis Persistence
# ==========================================================

def test_save_single_analysis():

    transaction_id = unique_transaction_id()

    from app.database.connection import SessionLocal
    from app.services.analysis_service import (
        analysis_service,
    )

    db = SessionLocal()

    try:

        create_test_transaction(
            db=db,
            transaction_id=transaction_id,
        )

        result = make_analysis_result(
            transaction_id=transaction_id
        )

        analysis = analysis_service.save_analysis(
            db=db,
            result=result,
        )

        assert analysis.id is not None
        assert analysis.transaction_id == transaction_id
        assert (
            analysis.customer_id
            == "PYTEST-CUSTOMER-001"
        )
        assert analysis.risk_level == "LOW"
        assert analysis.action == "APPROVE"
        assert analysis.success is True

    finally:

        db.close()


# ==========================================================
# Single Analysis Validation
# ==========================================================

def test_save_analysis_missing_transaction_id():

    from app.database.connection import SessionLocal
    from app.services.analysis_service import (
        analysis_service,
    )

    db = SessionLocal()

    try:

        result = make_analysis_result(
            transaction_id=unique_transaction_id()
        )

        del result["transaction_id"]

        try:

            analysis_service.save_analysis(
                db=db,
                result=result,
            )

            assert False, (
                "Expected ValueError"
            )

        except ValueError as exc:

            assert (
                "missing transaction_id"
                in str(exc)
            )

    finally:

        db.close()


def test_save_analysis_missing_customer_id():

    from app.database.connection import SessionLocal
    from app.services.analysis_service import (
        analysis_service,
    )

    db = SessionLocal()

    try:

        result = make_analysis_result(
            transaction_id=unique_transaction_id()
        )

        del result["customer_id"]

        try:

            analysis_service.save_analysis(
                db=db,
                result=result,
            )

            assert False, (
                "Expected ValueError"
            )

        except ValueError as exc:

            assert (
                "missing customer_id"
                in str(exc)
            )

    finally:

        db.close()


# ==========================================================
# Single Analysis Retrieval API
# ==========================================================

def test_get_analysis_api():

    transaction_id = unique_transaction_id()

    from app.database.connection import SessionLocal
    from app.services.analysis_service import (
        analysis_service,
    )

    db = SessionLocal()

    try:

        create_test_transaction(
            db=db,
            transaction_id=transaction_id,
        )

        analysis_service.save_analysis(
            db=db,
            result=make_analysis_result(
                transaction_id=transaction_id
            ),
        )

    finally:

        db.close()

    response = client.get(
        f"/api/v1/analysis/{transaction_id}"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True
    assert (
        data["analysis"]["transaction_id"]
        == transaction_id
    )
    assert (
        data["analysis"]["decision"]["risk_level"]
        == "LOW"
    )
    assert (
        data["analysis"]["decision"]["action"]
        == "APPROVE"
    )


# ==========================================================
# Batch Analysis Persistence
# ==========================================================

def test_save_batch_analysis():

    batch_id = unique_batch_id()

    from app.database.connection import SessionLocal
    from app.services.analysis_service import (
        analysis_service,
    )

    db = SessionLocal()

    try:

        analysis = (
            analysis_service.save_batch_analysis(
                db=db,
                batch_id=batch_id,
                transaction_count=10,
                input_s3_location=(
                    "s3://pytest-bucket/test.csv"
                ),
                result=make_batch_result(),
            )
        )

        assert analysis.id is not None
        assert analysis.batch_id == batch_id
        assert analysis.transaction_count == 10
        assert analysis.success is True
        assert analysis.status == "completed"
        assert analysis.fraud_transactions == 1
        assert analysis.legitimate_transactions == 9
        assert (
            analysis.model_name
            == "AI-Risk-Manager-XGBoost"
        )
        assert analysis.model_alias == "champion"
        assert analysis.model_version == 11

    finally:

        db.close()


# ==========================================================
# Batch Analysis Validation
# ==========================================================

def test_save_batch_analysis_missing_batch_id():

    from app.database.connection import SessionLocal
    from app.services.analysis_service import (
        analysis_service,
    )

    db = SessionLocal()

    try:

        try:

            analysis_service.save_batch_analysis(
                db=db,
                batch_id="",
                transaction_count=10,
                input_s3_location=(
                    "s3://pytest-bucket/test.csv"
                ),
                result=make_batch_result(),
            )

            assert False, (
                "Expected ValueError"
            )

        except ValueError as exc:

            assert (
                "batch_id is required"
                in str(exc)
            )

    finally:

        db.close()


def test_duplicate_batch_analysis():

    batch_id = unique_batch_id()

    from app.database.connection import SessionLocal
    from app.services.analysis_service import (
        analysis_service,
    )

    db = SessionLocal()

    try:

        result = make_batch_result()

        analysis_service.save_batch_analysis(
            db=db,
            batch_id=batch_id,
            transaction_count=10,
            input_s3_location=(
                "s3://pytest-bucket/test.csv"
            ),
            result=result,
        )

        try:

            analysis_service.save_batch_analysis(
                db=db,
                batch_id=batch_id,
                transaction_count=10,
                input_s3_location=(
                    "s3://pytest-bucket/test.csv"
                ),
                result=result,
            )

            assert False, (
                "Expected ValueError"
            )

        except ValueError as exc:

            assert "already exists" in str(exc)

    finally:

        db.close()


# ==========================================================
# Batch Analysis Retrieval API
# ==========================================================

def test_get_batch_analysis_api():

    batch_id = unique_batch_id()

    from app.database.connection import SessionLocal
    from app.services.analysis_service import (
        analysis_service,
    )

    db = SessionLocal()

    try:

        analysis_service.save_batch_analysis(
            db=db,
            batch_id=batch_id,
            transaction_count=10,
            input_s3_location=(
                "s3://pytest-bucket/test.csv"
            ),
            result=make_batch_result(),
        )

    finally:

        db.close()

    response = client.get(
        f"/api/v1/analysis/batches/{batch_id}"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True
    assert (
        data["analysis"]["batch_id"]
        == batch_id
    )
    assert (
        data["analysis"]["transaction_count"]
        == 10
    )
    assert (
        data["analysis"]["status"]
        == "completed"
    )
    assert (
        data["analysis"]["model"]["name"]
        == "AI-Risk-Manager-XGBoost"
    )


# ==========================================================
# Analysis Not Found
# ==========================================================

def test_analysis_not_found():

    response = client.get(
        "/api/v1/analysis/"
        "PYTEST-ANALYSIS-DOES-NOT-EXIST"
    )

    assert response.status_code == 404

    data = response.json()

    assert "Analysis not found" in data["detail"]


def test_batch_analysis_not_found():

    response = client.get(
        "/api/v1/analysis/batches/"
        "PYTEST-BATCH-DOES-NOT-EXIST"
    )

    assert response.status_code == 404

    data = response.json()

    assert (
        "Batch analysis not found"
        in data["detail"]
    )