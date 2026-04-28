"""
routes/products.py – Endpoints de gestión de productos.

Endpoints:
  GET    /api/products                    → Catálogo público con paginación (tarea 5.1)
  GET    /api/products/:id                → Detalle de producto (tarea 5.6)
  POST   /api/products                    → Crear producto (tarea 4.2)
  PUT    /api/products/:id                → Actualizar producto (tarea 4.6)
  PATCH  /api/products/:id/status         → Activar/inactivar producto (tarea 4.10)
  POST   /api/products/:id/images         → Subir imagen (tarea 4.8)
  DELETE /api/products/:id/images/:imgId  → Eliminar imagen (tarea 4.8)
"""

import logging
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status

from middleware.auth_middleware import require_producer
from models.product import ProductCreate, ProductStatusUpdate, ProductUpdate
from services.product_service import (
    ProductForbiddenError,
    ProductImageLimitError,
    ProductImageNotFoundError,
    ProductNotFoundServiceError,
    ProductService,
    ProductServiceError,
    ProductValidationError,
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


def _serialize_doc(doc: dict) -> dict:
    return {k: _serialize(v) for k, v in doc.items()}


# ------------------------------------------------------------------
# GET /api/products – Tarea 5.1 + 5.4 (Req. 9.1–9.4, 10.1–10.5)
# ------------------------------------------------------------------

@router.get(
    "",
    status_code=status.HTTP_200_OK,
    summary="Catálogo de productos",
    description=(
        "Retorna el catálogo de productos activos con paginación y filtros opcionales. "
        "Endpoint público – no requiere autenticación. "
        "Requerimientos: 9.1, 9.3, 9.4, 10.1, 10.2, 10.3, 10.4, 10.5"
    ),
)
async def get_catalog(
    page: int = Query(1, ge=1, description="Número de página (inicia en 1)"),
    page_size: int = Query(20, ge=1, le=100, alias="page_size", description="Productos por página (máx. 100 para panel productor)"),
    q: Optional[str] = Query(None, description="Búsqueda por nombre o descripción"),
    min_price: Optional[float] = Query(None, ge=0, alias="min_price", description="Precio mínimo"),
    max_price: Optional[float] = Query(None, ge=0, alias="max_price", description="Precio máximo"),
    region: Optional[str] = Query(None, description="Región del productor"),
    producer_id: Optional[str] = Query(None, alias="producerId", description="Filtrar por ID de productor"),
    include_inactive: bool = Query(False, alias="includeInactive", description="Incluir productos inactivos (solo para panel productor)"),
):
    """
    Catálogo público de productos activos.

    - Solo productos con status == 'active' (Req. 9.1).
    - Ordenados por createdAt descendente (Req. 9.1).
    - Paginación: máx. 20 por página (Req. 9.4).
    - Cada ítem incluye: id, name, price, producerName, mainImageUrl (Req. 9.3).
    - Filtros opcionales: q, minPrice, maxPrice, region (Req. 10.1–10.4).
    - Sin resultados → mensaje informativo (Req. 10.5).
    """
    service = ProductService()

    try:
        result = service.get_catalog(
            page=page,
            page_size=page_size,
            q=q,
            min_price=min_price,
            max_price=max_price,
            region=region,
            producer_id=producer_id,
            include_inactive=include_inactive,
        )
    except ProductServiceError as exc:
        logger.error("Error al obtener catálogo: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=_make_error(code=exc.code, message=exc.message),
        ) from exc
    except Exception as exc:
        logger.error("Error inesperado al obtener catálogo: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=_make_error(code="INTERNAL_ERROR", message="Error interno al obtener el catálogo."),
        ) from exc

    return result


# ------------------------------------------------------------------
# GET /api/products/:id – Tarea 5.6 (Req. 11.1–11.3)
# ------------------------------------------------------------------

@router.get(
    "/{product_id}",
    status_code=status.HTTP_200_OK,
    summary="Detalle de producto",
    description=(
        "Retorna el detalle completo de un producto, incluyendo imágenes e información del productor. "
        "Endpoint público – no requiere autenticación. "
        "Retorna HTTP 404 si el producto no existe. "
        "Si el producto está inactivo, retorna HTTP 200 con mensaje de no disponible. "
        "Requerimientos: 11.1, 11.2, 11.3"
    ),
)
async def get_product_detail(product_id: str):
    """
    Detalle público de un producto.

    - Retorna todos los campos del producto, imágenes e info del productor (Req. 11.1).
    - Si está inactivo, incluye mensaje de no disponible (Req. 11.2).
    - Si no existe, retorna HTTP 404 (Req. 11.3).
    """
    service = ProductService()

    try:
        result = service.get_product_detail(product_id)
    except ProductNotFoundServiceError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=_make_error(code=exc.code, message=exc.message),
        ) from exc
    except ProductServiceError as exc:
        logger.error("Error al obtener detalle del producto '%s': %s", product_id, exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=_make_error(code=exc.code, message=exc.message),
        ) from exc
    except Exception as exc:
        logger.error("Error inesperado al obtener detalle del producto '%s': %s", product_id, exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=_make_error(code="INTERNAL_ERROR", message="Error interno al obtener el producto."),
        ) from exc

    # Serializar timestamps en el campo data
    if "data" in result and isinstance(result["data"], dict):
        result["data"] = _serialize_doc(result["data"])
        # Serializar imágenes anidadas
        if "images" in result["data"] and isinstance(result["data"]["images"], list):
            result["data"]["images"] = [
                _serialize_doc(img) if isinstance(img, dict) else img
                for img in result["data"]["images"]
            ]

    return result


