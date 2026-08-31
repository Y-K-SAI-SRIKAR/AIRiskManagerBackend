from datetime import datetime

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


# ==========================================================
# Health
# ==========================================================

def test_health():

    response = client.get("/health")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "ok"
    assert data["service"] == "AI Risk Manager Backend"


# ==========================================================
# Database Health
# ==========================================================

def test_database_health():

    response = client.get("/health/db")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "ok"
    assert data["database"] == "connected"


# ==========================================================
# Agent Health
# ==========================================================

def test_agent_health():

    response = client.get(
        "/api/v1/agent/health"
    )

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, dict)


# ==========================================================
# Transaction API
# ==========================================================

def test_transaction_list_api():

    response = client.get(
        "/api/v1/transactions"
    )

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)


def test_transaction_not_found_api():

    response = client.get(
        "/api/v1/transactions/API-DOES-NOT-EXIST"
    )

    assert response.status_code == 404

    data = response.json()

    assert data["detail"] == "Transaction not found."


# ==========================================================
# Analysis API
# ==========================================================

def test_analysis_list_api():

    response = client.get(
        "/api/v1/analysis"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True
    assert "count" in data
    assert "analyses" in data
    assert isinstance(data["analyses"], list)


def test_analysis_not_found_api():

    response = client.get(
        "/api/v1/analysis/API-DOES-NOT-EXIST"
    )

    assert response.status_code == 404

    data = response.json()

    assert "Analysis not found" in data["detail"]


def test_batch_analysis_list_api():

    response = client.get(
        "/api/v1/analysis/batches"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["success"] is True
    assert "count" in data
    assert "analyses" in data
    assert isinstance(data["analyses"], list)


def test_batch_analysis_not_found_api():

    response = client.get(
        "/api/v1/analysis/batches/API-DOES-NOT-EXIST"
    )

    assert response.status_code == 404

    data = response.json()

    assert "Batch analysis not found" in data["detail"]


# ==========================================================
# Feedback API
# ==========================================================

def test_feedback_list_api():

    response = client.get(
        "/api/v1/feedback"
    )

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)


def test_feedback_not_found_api():

    response = client.get(
        "/api/v1/feedback/999999999"
    )

    assert response.status_code == 404

    data = response.json()

    assert data["detail"] == "Feedback not found."


def test_transaction_feedback_api():

    response = client.get(
        "/api/v1/feedback/transaction/"
        "TXN-28A2CFB46E63"
    )

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)