from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


# ==========================================================
# Test Data
# ==========================================================

EXISTING_TRANSACTION_ID = "TXN-28A2CFB46E63"
EXISTING_CUSTOMER_ID = "CUSTOMER-9E08A836DF8D"


def make_feedback(
    transaction_id: str = EXISTING_TRANSACTION_ID,
    customer_id: str = EXISTING_CUSTOMER_ID,
) -> dict:

    return {
        "transaction_id": transaction_id,
        "customer_id": customer_id,
        "original_prediction": "Legitimate",
        "actual_outcome": "Legitimate",
        "feedback_type": "REVIEW",
        "reviewer_decision": "CONFIRMED",
        "reason": "Automated test feedback.",
    }


# ==========================================================
# Create Feedback
# ==========================================================

def test_create_feedback():

    response = client.post(
        "/api/v1/feedback",
        json=make_feedback(),
    )

    assert response.status_code == 201

    data = response.json()

    assert data["transaction_id"] == EXISTING_TRANSACTION_ID
    assert data["customer_id"] == EXISTING_CUSTOMER_ID
    assert data["original_prediction"] == "Legitimate"
    assert data["actual_outcome"] == "Legitimate"
    assert data["feedback_type"] == "REVIEW"
    assert data["reviewer_decision"] == "CONFIRMED"


# ==========================================================
# Create Feedback - Transaction Not Found
# ==========================================================

def test_create_feedback_transaction_not_found():

    response = client.post(
        "/api/v1/feedback",
        json=make_feedback(
            transaction_id="PYTEST-FEEDBACK-NONEXISTENT",
            customer_id="PYTEST-CUSTOMER",
        ),
    )

    assert response.status_code == 404

    data = response.json()

    assert data["detail"] == "Transaction not found."


# ==========================================================
# Create Feedback - Invalid Body
# ==========================================================

def test_create_feedback_invalid_body():

    payload = {
        "customer_id": EXISTING_CUSTOMER_ID,
        "original_prediction": "Legitimate",
        "actual_outcome": "Fraud",
        "feedback_type": "REVIEW",
    }

    response = client.post(
        "/api/v1/feedback",
        json=payload,
    )

    assert response.status_code == 422


# ==========================================================
# Get Feedback by ID
# ==========================================================

def test_get_feedback():

    create_response = client.post(
        "/api/v1/feedback",
        json=make_feedback(),
    )

    assert create_response.status_code == 201

    feedback_id = create_response.json()["id"]

    response = client.get(
        f"/api/v1/feedback/{feedback_id}"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == feedback_id
    assert data["transaction_id"] == EXISTING_TRANSACTION_ID


# ==========================================================
# Get Feedback by Transaction
# ==========================================================

def test_get_transaction_feedback():

    response = client.get(
        "/api/v1/feedback/transaction/"
        f"{EXISTING_TRANSACTION_ID}"
    )

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)

    assert any(
        feedback["transaction_id"]
        == EXISTING_TRANSACTION_ID
        for feedback in data
    )


# ==========================================================
# Get All Feedback
# ==========================================================

def test_get_feedback_list():

    response = client.get(
        "/api/v1/feedback"
    )

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)


# ==========================================================
# Feedback Not Found
# ==========================================================

def test_feedback_not_found():

    response = client.get(
        "/api/v1/feedback/999999999"
    )

    assert response.status_code == 404

    data = response.json()

    assert data["detail"] == "Feedback not found."