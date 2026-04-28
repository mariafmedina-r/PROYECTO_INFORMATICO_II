"""
routes/sales.py – Endpoints del panel de ventas del productor.

Endpoints:
  GET /api/sales → Panel de ventas (tarea 9.2)

Requerimientos: 16.1, 16.2, 16.3, 16.4
"""

import logging
from datetime import date, datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status

from middleware.auth_middleware import require_producer
from services.order_service import OrderService, OrderServiceError

logger = logging.getLogger(__name__)
router = APIRouter()


def _make_error(code: str, message: str) -> dict:
    """Construye el cuerpo de error uniforme (RNF-009.3)."""
    return {"error": {"code": code, "message": message}}


def _serialize(value):
    """Serializa valores no-JSON (timestamps) para la respuesta."""
    if isinstance(value, datetime):
        return value.isoformat()
    return value


def _serialize_order(order: dict) -> dict:
    """Serializa un pedido para la respuesta HTTP."""
    result = {}
    for key, value in order.items():
        if isinstance(value, datetime):
            result[key] = value.isoformat()
        elif isinstance(value, list):
            result[key] = [
                {k: _serialize(v) for k, v in item.items()} if isinstance(item, dict) else item
                for item in value
            ]
        elif isinstance(value, dict):
            result[key] = {k: _serialize(v) for k, v in value.items()}
        else:
            result[key] = value
    return result


# ------------------------------------------------------------------
# GET /api/sales – Panel de ventas del productor (Req. 16.1–16.4)
# ------------------------------------------------------------------

@router.get(
    "",
    status_code=status.HTTP_200_OK,
    summary="Panel de ventas del productor",
    description=(
        "Retorna los pedidos que contienen productos del productor autenticado, "
        "con fecha, productos vendidos, cantidades, precios y estado. "
        "Incluye el total acumulado del mes en curso y del mes anterior. "
        "Soporta filtro por rango de fechas (from_date, to_date en formato YYYY-MM-DD). "
        "Solo expone datos de los propios productos del productor. "
        "Requiere rol PRODUCER. "
        "Requerimientos: 16.1, 16.2, 16.3, 16.4"
    ),
)
async def get_sales(
    from_date: Optional[date] = Query(
        default=None,
        description="Fecha de inicio del filtro (YYYY-MM-DD, inclusive).",
        alias="from_date",
    ),
    to_date: Optional[date] = Query(
        default=None,
        description="Fecha de fin del filtro (YYYY-MM-DD, inclusive).",
        alias="to_date",
    ),
    current_user: dict = Depends(require_producer),
):
    """
    Retorna el panel de ventas del productor autenticado.

    - Lista de pedidos que contienen productos del productor (Req. 16.1).
    - Cada pedido incluye: id, createdAt, status, shippingCompany e items del productor.
    - Total acumulado del mes en curso y del mes anterior (Req. 16.2).
    - Filtro opcional por rango de fechas en la lista de pedidos (Req. 16.3).
    - Solo expone datos de los propios productos del productor (Req. 16.4).
    """
    producer_id = current_user.get("uid")
    service = OrderService()

    try:
        result = service.get_producer_sales(
            producer_id=producer_id,
            from_date=from_date,
            to_date=to_date,
        )
    except OrderServiceError as exc:
        logger.error("Error al obtener ventas del productor '%s': %s", producer_id, exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=_make_error(code=exc.code, message=exc.message),
        ) from exc
    except Exception as exc:
        logger.error(
            "Error inesperado al obtener ventas del productor '%s': %s", producer_id, exc
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=_make_error(
                code="INTERNAL_ERROR",
                message="Error interno al obtener el panel de ventas.",
            ),
        ) from exc

    return {
        "data": {
            "orders": [_serialize_order(o) for o in result["orders"]],
            "current_month_total": result["current_month_total"],
            "previous_month_total": result["previous_month_total"],
        }
    }
