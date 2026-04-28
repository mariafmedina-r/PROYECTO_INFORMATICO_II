"""
repositories/address_repository.py – Acceso a la colección 'addresses' en Firestore.

Colección Firestore: /addresses/{addressId}

Implementado en tarea 10 (Req. 18.1, 18.2, 18.3, 18.4)
"""

import logging
import uuid
from datetime import datetime, timezone
from typing import Optional

logger = logging.getLogger(__name__)

_COLLECTION = "addresses"
MAX_ADDRESSES_PER_USER = 5


class AddressRepositoryError(Exception):
    """Error base del repositorio de direcciones."""

    def __init__(self, message: str, code: str = "REPOSITORY_ERROR"):
        self.message = message
        self.code = code
        super().__init__(message)


class AddressNotFoundError(AddressRepositoryError):
    """La dirección no existe o no pertenece al usuario."""

    def __init__(self, address_id: str):
        super().__init__(
            message=f"Dirección con id '{address_id}' no encontrada.",
            code="ADDRESS_NOT_FOUND",
        )


class AddressRepository:
    """Repositorio de direcciones de envío en Firestore."""

    def __init__(self):
        """Inicializa el cliente de Firestore."""
        try:
            from firebase_admin import firestore as fb_firestore
            self._db = fb_firestore.client()
        except Exception as exc:  # pragma: no cover
            logger.error("Error al inicializar Firestore: %s", exc)
            raise AddressRepositoryError(
                "No se pudo conectar a Firestore.", "FIRESTORE_INIT_ERROR"
            ) from exc

    def get_by_user(self, user_id: str) -> list[dict]:
        """
        Retorna todas las direcciones del usuario, ordenadas por createdAt ascendente.

        Args:
            user_id: UID del consumidor.

        Returns:
            Lista de diccionarios con los datos de cada dirección.

        Raises:
            AddressRepositoryError: Si ocurre un error al acceder a Firestore.
        """
        try:
            docs = (
                self._db.collection(_COLLECTION)
                .where("userId", "==", user_id)
                .stream()
            )
            result = []
            for doc in docs:
                data = doc.to_dict()
                data["id"] = doc.id
                result.append(data)
            # Ordenar en memoria para evitar requerir índice compuesto en Firestore
            result.sort(key=lambda x: x.get("createdAt") or "")
            return result
        except Exception as exc:
            logger.error("Error al obtener direcciones del usuario '%s': %s", user_id, exc)
            raise AddressRepositoryError(
                f"Error al obtener las direcciones: {exc}", "FIRESTORE_READ_ERROR"
            ) from exc

    def count_by_user(self, user_id: str) -> int:
        """
        Cuenta cuántas direcciones tiene el usuario.

        Args:
            user_id: UID del consumidor.

        Returns:
            Número de direcciones registradas.

        Raises:
            AddressRepositoryError: Si ocurre un error al acceder a Firestore.
        """
        try:
            docs = (
                self._db.collection(_COLLECTION)
                .where("userId", "==", user_id)
                .stream()
            )
            return sum(1 for _ in docs)
        except Exception as exc:
            logger.error("Error al contar direcciones del usuario '%s': %s", user_id, exc)
            raise AddressRepositoryError(
                f"Error al contar las direcciones: {exc}", "FIRESTORE_READ_ERROR"
            ) from exc

    def create(self, user_id: str, street: str, city: str, department: str,
               postal_code: Optional[str] = None) -> dict:
        """
        Crea una nueva dirección de envío para el usuario.

        Args:
            user_id: UID del consumidor.
            street: Calle (obligatorio).
            city: Ciudad (obligatorio).
            department: Departamento (obligatorio).
            postal_code: Código postal (opcional).

        Returns:
            Diccionario con los datos de la dirección creada (incluye id y createdAt).

        Raises:
            AddressRepositoryError: Si ocurre un error al escribir en Firestore.
        """
        try:
            now = datetime.now(timezone.utc)
            address_id = str(uuid.uuid4())
            address_data = {
                "userId": user_id,
                "street": street,
                "city": city,
                "department": department,
                "postalCode": postal_code,
                "createdAt": now,
            }
            self._db.collection(_COLLECTION).document(address_id).set(address_data)
            address_data["id"] = address_id
            return address_data
        except Exception as exc:
            logger.error("Error al crear dirección para usuario '%s': %s", user_id, exc)
            raise AddressRepositoryError(
                f"Error al guardar la dirección: {exc}", "FIRESTORE_WRITE_ERROR"
            ) from exc

    def get_by_id(self, address_id: str, user_id: Optional[str] = None) -> Optional[dict]:
        """
        Obtiene una dirección por su ID, verificando opcionalmente que pertenezca al usuario.

        Args:
            address_id: ID del documento en /addresses/{addressId}.
            user_id: Si se proporciona, verifica que la dirección pertenezca a este usuario.

        Returns:
            Diccionario con los datos de la dirección, o None si no existe o no pertenece al usuario.

        Raises:
            AddressRepositoryError: Si ocurre un error al acceder a Firestore.
        """
        try:
            doc_ref = self._db.collection(_COLLECTION).document(address_id)
            doc = doc_ref.get()
            if not doc.exists:
                return None
            data = doc.to_dict()
            data["id"] = doc.id
            # Verificar que la dirección pertenece al usuario si se especificó
            if user_id is not None and data.get("userId") != user_id:
                return None
            return data
        except Exception as exc:
            logger.error("Error al obtener dirección '%s': %s", address_id, exc)
            raise AddressRepositoryError(
                f"Error al acceder a la dirección: {exc}", "FIRESTORE_READ_ERROR"
            ) from exc

    def delete(self, address_id: str, user_id: str) -> None:
        """
        Elimina una dirección del usuario.

        Args:
            address_id: ID del documento a eliminar.
            user_id: UID del consumidor (para verificar propiedad).

        Raises:
            AddressNotFoundError: Si la dirección no existe o no pertenece al usuario.
            AddressRepositoryError: Si ocurre un error al acceder a Firestore.
        """
        try:
            doc_ref = self._db.collection(_COLLECTION).document(address_id)
            doc = doc_ref.get()
            if not doc.exists:
                raise AddressNotFoundError(address_id)
            data = doc.to_dict()
            if data.get("userId") != user_id:
                raise AddressNotFoundError(address_id)
            doc_ref.delete()
        except AddressNotFoundError:
            raise
        except Exception as exc:
            logger.error("Error al eliminar dirección '%s': %s", address_id, exc)
            raise AddressRepositoryError(
                f"Error al eliminar la dirección: {exc}", "FIRESTORE_WRITE_ERROR"
            ) from exc
