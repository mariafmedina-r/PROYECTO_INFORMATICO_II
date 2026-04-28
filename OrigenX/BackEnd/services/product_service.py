"""
services/product_service.py – Lógica de negocio de productos.

Responsabilidades:
  - Crear productos con validación de reglas de negocio (tarea 4.2)
  - Actualizar productos con verificación de propiedad (tarea 4.6)
  - Gestión de imágenes: validación de formato/tamaño, límite de 5 (tarea 4.8)
  - Control de estado active/inactive (tarea 4.10)

Requerimientos: 5.1–5.5, 6.1–6.4, 7.1–7.5, 8.1–8.4
"""

import logging
from typing import Optional

from repositories.product_repository import (
    ProductNotFoundError,
    ProductRepository,
    ProductRepositoryError,
)

logger = logging.getLogger(__name__)

# Límites de imágenes (Req. 7.3, 7.4)
MAX_IMAGES_PER_PRODUCT = 5
MAX_IMAGE_SIZE_BYTES = 5 * 1024 * 1024  # 5 MB
ALLOWED_IMAGE_CONTENT_TYPES = {"image/jpeg", "image/png"}
ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png"}


class ProductServiceError(Exception):
    """Error base del servicio de productos."""

    def __init__(self, message: str, code: str = "PRODUCT_SERVICE_ERROR"):
        self.message = message
        self.code = code
        super().__init__(message)


class ProductNotFoundServiceError(ProductServiceError):
    """El producto no existe."""

    def __init__(self, product_id: str):
        super().__init__(
            message=f"Producto con id '{product_id}' no encontrado.",
            code="PRODUCT_NOT_FOUND",
        )


class ProductForbiddenError(ProductServiceError):
    """El productor no es dueño del producto (Req. 6.3)."""

    def __init__(self):
        super().__init__(
            message="No tienes permiso para modificar este producto.",
            code="FORBIDDEN",
        )


class ProductValidationError(ProductServiceError):
    """Error de validación de campos del producto (Req. 5.2, 6.2)."""

    def __init__(self, message: str, fields: Optional[list] = None):
        super().__init__(message=message, code="VALIDATION_ERROR")
        self.fields = fields or []


class ProductImageLimitError(ProductServiceError):
    """Se superó el límite de imágenes por producto (Req. 7.4)."""

    def __init__(self):
        super().__init__(
            message=f"El producto ya tiene el máximo de {MAX_IMAGES_PER_PRODUCT} imágenes permitidas.",
            code="IMAGE_LIMIT_EXCEEDED",
        )


class ProductImageNotFoundError(ProductServiceError):
    """La imagen no existe en el producto."""

    def __init__(self, image_id: str):
        super().__init__(
            message=f"Imagen con id '{image_id}' no encontrada.",
            code="IMAGE_NOT_FOUND",
        )


