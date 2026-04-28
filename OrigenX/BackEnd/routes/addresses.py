"""
routes/addresses.py – Endpoints de direcciones de envío (rol CONSUMER).

Endpoints:
  GET    /api/addresses       → Listar direcciones (Req. 18.4)
  POST   /api/addresses       → Crear dirección (Req. 18.1, 18.2, 18.3)
  DELETE /api/addresses/:id   → Eliminar dirección

Todos los endpoints requieren rol CONSUMER (Req. 3.2, 3.4).
"""

import logging

from fastapi import APIRouter, Depends, HTTPException, status

from middleware.auth_middleware import require_consumer
from models.address import AddressCreate
from services.address_service import (
    AddressLimitExceededError,
    AddressNotFoundServiceError,
    AddressService,
    AddressServiceError,
)

logger = logging.getLogger(__name__)
router = APIRouter()


def _make_error(code: str, message: str, fields: list | None = None) -> dict:
    """Construye el cuerpo de error uniforme (RNF-009.3)."""
    body: dict = {"code": code, "message": message}
    if fields:
        body["fields"] = fields
    return {"error": body}


# ------------------------------------------------------------------
# GET /api/addresses – Listar direcciones (Req. 18.4)
# ------------------------------------------------------------------

@router.get(
    "",
    status_code=status.HTTP_200_OK,
    summary="Listar direcciones de envío",
    description=(
        "Retorna todas las direcciones de envío registradas por el consumidor autenticado. "
        "Requiere rol CONSUMER. "
        "Requerimientos: 18.4"
    ),
)
async def list_addresses(
    current_user: dict = Depends(require_consumer),
):
    """
    Lista las direcciones de envío del consumidor.

    - Retorna hasta 5 direcciones ordenadas por fecha de creación.
    - Requiere rol CONSUMER.
    """
    user_id = current_user.get("uid")
    service = AddressService()

    try:
        addresses = service.list_addresses(user_id)
    except AddressServiceError as exc:
        logger.error("Error al listar direcciones del usuario '%s': %s", user_id, exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=_make_error(code=exc.code, message=exc.message),
        ) from exc
    except Exception as exc:
        logger.error("Error inesperado al listar direcciones del usuario '%s': %s", user_id, exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=_make_error(code="INTERNAL_ERROR", message="Error interno al obtener las direcciones."),
        ) from exc

    return {"data": addresses}


# ------------------------------------------------------------------
# POST /api/addresses – Crear dirección (Req. 18.1, 18.2, 18.3)
# ------------------------------------------------------------------

@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    summary="Registrar dirección de envío",
    description=(
        "Registra una nueva dirección de envío para el consumidor autenticado. "
        "Campos obligatorios: street, city, department. "
        "Retorna HTTP 400 si se supera el límite de 5 direcciones. "
        "Requiere rol CONSUMER. "
        "Requerimientos: 18.1, 18.2, 18.3"
    ),
)
async def create_address(
    payload: AddressCreate,
    current_user: dict = Depends(require_consumer),
):
    """
    Registra una nueva dirección de envío.

    - Valida campos obligatorios: street, city, department (Req. 18.2).
    - Limita a 5 direcciones por usuario; retorna HTTP 400 si se supera (Req. 18.3).
    - Persiste la dirección asociada al userId del token (Req. 18.1).
    """
    user_id = current_user.get("uid")
    service = AddressService()

    try:
        address = service.create_address(
            user_id=user_id,
            street=payload.street,
            city=payload.city,
            department=payload.department,
            postal_code=payload.postal_code,
        )
    except AddressLimitExceededError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=_make_error(code=exc.code, message=exc.message),
        ) from exc
    except AddressServiceError as exc:
        logger.error("Error al crear dirección para usuario '%s': %s", user_id, exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=_make_error(code=exc.code, message=exc.message),
        ) from exc
    except Exception as exc:
        logger.error("Error inesperado al crear dirección para usuario '%s': %s", user_id, exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=_make_error(code="INTERNAL_ERROR", message="Error interno al guardar la dirección."),
        ) from exc

    return {"message": "Dirección registrada exitosamente.", "data": address}


# ------------------------------------------------------------------
# DELETE /api/addresses/:id – Eliminar dirección
# ------------------------------------------------------------------

@router.delete(
    "/{address_id}",
    status_code=status.HTTP_200_OK,
    summary="Eliminar dirección de envío",
    description=(
        "Elimina una dirección de envío del consumidor autenticado. "
        "Retorna HTTP 404 si la dirección no existe o no pertenece al usuario. "
        "Requiere rol CONSUMER."
    ),
)
async def delete_address(
    address_id: str,
    current_user: dict = Depends(require_consumer),
):
    """
    Elimina una dirección de envío del consumidor.

    - Verifica que la dirección pertenece al usuario autenticado.
    - Retorna HTTP 404 si la dirección no existe o no pertenece al usuario.
    """
    user_id = current_user.get("uid")
    service = AddressService()

    try:
        service.delete_address(user_id=user_id, address_id=address_id)
    except AddressNotFoundServiceError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=_make_error(code=exc.code, message=exc.message),
        ) from exc
    except AddressServiceError as exc:
        logger.error(
            "Error al eliminar dirección '%s' del usuario '%s': %s", address_id, user_id, exc
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=_make_error(code=exc.code, message=exc.message),
        ) from exc
    except Exception as exc:
        logger.error(
            "Error inesperado al eliminar dirección '%s' del usuario '%s': %s",
            address_id, user_id, exc,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=_make_error(code="INTERNAL_ERROR", message="Error interno al eliminar la dirección."),
        ) from exc

    return {"message": "Dirección eliminada exitosamente."}
