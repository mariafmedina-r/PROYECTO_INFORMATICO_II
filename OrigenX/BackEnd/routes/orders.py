"""
routes/orders.py – Endpoints de pedidos.

Endpoints:
  POST  /api/orders              → Crear pedido (tarea 8.1)
  GET   /api/orders              → Historial del consumidor (tarea 9.1)
  GET   /api/orders/:id          → Detalle de pedido (tarea 9.1)
  PATCH /api/orders/:id/status   → Actualizar estado (tarea 8.6)

Requerimientos: 13.1, 13.2, 13.3, 13.4, 13.5, 19.1, 19.2, 19.3, 19.4
"""

import logging
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status

from middleware.auth_middleware import (
    get_current_user,
    require_consumer,
    require_producer_or_admin,
)
from models.order import OrderCreate, OrderStatusUpdate
from services.order_service import (
    OrderAddressNotFoundError,
    OrderCartEmptyError,
    OrderForbiddenError,
    OrderInvalidTransitionError,
    OrderNotFoundError,
    OrderService,
    OrderServiceError,
    OrderShippingOptionNotFoundError,
)

logger = logging.getLogger(__name__)
router = APIRouter()


def _make_error(code: str, message: str, fields: list | None = None) -> dict:
    """Construye el cuerpo de error uniforme (RNF-009.3)."""
    body: dict = {"code": code, "message": message}
    if fields:
        body["fields"] = fields
    return {"error": body}


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
# POST /api/orders – Crear pedido (Req. 13.1 – 13.5)
# ------------------------------------------------------------------

@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    summary="Crear pedido",
    description=(
        "Crea un pedido a partir del carrito del consumidor. "
        "Valida carrito no vacío, dirección válida y empresa de envío seleccionada. "
        "Registra snapshot de productos y vacía el carrito automáticamente. "
        "Requiere rol CONSUMER. "
        "Requerimientos: 13.1, 13.2, 13.3, 13.4, 13.5"
    ),
)
async def create_order(
    payload: OrderCreate,
    current_user: dict = Depends(require_consumer),
):
    """
    Crea un pedido a partir del carrito del consumidor.

    - Valida que el carrito no esté vacío (Req. 13.3).
    - Valida que la dirección de envío exista y pertenezca al consumidor.
    - Valida que la empresa de envío esté disponible.
    - Registra snapshot de productos (nombre, precio, cantidad) (Req. 13.4).
    - Crea el pedido con estado 'pendiente' y registra createdAt (Req. 13.1).
    - Vacía el carrito automáticamente (Req. 13.2).
    - Retorna el número de confirmación del pedido (Req. 13.5).
    """
    consumer_id = current_user.get("uid")
    service = OrderService()

    try:
        order = service.create_order(
            consumer_id=consumer_id,
            address_id=payload.address_id,
            shipping_company_id=payload.shipping_company,
        )
    except OrderCartEmptyError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=_make_error(code=exc.code, message=exc.message),
        ) from exc
    except OrderAddressNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=_make_error(code=exc.code, message=exc.message),
        ) from exc
    except OrderShippingOptionNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=_make_error(code=exc.code, message=exc.message),
        ) from exc
    except OrderServiceError as exc:
        logger.error("Error al crear pedido para consumidor '%s': %s", consumer_id, exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=_make_error(code=exc.code, message=exc.message),
        ) from exc
    except Exception as exc:
        logger.error("Error inesperado al crear pedido para consumidor '%s': %s", consumer_id, exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=_make_error(code="INTERNAL_ERROR", message="Error interno al crear el pedido."),
        ) from exc

    return {
        "message": "Pedido creado exitosamente.",
        "data": _serialize_order(order),
    }


# ------------------------------------------------------------------
# GET /api/orders – Historial del consumidor (Req. 15.1)
# ------------------------------------------------------------------

@router.get(
    "",
    status_code=status.HTTP_200_OK,
    summary="Historial de pedidos",
    description=(
        "Retorna todos los pedidos del consumidor autenticado, "
        "ordenados por fecha de creación descendente. "
        "Requiere rol CONSUMER. "
        "Requerimientos: 15.1"
    ),
)
async def get_orders(
    current_user: dict = Depends(require_consumer),
):
    """
    Retorna el historial de pedidos del consumidor.

    - Ordenados por createdAt descendente (Req. 15.1).
    - Incluye número de pedido, fecha, total y estado.
    """
    consumer_id = current_user.get("uid")
    service = OrderService()

    try:
        orders = service.get_consumer_orders(consumer_id)
    except OrderServiceError as exc:
        logger.error("Error al obtener pedidos del consumidor '%s': %s", consumer_id, exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=_make_error(code=exc.code, message=exc.message),
        ) from exc
    except Exception as exc:
        logger.error(
            "Error inesperado al obtener pedidos del consumidor '%s': %s", consumer_id, exc
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=_make_error(code="INTERNAL_ERROR", message="Error interno al obtener los pedidos."),
        ) from exc

    return {"data": [_serialize_order(o) for o in orders]}


