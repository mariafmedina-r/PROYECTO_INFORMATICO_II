"""
repositories/order_repository.py – Acceso a la colección 'orders' en Firestore.

Colecciones Firestore:
  /orders/{orderId}
  /orders/{orderId}/items/{itemId}

Implementado en tareas 8.1, 8.6 y 9.2 (Req. 13.1, 13.4, 13.5, 16.1–16.4)
"""

import logging
import uuid
from datetime import date, datetime, timezone
from typing import Optional

logger = logging.getLogger(__name__)

_COLLECTION = "orders"


class OrderRepositoryError(Exception):
    """Error base del repositorio de pedidos."""

    def __init__(self, message: str, code: str = "REPOSITORY_ERROR"):
        self.message = message
        self.code = code
        super().__init__(message)


class OrderRepository:
    """Repositorio de pedidos en Firestore."""

    def __init__(self):
        """Inicializa el cliente de Firestore."""
        try:
            from firebase_admin import firestore as fb_firestore
            self._db = fb_firestore.client()
        except Exception as exc:  # pragma: no cover
            logger.error("Error al inicializar Firestore: %s", exc)
            raise OrderRepositoryError(
                "No se pudo conectar a Firestore.", "FIRESTORE_INIT_ERROR"
            ) from exc

    # ------------------------------------------------------------------
    # /orders/{orderId}
    # ------------------------------------------------------------------

    def create_order(self, order_data: dict) -> dict:
        """
        Crea un nuevo documento de pedido en /orders con ID auto-generado.

        Args:
            order_data: Diccionario con los campos del pedido (sin 'id').

        Returns:
            Diccionario con los datos del pedido creado, incluyendo el 'id' generado.

        Raises:
            OrderRepositoryError: Si ocurre un error al escribir en Firestore.
        """
        try:
            order_id = str(uuid.uuid4())
            doc_ref = self._db.collection(_COLLECTION).document(order_id)
            doc_ref.set(order_data)
            result = order_data.copy()
            result["id"] = order_id
            return result
        except Exception as exc:
            logger.error("Error al crear pedido: %s", exc)
            raise OrderRepositoryError(
                f"Error al crear el pedido: {exc}", "FIRESTORE_WRITE_ERROR"
            ) from exc

    def create_order_items(self, order_id: str, items: list[dict]) -> None:
        """
        Crea los documentos de ítems en la subcolección /orders/{orderId}/items.

        Args:
            order_id: ID del pedido padre.
            items: Lista de diccionarios con los campos de cada ítem
                   (productId, productNameSnapshot, priceSnapshot, quantity).

        Raises:
            OrderRepositoryError: Si ocurre un error al escribir en Firestore.
        """
        try:
            items_ref = (
                self._db.collection(_COLLECTION)
                .document(order_id)
                .collection("items")
            )
            for item in items:
                item_id = str(uuid.uuid4())
                items_ref.document(item_id).set(item)
        except Exception as exc:
            logger.error("Error al crear ítems del pedido '%s': %s", order_id, exc)
            raise OrderRepositoryError(
                f"Error al crear ítems del pedido: {exc}", "FIRESTORE_WRITE_ERROR"
            ) from exc

    def get_by_id(self, order_id: str) -> Optional[dict]:
        """
        Obtiene un pedido por su ID, incluyendo sus ítems de la subcolección.

        Args:
            order_id: ID del pedido.

        Returns:
            Diccionario con los datos del pedido e 'items' como lista, o None si no existe.

        Raises:
            OrderRepositoryError: Si ocurre un error al leer de Firestore.
        """
        try:
            doc_ref = self._db.collection(_COLLECTION).document(order_id)
            doc = doc_ref.get()
            if not doc.exists:
                return None
            data = doc.to_dict()
            data["id"] = doc.id

            # Obtener ítems de la subcolección
            items_ref = doc_ref.collection("items")
            items_docs = items_ref.stream()
            items = []
            for item_doc in items_docs:
                item_data = item_doc.to_dict()
                item_data["id"] = item_doc.id
                items.append(item_data)
            data["items"] = items

            return data
        except Exception as exc:
            logger.error("Error al obtener pedido '%s': %s", order_id, exc)
            raise OrderRepositoryError(
                f"Error al obtener el pedido: {exc}", "FIRESTORE_READ_ERROR"
            ) from exc

    def update_order(self, order_id: str, fields: dict) -> dict:
        """
        Actualiza campos de un pedido existente.

        Args:
            order_id: ID del pedido.
            fields: Diccionario con los campos a actualizar (ej. status, updatedAt).

        Returns:
            Diccionario con los datos actualizados del pedido (incluye ítems).

        Raises:
            OrderRepositoryError: Si ocurre un error al escribir en Firestore.
        """
        try:
            doc_ref = self._db.collection(_COLLECTION).document(order_id)
            doc_ref.update(fields)
            # Retornar el documento actualizado con ítems
            return self.get_by_id(order_id)
        except Exception as exc:
            logger.error("Error al actualizar pedido '%s': %s", order_id, exc)
            raise OrderRepositoryError(
                f"Error al actualizar el pedido: {exc}", "FIRESTORE_WRITE_ERROR"
            ) from exc

    def get_orders_by_consumer(self, consumer_id: str) -> list[dict]:
        """
        Obtiene todos los pedidos de un consumidor, ordenados por createdAt descendente.
        """
        try:
            docs = (
                self._db.collection(_COLLECTION)
                .where("consumerId", "==", consumer_id)
                .stream()
            )
            result = []
            for doc in docs:
                data = doc.to_dict()
                data["id"] = doc.id
                result.append(data)
            # Ordenar en memoria para evitar índice compuesto en Firestore
            result.sort(key=lambda x: x.get("createdAt") or "", reverse=True)
            return result
        except Exception as exc:
            logger.error(
                "Error al obtener pedidos del consumidor '%s': %s", consumer_id, exc
            )
            raise OrderRepositoryError(
                f"Error al obtener pedidos del consumidor: {exc}", "FIRESTORE_READ_ERROR"
            ) from exc

    def get_orders_by_producer(
        self,
        producer_id: str,
        from_date: Optional[date] = None,
        to_date: Optional[date] = None,
    ) -> list[dict]:
        """
        Obtiene todos los pedidos que contienen al menos un ítem del productor.

        Dado que Firestore no soporta consultas cross-collection, se obtienen todos
        los pedidos (opcionalmente filtrados por rango de fechas en createdAt), se
        cargan sus ítems y se filtran aquellos donde al menos un ítem pertenece al
        productor. Solo se incluyen los ítems del productor en cada pedido.

        Args:
            producer_id: UID del productor.
            from_date: Fecha de inicio del filtro (inclusive), en UTC.
            to_date: Fecha de fin del filtro (inclusive), en UTC.

        Returns:
            Lista de diccionarios con los datos de cada pedido relevante, donde
            'items' contiene únicamente los ítems del productor.

        Raises:
            OrderRepositoryError: Si ocurre un error al leer de Firestore.
        """
        try:
            from repositories.product_repository import ProductRepository, ProductRepositoryError

            product_repo = ProductRepository()

            # Construir consulta base ordenada por createdAt descendente
            query = self._db.collection(_COLLECTION).order_by(
                "createdAt", direction="DESCENDING"
            )

            # Aplicar filtros de fecha si se proporcionan
            if from_date is not None:
                from_dt = datetime(
                    from_date.year, from_date.month, from_date.day,
                    0, 0, 0, tzinfo=timezone.utc
                )
                query = query.where("createdAt", ">=", from_dt)

            if to_date is not None:
                to_dt = datetime(
                    to_date.year, to_date.month, to_date.day,
                    23, 59, 59, 999999, tzinfo=timezone.utc
                )
                query = query.where("createdAt", "<=", to_dt)

            docs = query.stream()

            # Caché de productos para evitar consultas repetidas
            product_owner_cache: dict[str, Optional[str]] = {}

            result = []
            for doc in docs:
                order_data = doc.to_dict()
                order_data["id"] = doc.id

                # Obtener ítems de la subcolección
                items_ref = (
                    self._db.collection(_COLLECTION)
                    .document(doc.id)
                    .collection("items")
                )
                items_docs = items_ref.stream()

                producer_items = []
                for item_doc in items_docs:
                    item = item_doc.to_dict()
                    item["id"] = item_doc.id
                    product_id = item.get("productId")
                    if not product_id:
                        continue

                    # Verificar propiedad del producto (con caché)
                    if product_id not in product_owner_cache:
                        try:
                            product = product_repo.get_by_id(product_id)
                            product_owner_cache[product_id] = (
                                product.get("producerId") if product else None
                            )
                        except ProductRepositoryError:
                            product_owner_cache[product_id] = None

                    if product_owner_cache[product_id] == producer_id:
                        producer_items.append(item)

                # Solo incluir el pedido si tiene al menos un ítem del productor
                if producer_items:
                    order_data["items"] = producer_items
                    result.append(order_data)

            return result
        except OrderRepositoryError:
            raise
        except Exception as exc:
            logger.error(
                "Error al obtener pedidos del productor '%s': %s", producer_id, exc
            )
            raise OrderRepositoryError(
                f"Error al obtener pedidos del productor: {exc}", "FIRESTORE_READ_ERROR"
            ) from exc
