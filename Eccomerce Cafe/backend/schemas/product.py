from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class ProductVariantBase(BaseModel):
    name: str
    price: float
    stock: int
    iva_percentage: float = 19.0

class ProductVariantCreate(ProductVariantBase):
    pass

class ProductVariantResponse(ProductVariantBase):
    id: int
    product_id: int

    class Config:
        from_attributes = True

class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    producer_id: int

class ProductCreate(ProductBase):
    variants: List[ProductVariantCreate]

class ProductResponse(ProductBase):
    id: int
    variants: List[ProductVariantResponse]
    deleted_at: Optional[datetime] = None

    class Config:
        from_attributes = True
