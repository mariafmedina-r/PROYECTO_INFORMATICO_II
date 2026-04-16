from pydantic import BaseModel
from typing import List
try:
    from schemas.product import ProductVariantResponse
except ImportError:
    from backend.schemas.product import ProductVariantResponse

class CartItemBase(BaseModel):
    variant_id: int
    quantity: int

class CartItemCreate(CartItemBase):
    pass

class CartItemResponse(CartItemBase):
    id: int
    user_id: int
    variant: ProductVariantResponse

    class Config:
        from_attributes = True

class CartSummary(BaseModel):
    items: List[CartItemResponse]
    subtotal: float
    total_iva: float
    total: float
