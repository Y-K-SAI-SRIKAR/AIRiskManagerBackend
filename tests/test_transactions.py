from datetime import datetime
from uuid import uuid4

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)

def unique_transaction_id(prefix: str) -> str:
    return f"PYTEST-{prefix}-{uuid4().hex[:12].upper()}"

def make_transaction(transaction_id: str) -> dict:
    return {
        "transaction_id": transaction_id,
        "customer_id": "TEST_CUSTOMER_001",
        "amount": 1250.50,
        "currency": "INR",
        "merchant_id": "TEST_MERCHANT_001",
        "merchant_category": "retail",
        "transaction_type": "purchase",
        "timestamp": datetime.utcnow().isoformat(),
        "device_id": "TEST_DEVICE_001",
        "ip_address": "192.168.1.10",
        "location": "IN",
        "country": "IN",
        "channel": "online",
        "features": {
            "test_feature": 1
        },
        "metadata": {
            "source": "pytest"
        },
    }


# ==========================================================
# Create Transaction
# ==========================================================

def test_create_transaction():

    transaction_id = unique_transaction_id("CREATE")

    response = client.post(
        "/api/v1/transactions",
        json=make_transaction(transaction_id),
    )

    assert response.status_code == 201

    data = response.json()

    assert data["transaction_id"] == transaction_id
    assert data["customer_id"] == "TEST_CUSTOMER_001"
    assert data["amount"] == 1250.50
    assert data["currency"] == "INR"


# ==========================================================
# Get Transaction
# ==========================================================

def test_get_transaction():

    transaction_id = unique_transaction_id("GET")

    create_response = client.post(
        "/api/v1/transactions",
        json=make_transaction(transaction_id),
    )

    assert create_response.status_code == 201

    response = client.get(
        f"/api/v1/transactions/{transaction_id}"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["transaction_id"] == transaction_id
    assert data["customer_id"] == "TEST_CUSTOMER_001"


# ==========================================================
# List Transactions
# ==========================================================

def test_get_transactions():

    response = client.get(
        "/api/v1/transactions"
    )

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)


# ==========================================================
# Duplicate Transaction
# ==========================================================

def test_duplicate_transaction():

    transaction_id = unique_transaction_id("DUPLICATE")

    first_response = client.post(
        "/api/v1/transactions",
        json=make_transaction(transaction_id),
    )

    assert first_response.status_code == 201

    second_response = client.post(
        "/api/v1/transactions",
        json=make_transaction(transaction_id),
    )

    assert second_response.status_code == 409

    data = second_response.json()

    assert "already exists" in data["detail"].lower()


# ==========================================================
# Transaction Not Found
# ==========================================================

def test_transaction_not_found():

    response = client.get(
        "/api/v1/transactions/PYTEST-DOES-NOT-EXIST"
    )

    assert response.status_code == 404

    data = response.json()

    assert data["detail"] == "Transaction not found."


# ==========================================================
# Invalid Transaction
# ==========================================================

def test_invalid_transaction():

    payload = {
        "transaction_id": "PYTEST-TXN-INVALID-001",
        "customer_id": "TEST_CUSTOMER_001",
        "amount": -100,
        "currency": "INR",
        "timestamp": datetime.utcnow().isoformat(),
    }

    response = client.post(
        "/api/v1/transactions",
        json=payload,
    )

    assert response.status_code == 422
# ==========================================================
# Update Transaction
# ==========================================================

def test_update_transaction():

    transaction_id = unique_transaction_id("UPDATE")

    create_response = client.post(
        "/api/v1/transactions",
        json=make_transaction(transaction_id),
    )

    assert create_response.status_code == 201

    update_response = client.patch(
        f"/api/v1/transactions/{transaction_id}",
        json={
            "amount": 2500.75,
        },
    )

    assert update_response.status_code == 200

    data = update_response.json()

    assert data["transaction_id"] == transaction_id
    assert data["amount"] == 2500.75
    assert data["customer_id"] == "TEST_CUSTOMER_001"


# ==========================================================
# Update Multiple Transaction Fields
# ==========================================================

def test_update_transaction_multiple_fields():

    transaction_id = unique_transaction_id("UPDATE-MULTIPLE")

    create_response = client.post(
        "/api/v1/transactions",
        json=make_transaction(transaction_id),
    )

    assert create_response.status_code == 201

    update_response = client.patch(
        f"/api/v1/transactions/{transaction_id}",
        json={
            "amount": 5000,
            "merchant_category": "electronics",
            "channel": "mobile",
        },
    )

    assert update_response.status_code == 200

    data = update_response.json()

    assert data["amount"] == 5000
    assert data["merchant_category"] == "electronics"
    assert data["channel"] == "mobile"

    # Unchanged fields should remain unchanged
    assert data["customer_id"] == "TEST_CUSTOMER_001"
    assert data["currency"] == "INR"


# ==========================================================
# Update Transaction Not Found
# ==========================================================

def test_update_transaction_not_found():

    response = client.patch(
        "/api/v1/transactions/PYTEST-DOES-NOT-EXIST",
        json={
            "amount": 5000,
        },
    )

    assert response.status_code == 404

    data = response.json()

    assert data["detail"] == "Transaction not found."