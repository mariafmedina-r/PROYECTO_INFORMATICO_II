"""
models/cart.py – Modelos Pydantic para el carrito de compras.
"""

from datetime import datetime

from pydantic import BaseModel, Field


class CartItemCreate(BaseModel):
    """Esquema de request para agregar ítem al carrito (Req. 12.1)."""
    product_id: str
    quantity: int = Field(..., gt=0)


class CartItemUpdate(BaseModel):
    """Esquema de request para actualizar cantidad de ítem (Req. 12.2)."""
    quantity: int = Field(..., gt=0)


class CartItemResponse(BaseModel):
    """Esquema de response para ítem del carrito."""
    id: str
    product_id: str
    product_name: str
    price: float
    quantity: int
    subtotal: float  # precio × cantidad (Req. 12.2)
    added_at: datetime

    model_config = {"from_attributes": True}


class CartResponse(BaseModel):
    """Esquema de response para el carrito completo (Req. 12.1)."""
    user_id: str
    items: list[CartItemResponse] = []
    total: float  # suma de subtotales (Req. 12.2)
    updated_at: datetime

    model_config = {"from_attributes": True}
