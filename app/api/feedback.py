from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.schemas.feedback import (
    FeedbackCreate,
    FeedbackResponse,
)
from app.services.feedback_service import (
    create_feedback,
    get_feedback,
    get_feedback_list,
    get_transaction_feedback,
)


router = APIRouter(
    prefix="/feedback",
    tags=["Feedback"],
)


# ==========================================================
# Create Feedback
# ==========================================================

@router.post(
    "",
    response_model=FeedbackResponse,
    status_code=201,
)
def create_feedback_endpoint(
    feedback: FeedbackCreate,
    db: Session = Depends(get_db),
):

    return create_feedback(
        db=db,
        feedback_data=feedback,
    )


# ==========================================================
# Get Feedback by ID
# ==========================================================

@router.get(
    "/{feedback_id}",
    response_model=FeedbackResponse,
)
def get_feedback_endpoint(
    feedback_id: int,
    db: Session = Depends(get_db),
):

    feedback = get_feedback(
        db=db,
        feedback_id=feedback_id,
    )

    if not feedback:

        raise HTTPException(
            status_code=404,
            detail="Feedback not found.",
        )

    return feedback


# ==========================================================
# Get Feedback for Transaction
# ==========================================================

@router.get(
    "/transaction/{transaction_id}",
    response_model=list[FeedbackResponse],
)
def get_transaction_feedback_endpoint(
    transaction_id: str,
    db: Session = Depends(get_db),
):

    return get_transaction_feedback(
        db=db,
        transaction_id=transaction_id,
    )


# ==========================================================
# Get All Feedback
# ==========================================================

@router.get(
    "",
    response_model=list[FeedbackResponse],
)
def get_feedback_list_endpoint(
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

    return get_feedback_list(
        db=db,
        skip=skip,
        limit=limit,
    )