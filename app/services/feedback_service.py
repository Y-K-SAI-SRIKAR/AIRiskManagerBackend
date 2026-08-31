from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.feedback import Feedback
from app.models.transaction import Transaction
from app.schemas.feedback import FeedbackCreate


# ==========================================================
# Create Feedback
# ==========================================================

def create_feedback(
    db: Session,
    feedback_data: FeedbackCreate,
) -> Feedback:

    # ------------------------------------------------------
    # Verify transaction exists
    # ------------------------------------------------------

    transaction = db.scalar(
        select(Transaction).where(
            Transaction.transaction_id
            == feedback_data.transaction_id
        )
    )

    if not transaction:
        raise ValueError(
            "Transaction not found."
        )

    # ------------------------------------------------------
    # Build feedback
    # ------------------------------------------------------

    feedback = Feedback(
        transaction_id=feedback_data.transaction_id,
        customer_id=feedback_data.customer_id,
        original_prediction=feedback_data.original_prediction,
        actual_outcome=feedback_data.actual_outcome,
        feedback_type=feedback_data.feedback_type,
        reviewer_decision=feedback_data.reviewer_decision,
        reason=feedback_data.reason,
    )

    # ------------------------------------------------------
    # Persist safely
    # ------------------------------------------------------

    try:

        db.add(feedback)

        db.commit()

        db.refresh(feedback)

        return feedback

    except IntegrityError as exc:

        db.rollback()

        raise ValueError(
            "Feedback could not be created because "
            "a database constraint was violated."
        ) from exc

    except Exception:

        db.rollback()

        raise


# ==========================================================
# Get Feedback by ID
# ==========================================================

def get_feedback(
    db: Session,
    feedback_id: int,
) -> Feedback | None:

    return db.scalar(
        select(Feedback).where(
            Feedback.id == feedback_id
        )
    )


# ==========================================================
# Get Feedback for Transaction
# ==========================================================

def get_transaction_feedback(
    db: Session,
    transaction_id: str,
) -> list[Feedback]:

    return list(
        db.scalars(
            select(Feedback)
            .where(
                Feedback.transaction_id
                == transaction_id
            )
            .order_by(
                Feedback.created_at.desc()
            )
        )
    )


# ==========================================================
# Get All Feedback
# ==========================================================

def get_feedback_list(
    db: Session,
    skip: int = 0,
    limit: int = 100,
) -> list[Feedback]:

    return list(
        db.scalars(
            select(Feedback)
            .order_by(
                Feedback.created_at.desc()
            )
            .offset(skip)
            .limit(limit)
        )
    )