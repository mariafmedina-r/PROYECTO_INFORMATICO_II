"""
models/producer.py – Modelos Pydantic para el perfil de productor.
"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field

VALID_REGIONS = {"Huila", "Nariño", "Antioquia"}


class ProducerProfileCreate(BaseModel):
    """Esquema de request para crear/actualizar perfil de productor."""

    farm_name: str = Field(..., min_length=1, description="Nombre de finca (obligatorio)")
    region: str = Field(..., description="Región: Huila, Nariño o Antioquia")
    description: str = Field(..., min_length=1, description="Descripción enriquecida (HTML)")
    show_register_email: bool = Field(default=True, description="Mostrar correo de registro en perfil público")
    alt_email: Optional[str] = Field(default=None, description="Correo alternativo de contacto (opcional)")
    show_alt_email: bool = Field(default=False, description="Mostrar correo alternativo en perfil público")
    whatsapp: str = Field(..., min_length=7, description="Número de WhatsApp")
    images: Optional[List[str]] = Field(
        default=None,
        description="URLs de imágenes almacenadas en Firebase Storage (máx. 6)",
    )


class ProducerVisibilityUpdate(BaseModel):
    """Esquema para activar/desactivar visibilidad del perfil en el catálogo."""
    is_active: bool = Field(..., description="True = visible en el catálogo de productores")


class ProducerProfileResponse(ProducerProfileCreate):
    """Esquema de response para perfil de productor."""

    user_id: str
    updated_at: datetime

    model_config = {"from_attributes": True}
