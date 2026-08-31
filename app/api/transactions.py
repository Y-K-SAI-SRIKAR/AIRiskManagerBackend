from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.schemas.transaction import (
    TransactionCreate,
    TransactionResponse,
)
from app.services.transaction_service import (
    create_transaction,
    get_transaction,
    get_transactions,
)


router = APIRouter(
    prefix="/transactions",
    tags=["Transactions"],
)


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
        raise HTTPException(
            status_code=409,
            detail=str(exc),
        )


@router.get(
    "/{transaction_id}",
    response_model=TransactionResponse,
)
def get_transaction_endpoint(
    transaction_id: str,
    db: Session = Depends(get_db),
):

    transaction = get_transaction(
        db=db,
        transaction_id=transaction_id,
    )

    if not transaction:
        raise HTTPException(
            status_code=404,
            detail="Transaction not found.",
        )

    return transaction


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

    return get_transactions(
        db=db,
        skip=skip,
        limit=limit,
    )