# ------------------------------------------------------------------
# POST /api/products – Tarea 4.2 (Req. 5.1–5.5)
# ------------------------------------------------------------------

@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    summary="Crear producto",
    description=(
        "Crea un nuevo producto asociado al Productor autenticado. "
        "El estado inicial es 'inactive'. "
        "Retorna HTTP 400 si los campos obligatorios son inválidos. "
        "Retorna HTTP 403 si el usuario no tiene rol PRODUCER. "
        "Requerimientos: 5.1, 5.2, 5.3, 5.4, 5.5"
    ),
)
async def create_product(
    payload: ProductCreate,
    current_user: dict = Depends(require_producer),
):
    """
    Crea un nuevo producto.

    - Asocia el producto al producerId del token (Req. 5.1).
    - Valida campos obligatorios: name, description, price > 0 (Req. 5.2, 5.3).
    - Asigna estado inicial 'inactive' (Req. 5.4).
    - Registra createdAt y updatedAt (Req. 5.5).
    """
    producer_id = current_user.get("uid")

    # Obtener farmName y region del perfil del productor para desnormalizar
    from services.producer_service import ProducerService as _PS
    try:
        _profile = _PS().get_profile(producer_id)
        producer_name = _profile.get("farmName") or current_user.get("name", current_user.get("email", ""))
        producer_region = _profile.get("region") or ""
    except Exception:
        producer_name = current_user.get("name", current_user.get("email", ""))
        producer_region = ""

    service = ProductService()

    try:
        created = service.create_product(
            producer_id=producer_id,
            producer_name=producer_name,
            producer_region=producer_region,
            name=payload.name,
            description=payload.description,
            price=payload.price,
            stock=payload.stock,
        )
    except ProductValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=_make_error(code=exc.code, message=exc.message, fields=exc.fields),
        ) from exc
    except ProductServiceError as exc:
        logger.error("Error al crear producto: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=_make_error(code=exc.code, message=exc.message),
        ) from exc
    except Exception as exc:
        logger.error("Error inesperado al crear producto: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=_make_error(code="INTERNAL_ERROR", message="Error interno al crear el producto."),
        ) from exc

    return {
        "message": "Producto creado exitosamente.",
        "data": _serialize_doc(created),
    }


# ------------------------------------------------------------------
# PUT /api/products/:id – Tarea 4.6 (Req. 6.1–6.4)
# ------------------------------------------------------------------

