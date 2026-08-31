from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.transaction import Transaction
from app.schemas.transaction import TransactionCreate


# ==========================================================
# Create Transaction
# ==========================================================

def create_transaction(
    db: Session,
    transaction_data: TransactionCreate,
) -> Transaction:

    # ------------------------------------------------------
    # Check for existing transaction
    # ------------------------------------------------------

    existing_transaction = db.scalar(
        select(Transaction).where(
            Transaction.transaction_id
            == transaction_data.transaction_id
        )
    )

    if existing_transaction:
        raise ValueError(
            "Transaction already exists."
        )

    # ------------------------------------------------------
    # Build transaction
    # ------------------------------------------------------

    transaction = Transaction(
        transaction_id=transaction_data.transaction_id,
        customer_id=transaction_data.customer_id,
        amount=transaction_data.amount,
        currency=transaction_data.currency,
        merchant_id=transaction_data.merchant_id,
        merchant_category=transaction_data.merchant_category,
        transaction_type=transaction_data.transaction_type,
        timestamp=transaction_data.timestamp,
        device_id=transaction_data.device_id,
        ip_address=transaction_data.ip_address,
        location=transaction_data.location,
        country=transaction_data.country,
        channel=transaction_data.channel,
        features=transaction_data.features,
        transaction_metadata=transaction_data.metadata,
    )

    # ------------------------------------------------------
    # Persist safely
    # ------------------------------------------------------

    try:
        db.add(transaction)

        db.commit()

        db.refresh(transaction)

        return transaction

    except IntegrityError as exc:
        db.rollback()

        raise ValueError(
            "Transaction could not be created because "
            "the transaction_id already exists or a "
            "database constraint was violated."
        ) from exc

    except Exception:
        db.rollback()
        raise


# ==========================================================
# Get Single Transaction
# ==========================================================

def get_transaction(
    db: Session,
    transaction_id: str,
) -> Transaction | None:

    return db.scalar(
        select(Transaction).where(
            Transaction.transaction_id
            == transaction_id
        )
    )


# ==========================================================
# Get Transactions
# ==========================================================

def get_transactions(
    db: Session,
    skip: int = 0,
    limit: int = 100,
) -> list[Transaction]:

    return list(
        db.scalars(
            select(Transaction)
            .order_by(
                Transaction.created_at.desc()
            )
            .offset(skip)
            .limit(limit)
        )
    )