"""
routes/shipping.py – Endpoints de opciones de envío.

Endpoints:
  GET /api/shipping/options → Listar empresas de envío (tarea 8.3)

Requerimientos: 14.1, 14.2, 14.3, 14.4
"""

import logging

from fastapi import APIRouter, Depends, HTTPException, status

from middleware.auth_middleware import require_consumer
from services.shipping_service import ShippingService, ShippingServiceUnavailableError

logger = logging.getLogger(__name__)
router = APIRouter()


def _make_error(code: str, message: str) -> dict:
    """Construye el cuerpo de error uniforme (RNF-009.3)."""
    return {"error": {"code": code, "message": message}}


# ------------------------------------------------------------------
# GET /api/shipping/options – Listar empresas de envío (Req. 14.1)
# ------------------------------------------------------------------

@router.get(
    "/options",
    status_code=status.HTTP_200_OK,
    summary="Obtener opciones de envío",
    description=(
        "Retorna la lista de empresas de envío disponibles con tarifas y tiempos estimados. "
        "Retorna HTTP 503 si el módulo de envío no está disponible. "
        "Requiere rol CONSUMER. "
        "Requerimientos: 14.1, 14.2, 14.3, 14.4"
    ),
)
async def get_shipping_options(
    current_user: dict = Depends(require_consumer),
):
    """
    Retorna las empresas de envío disponibles.

    - Lista estática configurable con tarifas y tiempos estimados (Req. 14.1, 14.2).
    - Retorna HTTP 503 si el módulo no está disponible (Req. 14.3).
    """
    service = ShippingService()

    try:
        options = service.get_options()
    except ShippingServiceUnavailableError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=_make_error(code=exc.code, message=exc.message),
        ) from exc
    except Exception as exc:
        logger.error("Error inesperado al obtener opciones de envío: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=_make_error(
                code="INTERNAL_ERROR",
                message="Error interno al obtener las opciones de envío.",
            ),
        ) from exc

    return {"data": options}
