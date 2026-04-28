"""
models/address.py – Modelos Pydantic para direcciones de envío.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class AddressCreate(BaseModel):
    """Esquema de request para crear dirección (Req. 18.1)."""
    street: str = Field(..., min_length=1, description="Calle (obligatorio)")
    city: str = Field(..., min_length=1, description="Ciudad (obligatorio)")
    department: str = Field(..., min_length=1, description="Departamento (obligatorio)")
    postal_code: Optional[str] = None


class AddressResponse(AddressCreate):
    """Esquema de response para dirección."""
    id: str
    user_id: str
    created_at: datetime

    model_config = {"from_attributes": True}
