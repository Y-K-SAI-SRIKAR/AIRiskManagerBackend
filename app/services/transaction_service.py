from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.transaction import Transaction
from app.schemas.transaction import TransactionCreate


# ==========================================================
# CREATE TRANSACTION
# ==========================================================

def create_transaction(
    db: Session,
    transaction_data: TransactionCreate,
) -> Transaction:
    """
    Create and persist a transaction in RDS.

    A transaction_id must be unique.
    """

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

    try:
        db.add(transaction)
        db.commit()
        db.refresh(transaction)

    except Exception:
        db.rollback()
        raise

    return transaction


# ==========================================================
# GET SINGLE TRANSACTION
# ==========================================================

def get_transaction(
    db: Session,
    transaction_id: str,
) -> Transaction | None:
    """
    Retrieve a transaction using its transaction_id.
    """

    return db.scalar(
        select(Transaction).where(
            Transaction.transaction_id
            == transaction_id
        )
    )


# ==========================================================
# GET TRANSACTIONS
# ==========================================================

def get_transactions(
    db: Session,
    skip: int = 0,
    limit: int = 100,
) -> list[Transaction]:
    """
    Retrieve transactions with pagination.
    """

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


# ==========================================================
# GET CUSTOMER TRANSACTIONS
# ==========================================================

def get_customer_transactions(
    db: Session,
    customer_id: str,
    skip: int = 0,
    limit: int = 100,
) -> list[Transaction]:
    """
    Retrieve transactions belonging to a customer.
    """

    return list(
        db.scalars(
            select(Transaction)
            .where(
                Transaction.customer_id
                == customer_id
            )
            .order_by(
                Transaction.timestamp.desc()
            )
            .offset(skip)
            .limit(limit)
        )
    )


# ==========================================================
# TRANSACTION EXISTS
# ==========================================================

def transaction_exists(
    db: Session,
    transaction_id: str,
) -> bool:
    """
    Check whether a transaction already exists.
    """

    statement = select(Transaction.id).where(
        Transaction.transaction_id
        == transaction_id
    )

    return db.scalar(statement) is not None