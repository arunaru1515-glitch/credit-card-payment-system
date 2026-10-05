from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field

from services.payment_service import process_payment


router = APIRouter(
    prefix="/payments",
    tags=["Payments"]
)


security = HTTPBearer()


class PaymentRequest(BaseModel):
    card_id: int
    amount: Decimal = Field(gt=0)


@router.post(
    "/",
    summary="Make Payment"
)
async def make_payment(
    data: PaymentRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    authorization = f"Bearer {credentials.credentials}"

    result = await process_payment(
        card_id=data.card_id,
        amount=data.amount,
        authorization=authorization
    )

    if not result.get("success"):
        raise HTTPException(
            status_code=400,
            detail=result.get(
                "error",
                "Payment processing failed"
            )
        )

    return {
        "message": "Payment processed successfully",
        "payment": result
    }