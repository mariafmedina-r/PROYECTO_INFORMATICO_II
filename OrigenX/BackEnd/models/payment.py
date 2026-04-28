"""
models/payment.py – Modelos Pydantic para el simulador de pagos.
"""

from pydantic import BaseModel, Field, field_validator


class PaymentSimulateRequest(BaseModel):
    """
    Esquema de request para simular un pago (Req. 17.1).
    Los datos de tarjeta son ficticios y NO se almacenan en Firestore.
    """
    order_id: str
    card_number: str = Field(..., min_length=16, max_length=16, description="16 dígitos")
    card_holder: str = Field(..., min_length=1)
    expiry_date: str = Field(..., pattern=r"^\d{2}/\d{2}$", description="MM/YY")
    cvv: str = Field(..., min_length=3, max_length=4)
    amount: float = Field(..., gt=0)

    @field_validator("card_number")
    @classmethod
    def validate_card_number(cls, v: str) -> str:
        if not v.isdigit():
            raise ValueError("El número de tarjeta debe contener solo dígitos")
        return v


class PaymentSimulateResponse(BaseModel):
    """Esquema de response para simulación de pago."""
    success: bool
    transaction_id: str | None = None  # SIM-{uuid} si exitoso
    message: str
    order_status: str
