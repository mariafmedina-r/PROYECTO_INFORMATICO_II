"""
routes/cart.py – Endpoints del carrito de compras (rol CONSUMER).

Endpoints:
  GET    /api/cart                  → Obtener carrito (Req. 12.1, 12.6)
  POST   /api/cart/items            → Agregar ítem (Req. 12.1, 8.4)
  PUT    /api/cart/items/:itemId    → Actualizar cantidad (Req. 12.2)
  DELETE /api/cart/items/:itemId    → Eliminar ítem (Req. 12.3)

Todos los endpoints requieren rol CONSUMER (Req. 3.2, 3.4).
"""

import logging
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status

from middleware.auth_middleware import require_consumer
from models.cart import CartItemCreate, CartItemUpdate
from services.cart_service import (
    CartItemNotFoundServiceError,
    CartProductInactiveError,
    CartProductNotFoundError,
    CartService,
    CartServiceError,
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


def _serialize_item(item: dict) -> dict:
    """Serializa un ítem del carrito para la respuesta."""
    return {k: _serialize(v) for k, v in item.items()}


def _serialize_cart(cart: dict) -> dict:
    """Serializa el carrito completo para la respuesta."""
    result = {
        "user_id": cart.get("user_id"),
        "items": [_serialize_item(item) for item in cart.get("items", [])],
        "total": cart.get("total"),
        "updated_at": _serialize(cart.get("updated_at")),
    }
    return result


# ------------------------------------------------------------------
# GET /api/cart – Obtener carrito (Req. 12.1, 12.6)
# ------------------------------------------------------------------

@router.get(
    "",
    status_code=status.HTTP_200_OK,
    summary="Obtener carrito",
    description=(
        "Retorna el carrito del consumidor autenticado con subtotales y total calculados. "
        "Requiere rol CONSUMER. "
        "Requerimientos: 12.1, 12.6"
    ),
)
async def get_cart(
    current_user: dict = Depends(require_consumer),
):
    """
    Obtiene el carrito del consumidor.

    - Retorna todos los ítems con subtotal (precio × cantidad) y total del carrito.
    - Crea el carrito si no existe (Req. 12.6).
    """
    user_id = current_user.get("uid")
    service = CartService()

    try:
        cart = service.get_cart(user_id)
    except CartServiceError as exc:
        logger.error("Error al obtener carrito del usuario '%s': %s", user_id, exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=_make_error(code=exc.code, message=exc.message),
        ) from exc
    except Exception as exc:
        logger.error("Error inesperado al obtener carrito del usuario '%s': %s", user_id, exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=_make_error(code="INTERNAL_ERROR", message="Error interno al obtener el carrito."),
        ) from exc

    return {"data": _serialize_cart(cart)}


# ------------------------------------------------------------------
# POST /api/cart/items – Agregar ítem (Req. 12.1, 8.4)
# ------------------------------------------------------------------

@router.post(
    "/items",
    status_code=status.HTTP_201_CREATED,
    summary="Agregar ítem al carrito",
    description=(
        "Agrega un producto activo al carrito del consumidor. "
        "Retorna HTTP 400 si el producto está inactivo. "
        "Retorna HTTP 404 si el producto no existe. "
        "Requiere rol CONSUMER. "
        "Requerimientos: 12.1, 8.4"
    ),
)
async def add_cart_item(
    payload: CartItemCreate,
    current_user: dict = Depends(require_consumer),
):
    """
    Agrega un producto al carrito.

    - Verifica que el producto existe y está activo (Req. 8.4).
    - Si el producto ya está en el carrito, incrementa la cantidad.
    - Desnormaliza nombre y precio del producto.
    - Retorna el carrito actualizado con subtotales y total.
    """
    user_id = current_user.get("uid")
    service = CartService()

    try:
        cart = service.add_item(
            user_id=user_id,
            product_id=payload.product_id,
            quantity=payload.quantity,
        )
    except CartProductNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=_make_error(code=exc.code, message=exc.message),
        ) from exc
    except CartProductInactiveError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=_make_error(code=exc.code, message=exc.message),
        ) from exc
    except CartServiceError as exc:
        logger.error("Error al agregar ítem al carrito del usuario '%s': %s", user_id, exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=_make_error(code=exc.code, message=exc.message),
        ) from exc
    except Exception as exc:
        logger.error("Error inesperado al agregar ítem al carrito '%s': %s", user_id, exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=_make_error(code="INTERNAL_ERROR", message="Error interno al agregar ítem al carrito."),
        ) from exc

    return {"message": "Ítem agregado al carrito.", "data": _serialize_cart(cart)}


