"""
repositories/cart_repository.py – Acceso a la colección 'carts' en Firestore.

Colecciones Firestore:
  /carts/{userId}
  /carts/{userId}/items/{itemId}

Implementado en tarea 7.1 (Req. 12.1, 12.2, 12.3, 12.6)
"""

import logging
import uuid
from datetime import datetime, timezone
from typing import Optional

logger = logging.getLogger(__name__)

_COLLECTION = "carts"


class CartRepositoryError(Exception):
    """Error base del repositorio del carrito."""

    def __init__(self, message: str, code: str = "REPOSITORY_ERROR"):
        self.message = message
        self.code = code
        super().__init__(message)


class CartItemNotFoundError(CartRepositoryError):
    """El ítem no existe en el carrito."""

    def __init__(self, item_id: str):
        super().__init__(
            message=f"Ítem con id '{item_id}' no encontrado en el carrito.",
            code="CART_ITEM_NOT_FOUND",
        )


class CartRepository:
    """Repositorio del carrito de compras en Firestore."""

    def __init__(self):
        """Inicializa el cliente de Firestore."""
        try:
            from firebase_admin import firestore as fb_firestore
            self._db = fb_firestore.client()
        except Exception as exc:  # pragma: no cover
            logger.error("Error al inicializar Firestore: %s", exc)
            raise CartRepositoryError(
                "No se pudo conectar a Firestore.", "FIRESTORE_INIT_ERROR"
            ) from exc

    # ------------------------------------------------------------------
    # Carrito principal: /carts/{userId}
    # ------------------------------------------------------------------

    def get_or_create_cart(self, user_id: str) -> dict:
        """
        Obtiene el documento del carrito del usuario, creándolo si no existe.

        Args:
            user_id: UID del usuario (consumidor).

        Returns:
            Diccionario con los datos del carrito (userId, updatedAt).
        """
        try:
            doc_ref = self._db.collection(_COLLECTION).document(user_id)
            doc = doc_ref.get()
            if not doc.exists:
                now = datetime.now(timezone.utc)
                cart_data = {"userId": user_id, "updatedAt": now}
                doc_ref.set(cart_data)
                return cart_data
            data = doc.to_dict()
            data["userId"] = user_id
            return data
        except Exception as exc:
            logger.error("Error al obtener/crear carrito del usuario '%s': %s", user_id, exc)
            raise CartRepositoryError(
                f"Error al acceder al carrito: {exc}", "FIRESTORE_READ_ERROR"
            ) from exc

    def update_cart_timestamp(self, user_id: str) -> None:
        """Actualiza el campo updatedAt del carrito."""
        try:
            doc_ref = self._db.collection(_COLLECTION).document(user_id)
            doc_ref.set(
                {"userId": user_id, "updatedAt": datetime.now(timezone.utc)},
                merge=True,
            )
        except Exception as exc:
            logger.error("Error al actualizar timestamp del carrito '%s': %s", user_id, exc)
            raise CartRepositoryError(
                f"Error al actualizar el carrito: {exc}", "FIRESTORE_WRITE_ERROR"
            ) from exc

    # ------------------------------------------------------------------
    # Ítems del carrito: /carts/{userId}/items/{itemId}
    # ------------------------------------------------------------------

    def get_items(self, user_id: str) -> list[dict]:
        """
        Retorna todos los ítems del carrito del usuario.

        Args:
            user_id: UID del usuario.

        Returns:
            Lista de diccionarios con los datos de cada ítem.
        """
        try:
            items_ref = (
                self._db.collection(_COLLECTION)
                .document(user_id)
                .collection("items")
            )
            docs = items_ref.stream()
            result = []
            for doc in docs:
                data = doc.to_dict()
                data["id"] = doc.id
                result.append(data)
            return result
        except Exception as exc:
            logger.error("Error al obtener ítems del carrito '%s': %s", user_id, exc)
            raise CartRepositoryError(
                f"Error al obtener ítems del carrito: {exc}", "FIRESTORE_READ_ERROR"
            ) from exc

    def get_item_by_id(self, user_id: str, item_id: str) -> Optional[dict]:
        """
        Obtiene un ítem del carrito por su ID.

        Returns:
            Diccionario con los datos del ítem, o None si no existe.
        """
        try:
            item_ref = (
                self._db.collection(_COLLECTION)
                .document(user_id)
                .collection("items")
                .document(item_id)
            )
            doc = item_ref.get()
            if not doc.exists:
                return None
            data = doc.to_dict()
            data["id"] = doc.id
            return data
        except Exception as exc:
            logger.error(
                "Error al obtener ítem '%s' del carrito '%s': %s", item_id, user_id, exc
            )
            raise CartRepositoryError(
                f"Error al obtener ítem del carrito: {exc}", "FIRESTORE_READ_ERROR"
            ) from exc

    def get_item_by_product_id(self, user_id: str, product_id: str) -> Optional[dict]:
        """
        Busca un ítem en el carrito por productId.

        Returns:
            Diccionario con los datos del ítem, o None si no existe.
        """
        try:
            items_ref = (
                self._db.collection(_COLLECTION)
                .document(user_id)
                .collection("items")
                .where("productId", "==", product_id)
                .limit(1)
            )
            docs = list(items_ref.stream())
            if not docs:
                return None
            data = docs[0].to_dict()
            data["id"] = docs[0].id
            return data
        except Exception as exc:
            logger.error(
                "Error al buscar ítem por productId '%s' en carrito '%s': %s",
                product_id, user_id, exc,
            )
            raise CartRepositoryError(
                f"Error al buscar ítem en el carrito: {exc}", "FIRESTORE_READ_ERROR"
            ) from exc

    def add_item(self, user_id: str, item_fields: dict) -> dict:
        """
        Agrega un ítem a la subcolección del carrito.

        Args:
            user_id: UID del usuario.
            item_fields: Diccionario con productId, productName, price, quantity.

        Returns:
            Diccionario con los datos del ítem creado (incluye id y addedAt).
        """
        try:
            now = datetime.now(timezone.utc)
            item_id = str(uuid.uuid4())
            item_fields["addedAt"] = now
            item_ref = (
                self._db.collection(_COLLECTION)
                .document(user_id)
                .collection("items")
                .document(item_id)
            )
            item_ref.set(item_fields)
            data = item_ref.get().to_dict()
            data["id"] = item_id
            self.update_cart_timestamp(user_id)
            return data
        except CartRepositoryError:
            raise
        except Exception as exc:
            logger.error("Error al agregar ítem al carrito '%s': %s", user_id, exc)
            raise CartRepositoryError(
                f"Error al agregar ítem al carrito: {exc}", "FIRESTORE_WRITE_ERROR"
            ) from exc

    def update_item(self, user_id: str, item_id: str, fields: dict) -> dict:
        """
        Actualiza los campos de un ítem del carrito.

        Args:
            user_id: UID del usuario.
            item_id: ID del ítem.
            fields: Diccionario con los campos a actualizar (ej. quantity).

        Returns:
            Diccionario con los datos actualizados del ítem.

        Raises:
            CartItemNotFoundError: Si el ítem no existe.
        """
        try:
            item_ref = (
                self._db.collection(_COLLECTION)
                .document(user_id)
                .collection("items")
                .document(item_id)
            )
            doc = item_ref.get()
            if not doc.exists:
                raise CartItemNotFoundError(item_id)
            item_ref.update(fields)
            updated_doc = item_ref.get()
            data = updated_doc.to_dict()
            data["id"] = item_id
            self.update_cart_timestamp(user_id)
            return data
        except CartItemNotFoundError:
            raise
        except Exception as exc:
            logger.error(
                "Error al actualizar ítem '%s' del carrito '%s': %s", item_id, user_id, exc
            )
            raise CartRepositoryError(
                f"Error al actualizar ítem del carrito: {exc}", "FIRESTORE_WRITE_ERROR"
            ) from exc

    def delete_item(self, user_id: str, item_id: str) -> None:
        """
        Elimina un ítem del carrito.

        Args:
            user_id: UID del usuario.
            item_id: ID del ítem a eliminar.

        Raises:
            CartItemNotFoundError: Si el ítem no existe.
        """
        try:
            item_ref = (
                self._db.collection(_COLLECTION)
                .document(user_id)
                .collection("items")
                .document(item_id)
            )
            doc = item_ref.get()
            if not doc.exists:
                raise CartItemNotFoundError(item_id)
            item_ref.delete()
            self.update_cart_timestamp(user_id)
        except CartItemNotFoundError:
            raise
        except Exception as exc:
            logger.error(
                "Error al eliminar ítem '%s' del carrito '%s': %s", item_id, user_id, exc
            )
            raise CartRepositoryError(
                f"Error al eliminar ítem del carrito: {exc}", "FIRESTORE_WRITE_ERROR"
            ) from exc

    def clear_items(self, user_id: str) -> None:
        """
        Elimina todos los ítems del carrito (usado al crear un pedido).

        Args:
            user_id: UID del usuario.
        """
        try:
            items_ref = (
                self._db.collection(_COLLECTION)
                .document(user_id)
                .collection("items")
            )
            docs = list(items_ref.stream())
            for doc in docs:
                doc.reference.delete()
            self.update_cart_timestamp(user_id)
        except CartRepositoryError:
            raise
        except Exception as exc:
            logger.error("Error al vaciar carrito '%s': %s", user_id, exc)
            raise CartRepositoryError(
                f"Error al vaciar el carrito: {exc}", "FIRESTORE_WRITE_ERROR"
            ) from exc