@router.put(
    "/{product_id}",
    status_code=status.HTTP_200_OK,
    summary="Actualizar producto",
    description=(
        "Actualiza los campos de un producto existente. "
        "Solo el Productor dueño del producto puede actualizarlo. "
        "Retorna HTTP 400 si los campos obligatorios son inválidos. "
        "Retorna HTTP 403 si el Productor no es el dueño del producto. "
        "Retorna HTTP 404 si el producto no existe. "
        "Requerimientos: 6.1, 6.2, 6.3, 6.4"
    ),
)
async def update_product(
    product_id: str,
    payload: ProductUpdate,
    current_user: dict = Depends(require_producer),
):
    """
    Actualiza un producto existente.

    - Verifica que el Productor autenticado sea el dueño del producto (Req. 6.3).
    - Valida campos obligatorios: name, description, price > 0 (Req. 6.2).
    - Registra updatedAt con el timestamp actual (Req. 6.4).
    - Persiste los cambios en Firestore (Req. 6.1).
    """
    producer_id = current_user.get("uid")
    service = ProductService()

    try:
        updated = service.update_product(
            product_id=product_id,
            producer_id=producer_id,
            name=payload.name,
            description=payload.description,
            price=payload.price,
            stock=payload.stock,
        )
    except ProductValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=_make_error(code=exc.code, message=exc.message, fields=exc.fields),
        ) from exc
    except ProductForbiddenError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=_make_error(code=exc.code, message=exc.message),
        ) from exc
    except ProductNotFoundServiceError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=_make_error(code=exc.code, message=exc.message),
        ) from exc
    except Exception as exc:
        logger.error("Error inesperado al actualizar producto '%s': %s", product_id, exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=_make_error(code="INTERNAL_ERROR", message="Error interno al actualizar el producto."),
        ) from exc

    return {
        "message": "Producto actualizado exitosamente.",
        "data": _serialize_doc(updated),
    }


# ------------------------------------------------------------------
# PATCH /api/products/:id/status – Tarea 4.10 (Req. 8.1–8.4)
# ------------------------------------------------------------------

@router.patch(
    "/{product_id}/status",
    status_code=status.HTTP_200_OK,
    summary="Activar o inactivar producto",
    description=(
        "Cambia el estado de un producto entre 'active' e 'inactive'. "
        "Solo el Productor dueño puede cambiar el estado. "
        "Retorna HTTP 403 si el Productor no es el dueño. "
        "Retorna HTTP 404 si el producto no existe. "
        "Requerimientos: 8.1, 8.2, 8.3, 8.4"
    ),
)
async def update_product_status(
    product_id: str,
    payload: ProductStatusUpdate,
    current_user: dict = Depends(require_producer),
):
    """
    Activa o inactiva un producto.

    - Activar → visible en catálogo y se puede agregar al carrito (Req. 8.1).
    - Inactivar → oculto del catálogo, no se puede agregar al carrito (Req. 8.2).
    - El historial de pedidos no se ve afectado (Req. 8.3).
    """
    producer_id = current_user.get("uid")
    service = ProductService()

    try:
        updated = service.update_status(
            product_id=product_id,
            producer_id=producer_id,
            new_status=payload.status.value,
        )
    except ProductValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=_make_error(code=exc.code, message=exc.message, fields=exc.fields),
        ) from exc
    except ProductForbiddenError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=_make_error(code=exc.code, message=exc.message),
        ) from exc
    except ProductNotFoundServiceError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=_make_error(code=exc.code, message=exc.message),
        ) from exc
    except Exception as exc:
        logger.error("Error inesperado al cambiar estado del producto '%s': %s", product_id, exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=_make_error(code="INTERNAL_ERROR", message="Error interno al cambiar el estado."),
        ) from exc

    return {
        "message": f"Estado del producto actualizado a '{payload.status.value}'.",
        "data": _serialize_doc(updated),
    }


# ------------------------------------------------------------------
# POST /api/products/:id/images – Tarea 4.8 (Req. 7.1–7.4)
# ------------------------------------------------------------------