# ------------------------------------------------------------------
# GET /api/orders/:id – Detalle de pedido (Req. 15.2)
# ------------------------------------------------------------------

@router.get(
    "/{order_id}",
    status_code=status.HTTP_200_OK,
    summary="Detalle de pedido",
    description=(
        "Retorna el detalle completo de un pedido del consumidor autenticado. "
        "Incluye productos, cantidades, precios, dirección, empresa de envío y estado. "
        "Requiere rol CONSUMER. "
        "Requerimientos: 15.2"
    ),
)
async def get_order_detail(
    order_id: str,
    current_user: dict = Depends(require_consumer),
):
    """
    Retorna el detalle completo de un pedido.

    - Verifica que el pedido pertenece al consumidor autenticado.
    - Incluye ítems con cantidades y precios snapshot (Req. 15.2).
    """
    consumer_id = current_user.get("uid")
    service = OrderService()

    try:
        order = service.get_order_detail(order_id=order_id, consumer_id=consumer_id)
    except OrderNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=_make_error(code=exc.code, message=exc.message),
        ) from exc
    except OrderServiceError as exc:
        logger.error("Error al obtener detalle del pedido '%s': %s", order_id, exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=_make_error(code=exc.code, message=exc.message),
        ) from exc
    except Exception as exc:
        logger.error("Error inesperado al obtener detalle del pedido '%s': %s", order_id, exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=_make_error(code="INTERNAL_ERROR", message="Error interno al obtener el pedido."),
        ) from exc

    return {"data": _serialize_order(order)}


# ------------------------------------------------------------------
# PATCH /api/orders/:id/status – Actualizar estado (Req. 19.1, 19.3, 19.4)
# ------------------------------------------------------------------

@router.patch(
    "/{order_id}/status",
    status_code=status.HTTP_200_OK,
    summary="Actualizar estado del pedido",
    description=(
        "Actualiza el estado de un pedido siguiendo la máquina de estados. "
        "Solo PRODUCER (con productos en el pedido) o ADMIN pueden actualizar. "
        "Rechaza transiciones inválidas con HTTP 422. "
        "Notifica al consumidor del cambio de estado. "
        "Requiere rol PRODUCER o ADMIN. "
        "Requerimientos: 19.1, 19.2, 19.3, 19.4"
    ),
)
async def update_order_status(
    order_id: str,
    payload: OrderStatusUpdate,
    current_user: dict = Depends(require_producer_or_admin),
):
    """
    Actualiza el estado de un pedido.

    - Máquina de estados: pendiente → pagado → en_preparacion → enviado → entregado (Req. 19.1).
    - Rechaza transiciones inválidas con HTTP 422 (Req. 19.4).
    - Verifica que el PRODUCER tenga productos en el pedido (Req. 19.3).
    - Registra timestamp del cambio de estado (Req. 19.1).
    - Notifica al consumidor del nuevo estado (Req. 19.2).
    """
    requester_id = current_user.get("uid")
    requester_role = current_user.get("role")
    service = OrderService()

    try:
        updated_order = service.update_order_status(
            order_id=order_id,
            new_status=payload.status.value,
            requester_id=requester_id,
            requester_role=requester_role,
        )
    except OrderNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=_make_error(code=exc.code, message=exc.message),
        ) from exc
    except OrderForbiddenError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=_make_error(code=exc.code, message=exc.message),
        ) from exc
    except OrderInvalidTransitionError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=_make_error(code=exc.code, message=exc.message),
        ) from exc
    except OrderServiceError as exc:
        logger.error(
            "Error al actualizar estado del pedido '%s': %s", order_id, exc
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=_make_error(code=exc.code, message=exc.message),
        ) from exc
    except Exception as exc:
        logger.error(
            "Error inesperado al actualizar estado del pedido '%s': %s", order_id, exc
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=_make_error(
                code="INTERNAL_ERROR",
                message="Error interno al actualizar el estado del pedido.",
            ),
        ) from exc

    return {
        "message": f"Estado del pedido actualizado a '{payload.status.value}'.",
        "data": _serialize_order(updated_order),
    }
