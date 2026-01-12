from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.payments.service import create_payment_intent

router = APIRouter(prefix="/payments", tags=["payments"])

class CreatePaymentRequest(BaseModel):
    amount: int
    currency: str
    order_id: str
    email: str | None = None

@router.post("/create")
def create_payment(req: CreatePaymentRequest):
    try:
        intent = create_payment_intent(
            amount=req.amount,
            currency=req.currency,
            order_id=req.order_id,
            customer_email=req.email,
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {
        "client_secret": intent.client_secret
    }