# ------------------------------------------------------------------
# PUT /api/cart/items/:itemId – Actualizar cantidad (Req. 12.2)
# ------------------------------------------------------------------

@router.put(
    "/items/{item_id}",
    status_code=status.HTTP_200_OK,
    summary="Actualizar cantidad de ítem",
    description=(
        "Actualiza la cantidad de un ítem en el carrito del consumidor. "
        "Retorna HTTP 404 si el ítem no existe. "
        "Requiere rol CONSUMER. "
        "Requerimientos: 12.2"
    ),
)
async def update_cart_item(
    item_id: str,
    payload: CartItemUpdate,
    current_user: dict = Depends(require_consumer),
):
    """
    Actualiza la cantidad de un ítem del carrito.

    - Recalcula el subtotal del ítem y el total del carrito (Req. 12.2).
    - Retorna HTTP 404 si el ítem no existe.
    """
    user_id = current_user.get("uid")
    service = CartService()

    try:
        cart = service.update_item(
            user_id=user_id,
            item_id=item_id,
            quantity=payload.quantity,
        )
    except CartItemNotFoundServiceError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=_make_error(code=exc.code, message=exc.message),
        ) from exc
    except CartServiceError as exc:
        logger.error(
            "Error al actualizar ítem '%s' del carrito '%s': %s", item_id, user_id, exc
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=_make_error(code=exc.code, message=exc.message),
        ) from exc
    except Exception as exc:
        logger.error(
            "Error inesperado al actualizar ítem '%s' del carrito '%s': %s",
            item_id, user_id, exc,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=_make_error(code="INTERNAL_ERROR", message="Error interno al actualizar el ítem."),
        ) from exc

    return {"message": "Ítem actualizado.", "data": _serialize_cart(cart)}


# ------------------------------------------------------------------
# DELETE /api/cart/items/:itemId – Eliminar ítem (Req. 12.3)
# ------------------------------------------------------------------

@router.delete(
    "/items/{item_id}",
    status_code=status.HTTP_200_OK,
    summary="Eliminar ítem del carrito",
    description=(
        "Elimina un ítem del carrito del consumidor y recalcula el total. "
        "Retorna HTTP 404 si el ítem no existe. "
        "Requiere rol CONSUMER. "
        "Requerimientos: 12.3"
    ),
)
async def delete_cart_item(
    item_id: str,
    current_user: dict = Depends(require_consumer),
):
    """
    Elimina un ítem del carrito.

    - Recalcula el total del carrito tras la eliminación (Req. 12.3).
    - Retorna HTTP 404 si el ítem no existe.
    """
    user_id = current_user.get("uid")
    service = CartService()

    try:
        cart = service.delete_item(user_id=user_id, item_id=item_id)
    except CartItemNotFoundServiceError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=_make_error(code=exc.code, message=exc.message),
        ) from exc
    except CartServiceError as exc:
        logger.error(
            "Error al eliminar ítem '%s' del carrito '%s': %s", item_id, user_id, exc
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=_make_error(code=exc.code, message=exc.message),
        ) from exc
    except Exception as exc:
        logger.error(
            "Error inesperado al eliminar ítem '%s' del carrito '%s': %s",
            item_id, user_id, exc,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=_make_error(code="INTERNAL_ERROR", message="Error interno al eliminar el ítem."),
        ) from exc

    return {"message": "Ítem eliminado del carrito.", "data": _serialize_cart(cart)}
