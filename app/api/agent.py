from fastapi import APIRouter

from app.schemas.transaction import TransactionCreate
from app.services.agent_service import agent_service


router = APIRouter(
    prefix="/agent",
    tags=["Agent"],
)


@router.get("/health")
async def agent_health():
    return await agent_service.health()


@router.post("/analyze")
async def analyze_transaction(
    transaction: TransactionCreate,
):
    return await agent_service.analyze_transaction(
        transaction.model_dump(mode="json")
    )