class ProductService:
    """Servicio de gestión de productos."""

    def __init__(self, repository: Optional[ProductRepository] = None):
        self._repo = repository or ProductRepository()

    # ------------------------------------------------------------------
    # Tarea 4.2 – Crear producto (Req. 5.1–5.5)
    # ------------------------------------------------------------------

    def create_product(
        self,
        producer_id: str,
        producer_name: str,
        name: str,
        description: str,
        price: float,
        stock: int = 0,
        producer_region: str = "",
    ) -> dict:
        """
        Crea un nuevo producto asociado al productor autenticado.

        Reglas de negocio:
          - name, description y price son obligatorios (Req. 5.2).
          - price debe ser > 0 (Req. 5.3).
          - El estado inicial es 'inactive' (Req. 5.4).
          - Se registran createdAt y updatedAt (Req. 5.5).
          - El producto se asocia al producerId del token (Req. 5.1).

        Args:
            producer_id: UID del productor autenticado.
            producer_name: Nombre del productor (desnormalizado para el catálogo).
            name: Nombre del producto.
            description: Descripción del producto.
            price: Precio del producto (debe ser > 0).

        Returns:
            Diccionario con los datos del producto creado.

        Raises:
            ProductValidationError: Si los campos son inválidos.
        """
        invalid_fields = []
        if not name or not name.strip():
            invalid_fields.append({"field": "name", "message": "El nombre es obligatorio."})
        if not description or not description.strip():
            invalid_fields.append(
                {"field": "description", "message": "La descripción es obligatoria."}
            )
        if price is None or price <= 0:
            invalid_fields.append(
                {"field": "price", "message": "El precio debe ser un valor positivo."}
            )

        if invalid_fields:
            raise ProductValidationError(
                message="Campos obligatorios inválidos o faltantes.",
                fields=invalid_fields,
            )

        fields = {
            "producerId": producer_id,
            "producerName": producer_name.strip() if producer_name else "",
            "producerRegion": producer_region.strip() if producer_region else "",
            "name": name.strip(),
            "description": description.strip(),
            "price": price,
            "stock": max(0, int(stock)),
            "status": "inactive",
        }

        try:
            created = self._repo.create(fields)
        except ProductRepositoryError as exc:
            raise ProductServiceError(exc.message, exc.code) from exc

        return created

    # ------------------------------------------------------------------
    # Tarea 4.6 – Actualizar producto (Req. 6.1–6.4)
    # ------------------------------------------------------------------

    def update_product(
        self,
        product_id: str,
        producer_id: str,
        name: str,
        description: str,
        price: float,
        stock: int = 0,
    ) -> dict:
        """
        Actualiza los campos de un producto existente.

        Reglas de negocio:
          - El producto debe existir (404 si no).
          - Solo el productor dueño puede actualizar (403 si no es dueño, Req. 6.3).
          - name, description y price son obligatorios y price > 0 (Req. 6.2).
          - Se registra updatedAt con el timestamp actual (Req. 6.4).

        Args:
            product_id: ID del producto a actualizar.
            producer_id: UID del productor autenticado.
            name: Nuevo nombre del producto.
            description: Nueva descripción del producto.
            price: Nuevo precio del producto (debe ser > 0).

        Returns:
            Diccionario con los datos actualizados del producto.

        Raises:
            ProductNotFoundServiceError: Si el producto no existe.
            ProductForbiddenError: Si el productor no es el dueño.
            ProductValidationError: Si los campos son inválidos.
        """
        invalid_fields = []
        if not name or not name.strip():
            invalid_fields.append({"field": "name", "message": "El nombre es obligatorio."})
        if not description or not description.strip():
            invalid_fields.append(
                {"field": "description", "message": "La descripción es obligatoria."}
            )
        if price is None or price <= 0:
            invalid_fields.append(
                {"field": "price", "message": "El precio debe ser un valor positivo."}
            )

        if invalid_fields:
            raise ProductValidationError(
                message="Campos obligatorios inválidos o faltantes.",
                fields=invalid_fields,
            )

        try:
            product = self._repo.get_by_id(product_id)
        except ProductRepositoryError as exc:
            raise ProductServiceError(exc.message, exc.code) from exc

        if product is None:
            raise ProductNotFoundServiceError(product_id)

        # Verificar propiedad (Req. 6.3)
        if product.get("producerId") != producer_id:
            raise ProductForbiddenError()

        try:
            updated = self._repo.update(
                product_id,
                {
                    "name": name.strip(),
                    "description": description.strip(),
                    "price": price,
                    "stock": max(0, int(stock)),
                },
            )
        except ProductNotFoundError as exc:
            raise ProductNotFoundServiceError(product_id) from exc
        except ProductRepositoryError as exc:
            raise ProductServiceError(exc.message, exc.code) from exc

        return updated

    # ------------------------------------------------------------------
    # Tarea 4.8 – Gestión de imágenes (Req. 7.1–7.5)
    # ------------------------------------------------------------------

    def add_image(
        self,
        product_id: str,
        producer_id: str,
        file_content: bytes,
        content_type: str,
        filename: str,
    ) -> dict:
        """
        Sube una imagen a Firebase Storage y la asocia al producto.

        Reglas de negocio:
          - Solo el productor dueño puede agregar imágenes.
          - Formato permitido: JPG/PNG (Req. 7.1, 7.2).
          - Tamaño máximo: 5 MB (Req. 7.3).
          - Máximo 5 imágenes por producto (Req. 7.4).

        Args:
            product_id: ID del producto.
            producer_id: UID del productor autenticado.
            file_content: Contenido binario del archivo.
            content_type: MIME type del archivo.
            filename: Nombre original del archivo.

        Returns:
            Diccionario con los datos de la imagen creada.

        Raises:
            ProductNotFoundServiceError: Si el producto no existe.
            ProductForbiddenError: Si el productor no es el dueño.
            ProductValidationError: Si el formato o tamaño son inválidos.
            ProductImageLimitError: Si ya hay 5 imágenes.
        """
        import os

        # Obtener y verificar el producto
        try:
            product = self._repo.get_by_id(product_id)
        except ProductRepositoryError as exc:
            raise ProductServiceError(exc.message, exc.code) from exc

        if product is None:
            raise ProductNotFoundServiceError(product_id)

        if product.get("producerId") != producer_id:
            raise ProductForbiddenError()

        # Validar formato (Req. 7.1, 7.2)
        ext = os.path.splitext(filename)[1].lower()
        if content_type not in ALLOWED_IMAGE_CONTENT_TYPES or ext not in ALLOWED_IMAGE_EXTENSIONS:
            raise ProductValidationError(
                message="Formato de imagen no permitido. Solo se aceptan JPG y PNG.",
                fields=[
                    {
                        "field": "image",
                        "message": "El archivo debe ser JPG o PNG.",
                    }
                ],
            )

        # Validar tamaño (Req. 7.3)
        if len(file_content) > MAX_IMAGE_SIZE_BYTES:
            raise ProductValidationError(
                message="El archivo supera el tamaño máximo permitido de 5 MB.",
                fields=[
                    {
                        "field": "image",
                        "message": "El archivo no puede superar 5 MB.",
                    }
                ],
            )

        # Verificar límite de imágenes (Req. 7.4)
        try:
            current_count = self._repo.count_images(product_id)
        except ProductRepositoryError as exc:
            raise ProductServiceError(exc.message, exc.code) from exc

        if current_count >= MAX_IMAGES_PER_PRODUCT:
            raise ProductImageLimitError()

        # Subir a Firebase Storage
        storage_path, download_url = self._upload_to_storage(
            product_id=product_id,
            file_content=file_content,
            content_type=content_type,
            filename=filename,
        )

        # Guardar referencia en Firestore
        image_fields = {
            "url": download_url,
            "storagePath": storage_path,
            "sortOrder": current_count,
        }

        try:
            image = self._repo.add_image(product_id, image_fields)
        except ProductRepositoryError as exc:
            raise ProductServiceError(exc.message, exc.code) from exc

        # Desnormalizar la primera imagen en el documento del producto
        # para evitar consultas extra en el catálogo
        if current_count == 0:
            try:
                self._repo.update(product_id, {"mainImageUrl": download_url})
            except Exception:
                pass  # No crítico

        return image

    def delete_image(
        self,
        product_id: str,
        image_id: str,
        producer_id: str,
    ) -> None:
        """
        Elimina una imagen del producto.

        Reglas de negocio:
          - Solo el productor dueño puede eliminar imágenes.
          - Al eliminar, se desvincula la imagen sin afectar pedidos históricos (Req. 7.5).

        Args:
            product_id: ID del producto.
            image_id: ID de la imagen a eliminar.
            producer_id: UID del productor autenticado.

        Raises:
            ProductNotFoundServiceError: Si el producto no existe.
            ProductForbiddenError: Si el productor no es el dueño.
            ProductImageNotFoundError: Si la imagen no existe.
        """
        try:
            product = self._repo.get_by_id(product_id)
        except ProductRepositoryError as exc:
            raise ProductServiceError(exc.message, exc.code) from exc

        if product is None:
            raise ProductNotFoundServiceError(product_id)

        if product.get("producerId") != producer_id:
            raise ProductForbiddenError()

        try:
            image = self._repo.get_image_by_id(product_id, image_id)
        except ProductRepositoryError as exc:
            raise ProductServiceError(exc.message, exc.code) from exc

        if image is None:
            raise ProductImageNotFoundError(image_id)

        # Eliminar de Firebase Storage (best-effort; no falla si ya no existe)
        storage_path = image.get("storagePath")
        if storage_path:
            self._delete_from_storage(storage_path)

        # Desvincular de Firestore (Req. 7.5 – no afecta pedidos históricos)
        try:
            self._repo.delete_image(product_id, image_id)
        except ProductRepositoryError as exc:
            raise ProductServiceError(exc.message, exc.code) from exc

    # ------------------------------------------------------------------
    # Tarea 4.10 – Activar/inactivar producto (Req. 8.1–8.4)
    # ------------------------------------------------------------------

    def update_status(
        self,
        product_id: str,
        producer_id: str,
        new_status: str,
    ) -> dict:
        """
        Cambia el estado de un producto entre 'active' e 'inactive'.

        Reglas de negocio:
          - Solo el productor dueño puede cambiar el estado.
          - Activar → visible en catálogo y se puede agregar al carrito (Req. 8.1).
          - Inactivar → oculto del catálogo, no se puede agregar al carrito (Req. 8.2).
          - El historial de pedidos no se ve afectado (Req. 8.3).

        Args:
            product_id: ID del producto.
            producer_id: UID del productor autenticado.
            new_status: 'active' o 'inactive'.

        Returns:
            Diccionario con los datos actualizados del producto.

        Raises:
            ProductNotFoundServiceError: Si el producto no existe.
            ProductForbiddenError: Si el productor no es el dueño.
            ProductValidationError: Si el estado es inválido.
        """
        if new_status not in ("active", "inactive"):
            raise ProductValidationError(
                message="Estado inválido. Los valores permitidos son 'active' e 'inactive'.",
                fields=[
                    {
                        "field": "status",
                        "message": "El estado debe ser 'active' o 'inactive'.",
                    }
                ],
            )

        try:
            product = self._repo.get_by_id(product_id)
        except ProductRepositoryError as exc:
            raise ProductServiceError(exc.message, exc.code) from exc

        if product is None:
            raise ProductNotFoundServiceError(product_id)

        if product.get("producerId") != producer_id:
            raise ProductForbiddenError()

        try:
            updated = self._repo.update(product_id, {"status": new_status})
        except ProductNotFoundError as exc:
            raise ProductNotFoundServiceError(product_id) from exc
        except ProductRepositoryError as exc:
            raise ProductServiceError(exc.message, exc.code) from exc

        return updated

    # ------------------------------------------------------------------
    # Tarea 5.1 / 5.4 – Catálogo con paginación y filtros (Req. 9.1–9.4, 10.1–10.5)
    # ------------------------------------------------------------------

    def get_catalog(
        self,
        page: int = 1,
        page_size: int = 20,
        q: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        region: Optional[str] = None,
        producer_id: Optional[str] = None,
        include_inactive: bool = False,
    ) -> dict:
        try:
            if producer_id:
                all_items, _ = self._repo.list_by_producer(producer_id, page=1, page_size=10000)
                logger.info("get_catalog: list_by_producer devolvió %d items para producer_id=%s", len(all_items), producer_id)
                if not include_inactive:
                    all_items = [p for p in all_items if p.get("status") == "active"]
                logger.info("get_catalog: tras filtro de estado, quedan %d items", len(all_items))
            else:
                all_items, _ = self._repo.list_active(page=1, page_size=10000)
        except ProductRepositoryError as exc:
            raise ProductServiceError(exc.message, exc.code) from exc

        filtered = all_items

        # ── Filtros que NO necesitan perfiles ──────────────────────────
        # Precio primero (más barato, sin Firestore)
        if min_price is not None:
            filtered = [p for p in filtered if (p.get("price") or 0) >= min_price]
        if max_price is not None:
            filtered = [p for p in filtered if (p.get("price") or 0) <= max_price]

        # ── Cargar perfiles SOLO si se necesitan (q o region) ──────────
        producer_profiles: dict = {}
        needs_profiles = bool(q or region)

        if needs_profiles:
            unique_producer_ids = {p.get("producerId") for p in filtered if p.get("producerId")}
            for pid in unique_producer_ids:
                try:
                    producer_profiles[pid] = self._repo.get_producer_profile(pid)
                except ProductRepositoryError:
                    producer_profiles[pid] = None

        # Filtro por texto (nombre, descripción o farmName)
        if q:
            q_lower = q.lower()
            filtered = [
                p for p in filtered
                if q_lower in (p.get("name") or "").lower()
                or q_lower in (p.get("description") or "").lower()
                or q_lower in (
                    (producer_profiles.get(p.get("producerId")) or {}).get("farmName") or
                    p.get("producerName") or ""
                ).lower()
            ]

        # Filtro por región
        if region:
            region_lower = region.lower()
            filtered = [
                p for p in filtered
                if region_lower in (
                    (producer_profiles.get(p.get("producerId")) or {}).get("region") or ""
                ).lower()
            ]

        total = len(filtered)
        offset = (page - 1) * page_size
        page_items = filtered[offset: offset + page_size]

        # ── Construir ítems de la página ───────────────────────────────
        # Si no cargamos perfiles arriba, cargar solo los de esta página
        if not needs_profiles:
            unique_page_ids = {p.get("producerId") for p in page_items if p.get("producerId")}
            for pid in unique_page_ids:
                if pid not in producer_profiles:
                    try:
                        producer_profiles[pid] = self._repo.get_producer_profile(pid)
                    except ProductRepositoryError:
                        producer_profiles[pid] = None

        items = []
        for product in page_items:
            prod_id = product.get("id")
            producer_id_item = product.get("producerId")
            profile_data = producer_profiles.get(producer_id_item)

            farm_name = (
                (profile_data.get("farmName") if profile_data else None)
                or product.get("producerName")
            )
            producer_region = (
                (profile_data.get("region") if profile_data else None)
                or product.get("producerRegion")
            )

            # Usar imagen desnormalizada si existe, si no consultar subcolección
            # (solo para productos de la página actual, no todos)
            main_image_url = product.get("mainImageUrl") or None
            if not main_image_url:
                try:
                    first_image = self._repo.get_first_image(prod_id)
                    if first_image and first_image.get("url"):
                        main_image_url = first_image["url"]
                        # Desnormalizar para la próxima vez (fire-and-forget)
                        try:
                            self._repo.update(prod_id, {"mainImageUrl": main_image_url})
                        except Exception:
                            pass
                except ProductRepositoryError:
                    pass

            items.append({
                "id": prod_id,
                "name": product.get("name"),
                "price": product.get("price"),
                "stock": product.get("stock", 0),
                "status": product.get("status"),
                "producerName": farm_name,
                "producerRegion": producer_region,
                "mainImageUrl": main_image_url,
            })

        has_next = (offset + page_size) < total
        result: dict = {
            "items": items,
            "total": total,
            "page": page,
            "pageSize": page_size,
            "hasNext": has_next,
        }

        if total == 0:
            return {
                "data": result,
                "message": "No se encontraron productos con los criterios seleccionados.",
            }

        return {"data": result}

    # ------------------------------------------------------------------
    # Tarea 5.6 – Detalle de producto (Req. 11.1–11.3)
    # ------------------------------------------------------------------

    def get_product_detail(self, product_id: str) -> dict:
        """
        Retorna el detalle completo de un producto, incluyendo imágenes e info del productor.

        Reglas de negocio:
          - Retorna todos los campos del producto (Req. 11.1).
          - Si el producto está inactivo, incluye mensaje de no disponible (Req. 11.2).
          - Si no existe, lanza ProductNotFoundServiceError (Req. 11.3).

        Args:
            product_id: ID del producto.

        Returns:
            Diccionario con data (producto + imágenes + productor) y opcionalmente message.

        Raises:
            ProductNotFoundServiceError: Si el producto no existe.
        """
        try:
            product = self._repo.get_by_id(product_id)
        except ProductRepositoryError as exc:
            raise ProductServiceError(exc.message, exc.code) from exc

        if product is None:
            raise ProductNotFoundServiceError(product_id)

        # Obtener todas las imágenes del producto
        try:
            images = self._repo.get_images(product_id)
        except ProductRepositoryError:
            images = []

        # Obtener perfil del productor
        producer_id = product.get("producerId")
        producer_profile = None
        if producer_id:
            try:
                producer_profile = self._repo.get_producer_profile(producer_id)
            except ProductRepositoryError:
                producer_profile = None

        # Construir respuesta de imágenes
        images_data = [
            {
                "id": img.get("id"),
                "url": img.get("url"),
                "sortOrder": img.get("sortOrder", 0),
            }
            for img in images
        ]

        # Construir info del productor
        producer_info = None
        if producer_profile:
            producer_info = {
                "farmName": producer_profile.get("farmName"),
                "region": producer_profile.get("region"),
                "description": producer_profile.get("description"),
                "contactInfo": producer_profile.get("contactInfo"),
            }

        data = {
            "id": product.get("id"),
            "name": product.get("name"),
            "description": product.get("description"),
            "price": product.get("price"),
            "stock": product.get("stock", 0),
            "status": product.get("status"),
            "producerId": product.get("producerId"),
            "producerName": (
                producer_profile.get("farmName") if producer_profile else None
            ) or product.get("producerName"),
            "images": images_data,
            "producer": producer_info,
            "createdAt": product.get("createdAt"),
            "updatedAt": product.get("updatedAt"),
        }

        result: dict = {"data": data}

        if product.get("status") == "inactive":
            result["message"] = "Este producto no está disponible actualmente."

        return result

    # ------------------------------------------------------------------
    # Helpers privados – Firebase Storage
    # ------------------------------------------------------------------

    def _upload_to_storage(
        self,
        product_id: str,
        file_content: bytes,
        content_type: str,
        filename: str,
    ) -> tuple[str, str]:
        """
        Sube un archivo a Firebase Storage.

        Returns:
            Tupla (storage_path, download_url).
        """
        import uuid as _uuid

        try:
            from firebase_admin import storage as fb_storage

            bucket = fb_storage.bucket()
            file_id = str(_uuid.uuid4())
            import os
            ext = os.path.splitext(filename)[1].lower()
            storage_path = f"products/{product_id}/images/{file_id}{ext}"

            blob = bucket.blob(storage_path)
            blob.upload_from_string(file_content, content_type=content_type)
            blob.make_public()
            download_url = blob.public_url
            return storage_path, download_url
        except Exception as exc:
            logger.error("Error al subir imagen a Storage: %s", exc)
            raise ProductServiceError(
                f"Error al subir la imagen: {exc}", "STORAGE_UPLOAD_ERROR"
            ) from exc

    def _delete_from_storage(self, storage_path: str) -> None:
        """Elimina un archivo de Firebase Storage (best-effort)."""
        try:
            from firebase_admin import storage as fb_storage

            bucket = fb_storage.bucket()
            blob = bucket.blob(storage_path)
            blob.delete()
        except Exception as exc:
            # No propagamos el error; la imagen ya no es accesible desde el producto
            logger.warning("No se pudo eliminar imagen de Storage '%s': %s", storage_path, exc)
