from pydantic import BaseModel
from typing import List
from datetime import datetime

class OrderItemResponse(BaseModel):
    id: int
    variant_id: int
    quantity: int
    price_at_purchase: float
    iva_at_purchase: float

    class Config:
        from_attributes = True

class OrderResponse(BaseModel):
    id: int
    user_id: int
    status: str
    total_amount: float
    created_at: datetime
    items: List[OrderItemResponse]

    class Config:
        from_attributes = True
