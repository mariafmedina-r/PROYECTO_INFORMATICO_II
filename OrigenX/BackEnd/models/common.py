"""
models/common.py – Modelos comunes reutilizables en toda la API.
"""

from typing import Any, Optional

from pydantic import BaseModel


class ErrorDetail(BaseModel):
    """Detalle de un campo inválido (RNF-009.3)."""
    field: str
    message: str


class ErrorResponse(BaseModel):
    """
    Formato uniforme de respuesta de error (RNF-009.3).

    Ejemplo:
    {
      "error": {
        "code": "VALIDATION_ERROR",
        "message": "Datos de entrada inválidos",
        "fields": [
          { "field": "email", "message": "El correo ya está registrado" }
        ]
      }
    }
    """

    class ErrorBody(BaseModel):
        code: str
        message: str
        fields: Optional[list[ErrorDetail]] = None

    error: ErrorBody


class SuccessResponse(BaseModel):
    """Respuesta genérica de éxito."""
    message: str
    data: Optional[Any] = None
