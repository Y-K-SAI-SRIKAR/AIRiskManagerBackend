from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.database.connection import get_db

from app.schemas.transaction import (
    TransactionCreate,
    TransactionResponse,
    TransactionUpdate,
)

from app.services.transaction_service import (
    create_transaction,
    get_transaction,
    get_transactions,
    update_transaction,
)


router = APIRouter(
    prefix="/transactions",
    tags=["Transactions"],
)


# ==========================================================
# Create Transaction
# ==========================================================

@router.post(
    "",
    response_model=TransactionResponse,
    status_code=201,
)
def create_transaction_endpoint(
    transaction: TransactionCreate,
    db: Session = Depends(get_db),
):

    try:

        return create_transaction(
            db=db,
            transaction_data=transaction,
        )

    except ValueError as exc:

        db.rollback()

        raise HTTPException(
            status_code=409,
            detail=str(exc),
        ) from exc

    except SQLAlchemyError as exc:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=(
                "The transaction could not be saved "
                "because of a database error."
            ),
        ) from exc


# ==========================================================
# Update Transaction
# ==========================================================

@router.patch(
    "/{transaction_id}",
    response_model=TransactionResponse,
)
def update_transaction_endpoint(
    transaction_id: str,
    transaction: TransactionUpdate,
    db: Session = Depends(get_db),
):

    try:

        updated_transaction = update_transaction(
            db=db,
            transaction_id=transaction_id,
            transaction_data=transaction,
        )

    except SQLAlchemyError as exc:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=(
                "The transaction could not be updated "
                "because of a database error."
            ),
        ) from exc

    if updated_transaction is None:

        raise HTTPException(
            status_code=404,
            detail="Transaction not found.",
        )

    return updated_transaction


# ==========================================================
# Get Transaction
# ==========================================================

@router.get(
    "/{transaction_id}",
    response_model=TransactionResponse,
)
def get_transaction_endpoint(
    transaction_id: str,
    db: Session = Depends(get_db),
):

    try:

        transaction = get_transaction(
            db=db,
            transaction_id=transaction_id,
        )

    except SQLAlchemyError as exc:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=(
                "The transaction could not be retrieved "
                "because of a database error."
            ),
        ) from exc

    if transaction is None:

        raise HTTPException(
            status_code=404,
            detail="Transaction not found.",
        )

    return transaction


# ==========================================================
# List Transactions
# ==========================================================

@router.get(
    "",
    response_model=list[TransactionResponse],
)
def get_transactions_endpoint(
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

    try:

        return get_transactions(
            db=db,
            skip=skip,
            limit=limit,
        )

    except SQLAlchemyError as exc:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=(
                "Transactions could not be retrieved "
                "because of a database error."
            ),
        ) from exc