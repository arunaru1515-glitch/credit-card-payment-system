from pydantic import BaseModel, Field
from typing import Literal


class PaymentCreate(BaseModel):
    card_id: int
    amount: float = Field(gt=0)


class PaymentResponse(BaseModel):
    payment_id: int
    card_id: int
    amount: float
    status: Literal["PENDING", "SUCCESS", "FAILED"]
    message: str