"""
routes/admin.py – Endpoints de administración y mantenimiento.

POST /api/admin/backfill-images  → Rellena mainImageUrl en productos que no lo tienen
"""

import logging
from fastapi import APIRouter, Depends, status
from middleware.auth_middleware import require_producer
from repositories.product_repository import ProductRepository, ProductRepositoryError

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post(
    "/backfill-images",
    status_code=status.HTTP_200_OK,
    summary="Rellena mainImageUrl en productos existentes",
    description="Recorre todos los productos del productor autenticado y guarda la URL de la primera imagen en el campo mainImageUrl del documento principal.",
)
async def backfill_images(current_user: dict = Depends(require_producer)):
    """
    Migración: desnormaliza la primera imagen de cada producto en el campo mainImageUrl.
    Solo procesa los productos del productor autenticado.
    """
    producer_id = current_user.get("uid")
    repo = ProductRepository()
    updated = 0
    skipped = 0

    try:
        products, _ = repo.list_by_producer(producer_id, page=1, page_size=1000)
    except ProductRepositoryError as exc:
        return {"error": exc.message, "updated": 0}

    for product in products:
        prod_id = product.get("id")
        if not prod_id:
            continue

        # Si ya tiene mainImageUrl, saltar
        if product.get("mainImageUrl"):
            skipped += 1
            continue

        try:
            first_image = repo.get_first_image(prod_id)
            if first_image and first_image.get("url"):
                repo.update(prod_id, {"mainImageUrl": first_image["url"]})
                updated += 1
            else:
                skipped += 1
        except Exception as exc:
            logger.warning("backfill_images: error en producto '%s': %s", prod_id, exc)
            skipped += 1

    return {
        "message": f"Migración completada. {updated} productos actualizados, {skipped} omitidos.",
        "updated": updated,
        "skipped": skipped,
    }
