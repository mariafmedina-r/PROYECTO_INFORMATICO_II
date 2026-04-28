"""
repositories/producer_repository.py – Acceso a la colección 'producer_profiles' en Firestore.

Colección Firestore: /producer_profiles/{userId}
"""

import logging
from datetime import datetime, timezone
from typing import Optional

logger = logging.getLogger(__name__)

_COLLECTION = "producer_profiles"


class ProducerRepositoryError(Exception):
    """Error base del repositorio de productores."""

    def __init__(self, message: str, code: str = "REPOSITORY_ERROR"):
        self.message = message
        self.code = code
        super().__init__(message)


class ProducerRepository:
    """Repositorio de perfiles de productor en Firestore."""

    def __init__(self):
        """Inicializa el cliente de Firestore."""
        try:
            from firebase_admin import firestore as fb_firestore
            self._db = fb_firestore.client()
        except Exception as exc:  # pragma: no cover
            logger.error("Error al inicializar Firestore: %s", exc)
            raise ProducerRepositoryError(
                "No se pudo conectar a Firestore.", "FIRESTORE_INIT_ERROR"
            ) from exc

    def get_by_user_id(self, user_id: str) -> Optional[dict]:
        """
        Obtiene el perfil de productor por el UID del usuario.

        Returns:
            Diccionario con los datos del perfil, o None si no existe.
        """
        try:
            doc_ref = self._db.collection(_COLLECTION).document(user_id)
            doc = doc_ref.get()
            if not doc.exists:
                return None
            data = doc.to_dict()
            data["user_id"] = doc.id
            return data
        except Exception as exc:
            logger.error("Error al obtener perfil de productor '%s': %s", user_id, exc)
            raise ProducerRepositoryError(
                f"Error al obtener el perfil: {exc}", "FIRESTORE_READ_ERROR"
            ) from exc

    def upsert(self, user_id: str, fields: dict) -> dict:
        """
        Crea o actualiza el perfil de productor para el usuario dado.

        Args:
            user_id: UID del usuario (también es el ID del documento).
            fields: Diccionario con los campos a persistir.

        Returns:
            Diccionario con los datos del perfil guardado.
        """
        try:
            doc_ref = self._db.collection(_COLLECTION).document(user_id)
            fields["updatedAt"] = datetime.now(timezone.utc)
            # merge=True para no sobreescribir campos no enviados
            doc_ref.set(fields, merge=True)

            saved_doc = doc_ref.get()
            data = saved_doc.to_dict()
            data["user_id"] = saved_doc.id
            return data
        except Exception as exc:
            logger.error("Error al guardar perfil de productor '%s': %s", user_id, exc)
            raise ProducerRepositoryError(
                f"Error al guardar el perfil: {exc}", "FIRESTORE_WRITE_ERROR"
            ) from exc

    def list_all(self) -> list[dict]:
        """
        Retorna todos los perfiles de productor activos (isActive=True) con farmName definido.
        """
        try:
            docs = self._db.collection(_COLLECTION).stream()
            result = []
            for doc in docs:
                data = doc.to_dict()
                if data.get("farmName") and data.get("isActive", False):
                    data["user_id"] = doc.id
                    result.append(data)
            return result
        except Exception as exc:
            logger.error("Error al listar perfiles de productor: %s", exc)
            raise ProducerRepositoryError(
                f"Error al listar perfiles: {exc}", "FIRESTORE_READ_ERROR"
            ) from exc

    def set_visibility(self, user_id: str, is_active: bool) -> dict:
        """
        Activa o desactiva la visibilidad del perfil en el catálogo.
        """
        try:
            from datetime import datetime, timezone
            doc_ref = self._db.collection(_COLLECTION).document(user_id)
            doc_ref.set({"isActive": is_active, "updatedAt": datetime.now(timezone.utc)}, merge=True)
            data = doc_ref.get().to_dict()
            data["user_id"] = user_id
            return data
        except Exception as exc:
            logger.error("Error al cambiar visibilidad del perfil '%s': %s", user_id, exc)
            raise ProducerRepositoryError(
                f"Error al cambiar visibilidad: {exc}", "FIRESTORE_WRITE_ERROR"
            ) from exc
