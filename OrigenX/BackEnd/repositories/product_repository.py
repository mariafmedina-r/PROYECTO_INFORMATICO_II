"""
repositories/product_repository.py – Acceso a la colección 'products' en Firestore.

Colecciones Firestore:
  /products/{productId}
  /products/{productId}/images/{imageId}
"""

import logging
import uuid
from datetime import datetime, timezone
from typing import Optional

logger = logging.getLogger(__name__)

_COLLECTION = "products"


class ProductRepositoryError(Exception):
    """Error base del repositorio de productos."""

    def __init__(self, message: str, code: str = "REPOSITORY_ERROR"):
        self.message = message
        self.code = code
        super().__init__(message)


class ProductNotFoundError(ProductRepositoryError):
    """El producto no existe en Firestore."""

    def __init__(self, product_id: str):
        super().__init__(
            message=f"Producto con id '{product_id}' no encontrado.",
            code="PRODUCT_NOT_FOUND",
        )


class ProductRepository:
    """Repositorio de productos en Firestore."""

    def __init__(self):
        """Inicializa el cliente de Firestore."""
        try:
            from firebase_admin import firestore as fb_firestore
            self._db = fb_firestore.client()
        except Exception as exc:  # pragma: no cover
            logger.error("Error al inicializar Firestore: %s", exc)
            raise ProductRepositoryError(
                "No se pudo conectar a Firestore.", "FIRESTORE_INIT_ERROR"
            ) from exc

    def create(self, fields: dict) -> dict:
        """
        Crea un nuevo producto en Firestore.

        Args:
            fields: Diccionario con los datos del producto.

        Returns:
            Diccionario con los datos del producto creado, incluyendo el ID generado.
        """
        try:
            now = datetime.now(timezone.utc)
            product_id = str(uuid.uuid4())
            fields["createdAt"] = now
            fields["updatedAt"] = now
            doc_ref = self._db.collection(_COLLECTION).document(product_id)
            doc_ref.set(fields)
            data = doc_ref.get().to_dict()
            data["id"] = product_id
            return data
        except Exception as exc:
            logger.error("Error al crear producto: %s", exc)
            raise ProductRepositoryError(
                f"Error al crear el producto: {exc}", "FIRESTORE_WRITE_ERROR"
            ) from exc

    def get_by_id(self, product_id: str) -> Optional[dict]:
        """
        Obtiene un producto por su ID.

        Returns:
            Diccionario con los datos del producto, o None si no existe.
        """
        try:
            doc_ref = self._db.collection(_COLLECTION).document(product_id)
            doc = doc_ref.get()
            if not doc.exists:
                return None
            data = doc.to_dict()
            data["id"] = doc.id
            return data
        except Exception as exc:
            logger.error("Error al obtener producto '%s': %s", product_id, exc)
            raise ProductRepositoryError(
                f"Error al obtener el producto: {exc}", "FIRESTORE_READ_ERROR"
            ) from exc

    def update(self, product_id: str, fields: dict) -> dict:
        """
        Actualiza los campos indicados de un producto y registra updatedAt.

        Args:
            product_id: ID del documento en Firestore.
            fields: Diccionario con los campos a actualizar.

        Returns:
            Diccionario con los datos actualizados del producto.

        Raises:
            ProductNotFoundError: Si el producto no existe.
        """
        try:
            doc_ref = self._db.collection(_COLLECTION).document(product_id)

            # Verificar que el documento existe antes de actualizar
            doc = doc_ref.get()
            if not doc.exists:
                raise ProductNotFoundError(product_id)

            # Registrar timestamp de actualización (Req. 6.4)
            fields["updatedAt"] = datetime.now(timezone.utc)

            doc_ref.update(fields)

            # Retornar el documento actualizado
            updated_doc = doc_ref.get()
            data = updated_doc.to_dict()
            data["id"] = updated_doc.id
            return data
        except ProductNotFoundError:
            raise
        except Exception as exc:
            logger.error("Error al actualizar producto '%s': %s", product_id, exc)
            raise ProductRepositoryError(
                f"Error al actualizar el producto: {exc}", "FIRESTORE_WRITE_ERROR"
            ) from exc

    # ------------------------------------------------------------------
    # Subcolección de imágenes: /products/{productId}/images/{imageId}
    # ------------------------------------------------------------------

    def get_images(self, product_id: str) -> list[dict]:
        """
        Retorna todas las imágenes de un producto ordenadas por sortOrder.
        """
        try:
            images_ref = (
                self._db.collection(_COLLECTION)
                .document(product_id)
                .collection("images")
                .order_by("sortOrder")
            )
            docs = images_ref.stream()
            result = []
            for doc in docs:
                data = doc.to_dict()
                data["id"] = doc.id
                result.append(data)
            return result
        except Exception as exc:
            logger.error("Error al obtener imágenes del producto '%s': %s", product_id, exc)
            raise ProductRepositoryError(
                f"Error al obtener imágenes: {exc}", "FIRESTORE_READ_ERROR"
            ) from exc

    def count_images(self, product_id: str) -> int:
        """Retorna el número de imágenes asociadas al producto."""
        return len(self.get_images(product_id))

    def add_image(self, product_id: str, image_fields: dict) -> dict:
        """
        Agrega una imagen a la subcolección del producto.

        Args:
            product_id: ID del producto.
            image_fields: Diccionario con url, storagePath, sortOrder.

        Returns:
            Diccionario con los datos de la imagen creada.
        """
        try:
            now = datetime.now(timezone.utc)
            image_id = str(uuid.uuid4())
            image_fields["createdAt"] = now
            img_ref = (
                self._db.collection(_COLLECTION)
                .document(product_id)
                .collection("images")
                .document(image_id)
            )
            img_ref.set(image_fields)
            data = img_ref.get().to_dict()
            data["id"] = image_id
            return data
        except Exception as exc:
            logger.error("Error al agregar imagen al producto '%s': %s", product_id, exc)
            raise ProductRepositoryError(
                f"Error al agregar imagen: {exc}", "FIRESTORE_WRITE_ERROR"
            ) from exc

    def get_image_by_id(self, product_id: str, image_id: str) -> Optional[dict]:
        """Obtiene una imagen por su ID."""
        try:
            img_ref = (
                self._db.collection(_COLLECTION)
                .document(product_id)
                .collection("images")
                .document(image_id)
            )
            doc = img_ref.get()
            if not doc.exists:
                return None
            data = doc.to_dict()
            data["id"] = doc.id
            return data
        except Exception as exc:
            logger.error(
                "Error al obtener imagen '%s' del producto '%s': %s",
                image_id, product_id, exc,
            )
            raise ProductRepositoryError(
                f"Error al obtener imagen: {exc}", "FIRESTORE_READ_ERROR"
            ) from exc

    def delete_image(self, product_id: str, image_id: str) -> None:
        """
        Elimina el documento de imagen de la subcolección.
        No elimina el archivo de Firebase Storage (eso lo hace el servicio).
        """
        try:
            img_ref = (
                self._db.collection(_COLLECTION)
                .document(product_id)
                .collection("images")
                .document(image_id)
            )
            img_ref.delete()
        except Exception as exc:
            logger.error(
                "Error al eliminar imagen '%s' del producto '%s': %s",
                image_id, product_id, exc,
            )
            raise ProductRepositoryError(
                f"Error al eliminar imagen: {exc}", "FIRESTORE_WRITE_ERROR"
            ) from exc

    # ------------------------------------------------------------------
    # Catálogo y búsqueda (Tarea 5.1, 5.4)
    # ------------------------------------------------------------------

    def list_active(self, page: int = 1, page_size: int = 20) -> tuple[list[dict], int]:
        """
        Retorna productos activos ordenados por createdAt descendente con paginación.
        """
        try:
            collection_ref = self._db.collection(_COLLECTION)
            try:
                query = collection_ref.where("status", "==", "active").order_by(
                    "createdAt", direction="DESCENDING"
                )
                all_docs = list(query.stream())
            except Exception:
                # Fallback sin order_by si no existe el índice compuesto
                query = collection_ref.where("status", "==", "active")
                all_docs = list(query.stream())
                all_docs.sort(
                    key=lambda d: d.to_dict().get("createdAt") or "",
                    reverse=True,
                )

            total = len(all_docs)
            offset = (page - 1) * page_size
            paginated_docs = all_docs[offset: offset + page_size]

            items = []
            for doc in paginated_docs:
                data = doc.to_dict()
                data["id"] = doc.id
                items.append(data)

            return items, total
        except Exception as exc:
            logger.error("Error al listar productos activos: %s", exc)
            raise ProductRepositoryError(
                f"Error al listar productos: {exc}", "FIRESTORE_READ_ERROR"
            ) from exc

    def list_by_producer(self, producer_id: str, page: int = 1, page_size: int = 100) -> tuple[list[dict], int]:
        """
        Retorna todos los productos (activos e inactivos) de un productor específico.
        """
        try:
            collection_ref = self._db.collection(_COLLECTION)
            # Primero intentar con order_by (requiere índice compuesto en Firestore)
            try:
                query = collection_ref.where("producerId", "==", producer_id).order_by(
                    "createdAt", direction="DESCENDING"
                )
                all_docs = list(query.stream())
            except Exception as order_exc:
                logger.warning("list_by_producer: order_by falló (%s), usando fallback sin orden", order_exc)
                # Fallback: solo filtrar por producerId sin ordenar
                query = collection_ref.where("producerId", "==", producer_id)
                all_docs = list(query.stream())
                # Ordenar en memoria
                def get_created_at(doc):
                    val = doc.to_dict().get("createdAt")
                    return val if val is not None else ""
                all_docs.sort(key=get_created_at, reverse=True)

            total = len(all_docs)
            offset = (page - 1) * page_size
            paginated_docs = all_docs[offset: offset + page_size]
            items = []
            for doc in paginated_docs:
                data = doc.to_dict()
                data["id"] = doc.id
                items.append(data)
            logger.info("list_by_producer('%s'): encontrados %d productos", producer_id, total)
            return items, total
        except Exception as exc:
            logger.error("Error al listar productos del productor '%s': %s", producer_id, exc)
            raise ProductRepositoryError(
                f"Error al listar productos del productor: {exc}", "FIRESTORE_READ_ERROR"
            ) from exc

    def get_first_image(self, product_id: str) -> Optional[dict]:
        """
        Retorna la primera imagen (sortOrder más bajo) de un producto, o None si no tiene.
        """
        try:
            images_ref = (
                self._db.collection(_COLLECTION)
                .document(product_id)
                .collection("images")
                .order_by("sortOrder")
                .limit(1)
            )
            docs = list(images_ref.stream())
            if not docs:
                return None
            data = docs[0].to_dict()
            data["id"] = docs[0].id
            return data
        except Exception as exc:
            logger.error("Error al obtener primera imagen del producto '%s': %s", product_id, exc)
            raise ProductRepositoryError(
                f"Error al obtener imagen principal: {exc}", "FIRESTORE_READ_ERROR"
            ) from exc

    def get_producer_profile(self, producer_id: str) -> Optional[dict]:
        """
        Obtiene el perfil de productor desde la colección 'producer_profiles'.

        Args:
            producer_id: UID del productor.

        Returns:
            Diccionario con los datos del perfil, o None si no existe.
        """
        try:
            doc_ref = self._db.collection("producer_profiles").document(producer_id)
            doc = doc_ref.get()
            if not doc.exists:
                return None
            data = doc.to_dict()
            data["id"] = doc.id
            return data
        except Exception as exc:
            logger.error("Error al obtener perfil de productor '%s': %s", producer_id, exc)
            raise ProductRepositoryError(
                f"Error al obtener perfil de productor: {exc}", "FIRESTORE_READ_ERROR"
            ) from exc

    def update_producer_name(self, producer_id: str, new_name: str) -> int:
        """
        Actualiza el campo producerName en todos los productos de un productor.

        Args:
            producer_id: UID del productor.
            new_name: Nuevo nombre (farmName) a propagar.

        Returns:
            Número de productos actualizados.
        """
        try:
            from datetime import datetime, timezone
            collection_ref = self._db.collection(_COLLECTION)
            docs = list(collection_ref.where("producerId", "==", producer_id).stream())
            batch = self._db.batch()
            count = 0
            for doc in docs:
                batch.update(doc.reference, {
                    "producerName": new_name,
                    "updatedAt": datetime.now(timezone.utc),
                })
                count += 1
                # Firestore batch limit es 500 operaciones
                if count % 499 == 0:
                    batch.commit()
                    batch = self._db.batch()
            if count % 499 != 0:
                batch.commit()
            logger.info("update_producer_name: actualizados %d productos para producer '%s'", count, producer_id)
            return count
        except Exception as exc:
            logger.error("Error al actualizar producerName para '%s': %s", producer_id, exc)
            raise ProductRepositoryError(
                f"Error al actualizar nombre del productor en productos: {exc}", "FIRESTORE_WRITE_ERROR"
            ) from exc
