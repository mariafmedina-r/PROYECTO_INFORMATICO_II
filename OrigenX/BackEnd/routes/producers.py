"""
routes/producers.py – Endpoints de perfil de productor.

Endpoints:
  GET /api/producers/:id  → Obtener perfil público (tarea 4.1)
  PUT /api/producers/:id  → Crear/actualizar perfil (tarea 4.1)

Requerimientos: 4.1, 4.2, 4.3, 4.4
"""

import logging
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status

from middleware.auth_middleware import get_current_user, require_producer
from models.producer import ProducerProfileCreate, ProducerProfileResponse, ProducerVisibilityUpdate
from services.producer_service import (
    ProducerForbiddenError,
    ProducerNotFoundError,
    ProducerService,
    ProducerValidationError,
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


def _serialize_profile(profile: dict) -> dict:
    return {k: _serialize(v) for k, v in profile.items()}


# ------------------------------------------------------------------
# GET /api/producers – Listar todos los productores (público)
# ------------------------------------------------------------------

@router.get(
    "",
    status_code=status.HTTP_200_OK,
    summary="Listar productores",
    description="Retorna todos los perfiles de productor con farmName definido.",
)
async def list_producers():
    """Lista pública de productores registrados."""
    service = ProducerService()
    try:
        producers = service.list_all()
    except Exception as exc:
        logger.error("Error al listar productores: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=_make_error(code="INTERNAL_ERROR", message="Error interno al listar productores."),
        ) from exc
    return {"data": [_serialize_profile(p) for p in producers]}


# ------------------------------------------------------------------
# GET /api/producers/:id – Obtener perfil público (Req. 4.1, 4.4)
# ------------------------------------------------------------------

@router.get(
    "/{producer_id}",
    status_code=status.HTTP_200_OK,
    summary="Obtener perfil de productor",
    description=(
        "Retorna el perfil público de un productor. "
        "Accesible por cualquier usuario autenticado o visitante. "
        "Requerimientos: 4.1, 4.4"
    ),
)
async def get_producer_profile(producer_id: str):
    """
    Obtiene el perfil público de un productor por su UID.

    - Retorna HTTP 404 si el perfil no existe.
    """
    service = ProducerService()

    try:
        profile = service.get_profile(producer_id)
    except ProducerNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=_make_error(code=exc.code, message=exc.message),
        ) from exc
    except Exception as exc:
        logger.error("Error inesperado al obtener perfil '%s': %s", producer_id, exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=_make_error(
                code="INTERNAL_ERROR",
                message="Error interno al obtener el perfil.",
            ),
        ) from exc

    return {"data": _serialize_profile(profile)}


# ------------------------------------------------------------------
# PUT /api/producers/:id – Crear/actualizar perfil (Req. 4.1, 4.2, 4.3)
# ------------------------------------------------------------------

@router.put(
    "/{producer_id}",
    status_code=status.HTTP_200_OK,
    summary="Actualizar perfil de productor",
    description=(
        "Crea o actualiza el perfil de un productor. "
        "Solo el Productor dueño puede actualizar su propio perfil. "
        "Retorna HTTP 400 si farmName está vacío. "
        "Retorna HTTP 403 si el usuario autenticado no es el dueño del perfil. "
        "Requerimientos: 4.1, 4.2, 4.3, 4.4"
    ),
)
async def update_producer_profile(
    producer_id: str,
    payload: ProducerProfileCreate,
    current_user: dict = Depends(require_producer),
):
    """
    Crea o actualiza el perfil de un productor.

    - Solo el Productor autenticado puede actualizar su propio perfil (Req. 4.2).
    - farmName es obligatorio (Req. 4.3).
    - Los cambios se reflejan en el catálogo en ≤ 5 s (Req. 4.2).
    """
    requesting_user_id = current_user.get("uid")
    service = ProducerService()

    try:
        saved = service.update_profile(
            producer_id=producer_id,
            requesting_user_id=requesting_user_id,
            farm_name=payload.farm_name,
            region=payload.region,
            description=payload.description,
            whatsapp=payload.whatsapp,
            show_register_email=payload.show_register_email,
            alt_email=payload.alt_email,
            show_alt_email=payload.show_alt_email,
            images=payload.images,
        )
    except ProducerValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=_make_error(
                code=exc.code,
                message=exc.message,
                fields=exc.fields,
            ),
        ) from exc
    except ProducerForbiddenError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=_make_error(code=exc.code, message=exc.message),
        ) from exc
    except Exception as exc:
        logger.error("Error inesperado al actualizar perfil '%s': %s", producer_id, exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=_make_error(
                code="INTERNAL_ERROR",
                message="Error interno al actualizar el perfil.",
            ),
        ) from exc

    return {
        "message": "Perfil actualizado exitosamente.",
        "data": _serialize_profile(saved),
    }


# ------------------------------------------------------------------
# PATCH /api/producers/:id/visibility – Activar/desactivar perfil
# ------------------------------------------------------------------

@router.patch(
    "/{producer_id}/visibility",
    status_code=status.HTTP_200_OK,
    summary="Activar o desactivar visibilidad del perfil",
    description=(
        "Permite al productor activar su perfil en el catálogo público o desactivarlo. "
        "Solo se puede activar si el perfil tiene todos los datos obligatorios completos."
    ),
)
async def set_producer_visibility(
    producer_id: str,
    payload: ProducerVisibilityUpdate,
    current_user: dict = Depends(require_producer),
):
    requesting_user_id = current_user.get("uid")
    service = ProducerService()

    try:
        saved = service.set_visibility(
            producer_id=producer_id,
            requesting_user_id=requesting_user_id,
            is_active=payload.is_active,
        )
    except ProducerValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=_make_error(code=exc.code, message=exc.message, fields=exc.fields),
        ) from exc
    except ProducerForbiddenError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=_make_error(code=exc.code, message=exc.message),
        ) from exc
    except ProducerNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=_make_error(code=exc.code, message=exc.message),
        ) from exc
    except Exception as exc:
        logger.error("Error al cambiar visibilidad del perfil '%s': %s", producer_id, exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=_make_error(code="INTERNAL_ERROR", message="Error interno."),
        ) from exc

    action = "activado" if payload.is_active else "desactivado"
    return {"message": f"Perfil {action} exitosamente.", "data": _serialize_profile(saved)}
