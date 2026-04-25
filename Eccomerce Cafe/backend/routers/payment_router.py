import mercadopago
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import os
from dotenv import load_dotenv

load_dotenv()

router = APIRouter(prefix="/payments", tags=["payments"])

sdk = mercadopago.SDK(os.getenv("MERCADOPAGO_ACCESS_TOKEN"))

class PaymentRequest(BaseModel):
    token: str
    issuer_id: str
    payment_method_id: str
    transaction_amount: float
    installments: int
    description: str
    payer_email: str

@router.post("/process")
def process_payment(request: PaymentRequest):
    payment_data = {
        "transaction_amount": request.transaction_amount,
        "token": request.token,
        "description": request.description,
        "installments": request.installments,
        "payment_method_id": request.payment_method_id,
        "issuer_id": request.issuer_id,
        "payer": {
            "email": request.payer_email
        }
    }

    try:
        payment_response = sdk.payment().create(payment_data)
        payment = payment_response["response"]

        if payment_response["status"] >= 400:
            return {
                "status": "error",
                "message": payment.get("message", "Error procesando el pago"),
                "detail": payment
            }

        return {
            "id": payment.get("id"),
            "status": payment.get("status"),
            "status_detail": payment.get("status_detail"),
            "message": "Pago procesado por Mercado Pago"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
