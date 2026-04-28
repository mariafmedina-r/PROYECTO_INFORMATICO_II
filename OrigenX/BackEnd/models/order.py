"""
models/order.py – Modelos Pydantic para pedidos.
"""

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class OrderStatus(str, Enum):
    """Estados del ciclo de vida del pedido (Req. 19.1)."""
    PENDIENTE = "pendiente"
    PAGADO = "pagado"
    EN_PREPARACION = "en_preparacion"
    ENVIADO = "enviado"
    ENTREGADO = "entregado"
    CANCELADO = "cancelado"


class AddressSnapshot(BaseModel):
    """Snapshot de dirección al momento del pedido (Req. 13.4)."""
    street: str
    city: str
    department: str
    postal_code: Optional[str] = None


class OrderItemSnapshot(BaseModel):
    """Snapshot de producto al momento del pedido (Req. 13.4)."""
    product_id: str
    product_name_snapshot: str
    price_snapshot: float
    quantity: int = Field(..., gt=0)


class OrderCreate(BaseModel):
    """Esquema de request para crear pedido (Req. 13.1)."""
    address_id: str
    shipping_company: str


class OrderStatusUpdate(BaseModel):
    """Esquema de request para actualizar estado del pedido (Req. 19.1)."""
    status: OrderStatus


class OrderResponse(BaseModel):
    """Esquema de response para pedido."""
    id: str
    consumer_id: str
    address_snapshot: AddressSnapshot
    shipping_company: str
    shipping_cost: float
    total: float
    status: OrderStatus
    transaction_id: Optional[str] = None
    items: list[OrderItemSnapshot] = []
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class OrderListItem(BaseModel):
    """Esquema de response para ítem del historial de pedidos (Req. 15.1)."""
    id: str
    total: float
    status: OrderStatus
    created_at: datetime

    model_config = {"from_attributes": True}