@router.post(
    "/{product_id}/images",
    status_code=status.HTTP_201_CREATED,
    summary="Subir imagen de producto",
    description=(
        "Sube una imagen JPG o PNG (máx. 5 MB) y la asocia al producto. "
        "Máximo 5 imágenes por producto. "
        "Solo el Productor dueño puede subir imágenes. "
        "Requerimientos: 7.1, 7.2, 7.3, 7.4"
    ),
)
async def upload_product_image(
    product_id: str,
    file: UploadFile = File(...),
    current_user: dict = Depends(require_producer),
):
    """
    Sube una imagen al producto.

    - Valida formato JPG/PNG (Req. 7.1, 7.2).
    - Valida tamaño ≤ 5 MB (Req. 7.3).
    - Rechaza si ya hay 5 imágenes (Req. 7.4).
    - Sube a Firebase Storage y guarda URL en Firestore.
    """
    producer_id = current_user.get("uid")
    service = ProductService()

    file_content = await file.read()

    try:
        image = service.add_image(
            product_id=product_id,
            producer_id=producer_id,
            file_content=file_content,
            content_type=file.content_type or "",
            filename=file.filename or "image",
        )
    except ProductValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=_make_error(code=exc.code, message=exc.message, fields=exc.fields),
        ) from exc
    except ProductImageLimitError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=_make_error(code=exc.code, message=exc.message),
        ) from exc
    except ProductForbiddenError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=_make_error(code=exc.code, message=exc.message),
        ) from exc
    except ProductNotFoundServiceError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=_make_error(code=exc.code, message=exc.message),
        ) from exc
    except ProductServiceError as exc:
        logger.error("Error al subir imagen al producto '%s': %s", product_id, exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=_make_error(code=exc.code, message=exc.message),
        ) from exc
    except Exception as exc:
        logger.error("Error inesperado al subir imagen al producto '%s': %s", product_id, exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=_make_error(code="INTERNAL_ERROR", message="Error interno al subir la imagen."),
        ) from exc

    return {
        "message": "Imagen subida exitosamente.",
        "data": _serialize_doc(image),
    }


# ------------------------------------------------------------------
# DELETE /api/products/:id/images/:imgId – Tarea 4.8 (Req. 7.5)
# ------------------------------------------------------------------

@router.delete(
    "/{product_id}/images/{image_id}",
    status_code=status.HTTP_200_OK,
    summary="Eliminar imagen de producto",
    description=(
        "Elimina una imagen del producto. "
        "No afecta el historial de pedidos que referencian ese producto. "
        "Solo el Productor dueño puede eliminar imágenes. "
        "Requerimientos: 7.5"
    ),
)
async def delete_product_image(
    product_id: str,
    image_id: str,
    current_user: dict = Depends(require_producer),
):
    """
    Elimina una imagen del producto.

    - Desvincula la imagen sin afectar pedidos históricos (Req. 7.5).
    - Elimina el archivo de Firebase Storage (best-effort).
    """
    producer_id = current_user.get("uid")
    service = ProductService()

    try:
        service.delete_image(
            product_id=product_id,
            image_id=image_id,
            producer_id=producer_id,
        )
    except ProductForbiddenError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=_make_error(code=exc.code, message=exc.message),
        ) from exc
    except ProductNotFoundServiceError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=_make_error(code=exc.code, message=exc.message),
        ) from exc
    except ProductImageNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=_make_error(code=exc.code, message=exc.message),
        ) from exc
    except ProductServiceError as exc:
        logger.error(
            "Error al eliminar imagen '%s' del producto '%s': %s", image_id, product_id, exc
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=_make_error(code=exc.code, message=exc.message),
        ) from exc
    except Exception as exc:
        logger.error(
            "Error inesperado al eliminar imagen '%s' del producto '%s': %s",
            image_id, product_id, exc,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=_make_error(code="INTERNAL_ERROR", message="Error interno al eliminar la imagen."),
        ) from exc

    return {"message": "Imagen eliminada exitosamente."}
