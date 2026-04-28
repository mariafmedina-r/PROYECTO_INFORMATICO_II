"""
models/product.py – Modelos Pydantic para productos e imágenes.
"""

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class ProductStatus(str, Enum):
    """Estado del producto (Req. 5.4, 8.1, 8.2)."""
    ACTIVE = "active"
    INACTIVE = "inactive"


class ProductBase(BaseModel):
    """Campos base de un producto."""
    name: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=1)
    price: float = Field(..., gt=0, description="Debe ser mayor que cero (Req. 5.3)")
    stock: int = Field(default=0, ge=0, description="Cantidad disponible en stock")


class ProductCreate(ProductBase):
    """Esquema de request para crear producto (Req. 5.1)."""
    pass


class ProductUpdate(ProductBase):
    """Esquema de request para actualizar producto (Req. 6.1)."""
    pass


class ProductStatusUpdate(BaseModel):
    """Esquema de request para cambiar estado del producto (Req. 8.1, 8.2)."""
    status: ProductStatus


class ProductImageResponse(BaseModel):
    """Esquema de response para imagen de producto."""
    id: str
    url: str
    storage_path: str
    sort_order: int
    created_at: datetime

    model_config = {"from_attributes": True}


class ProductResponse(ProductBase):
    """Esquema de response para producto."""
    id: str
    producer_id: str
    producer_name: str
    status: ProductStatus
    created_at: datetime
    updated_at: datetime
    images: list[ProductImageResponse] = []

    model_config = {"from_attributes": True}


class ProductListItem(BaseModel):
    """Esquema de response para ítem del catálogo (Req. 9.3)."""
    id: str
    name: str
    price: float
    producer_name: str
    main_image_url: Optional[str] = None
    status: ProductStatus

    model_config = {"from_attributes": True}


class PaginatedProductsResponse(BaseModel):
    """Respuesta paginada del catálogo (Req. 9.4)."""
    items: list[ProductListItem]
    total: int
    page: int
    page_size: int
    has_next: bool
