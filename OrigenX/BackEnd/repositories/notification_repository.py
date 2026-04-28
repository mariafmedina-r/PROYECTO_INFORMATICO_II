"""
repositories/notification_repository.py – Acceso a la colección 'notifications' en Firestore.

Colección Firestore: /notifications/{notificationId}

Implementado en tarea 8.9 (Req. 19.2)
"""

import logging
import uuid
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

_COLLECTION = "notifications"


class NotificationRepositoryError(Exception):
    """Error base del repositorio de notificaciones."""

    def __init__(self, message: str, code: str = "REPOSITORY_ERROR"):
        self.message = message
        self.code = code
        super().__init__(message)


class NotificationRepository:
    """Repositorio de notificaciones en Firestore."""

    def __init__(self):
        """Inicializa el cliente de Firestore."""
        try:
            from firebase_admin import firestore as fb_firestore
            self._db = fb_firestore.client()
        except Exception as exc:  # pragma: no cover
            logger.error("Error al inicializar Firestore: %s", exc)
            raise NotificationRepositoryError(
                "No se pudo conectar a Firestore.", "FIRESTORE_INIT_ERROR"
            ) from exc

    def create(self, user_id: str, order_id: str, message: str) -> dict:
        """
        Crea un documento de notificación en /notifications.

        Args:
            user_id: UID del usuario destinatario.
            order_id: ID del pedido relacionado.
            message: Texto descriptivo del cambio de estado.

        Returns:
            Diccionario con los datos de la notificación creada.

        Raises:
            NotificationRepositoryError: Si ocurre un error al escribir en Firestore.
        """
        try:
            notification_id = str(uuid.uuid4())
            now = datetime.now(timezone.utc)
            notification_data = {
                "userId": user_id,
                "orderId": order_id,
                "message": message,
                "read": False,
                "createdAt": now,
            }
            doc_ref = self._db.collection(_COLLECTION).document(notification_id)
            doc_ref.set(notification_data)
            result = notification_data.copy()
            result["id"] = notification_id
            return result
        except Exception as exc:
            logger.error(
                "Error al crear notificación para usuario '%s', pedido '%s': %s",
                user_id, order_id, exc,
            )
            raise NotificationRepositoryError(
                f"Error al crear la notificación: {exc}", "FIRESTORE_WRITE_ERROR"
            ) from exc
