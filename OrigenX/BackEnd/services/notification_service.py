"""
services/notification_service.py – Servicio de notificaciones.

Responsabilidades:
  - Escribir notificaciones en Firestore (colección 'notifications')
  - Campos: userId, orderId, message, read=False, createdAt
  - El frontend las consume en tiempo real via Firestore onSnapshot

Requerimientos: 19.2
"""

import logging
from typing import Optional

from repositories.notification_repository import (
    NotificationRepository,
    NotificationRepositoryError,
)

logger = logging.getLogger(__name__)

# Plantillas de mensajes de notificación por estado del pedido
_STATUS_MESSAGES: dict[str, str] = {
    "pagado": "Tu pedido ha sido pagado exitosamente y está siendo procesado.",
    "en_preparacion": "Tu pedido está siendo preparado por el productor.",
    "enviado": "Tu pedido ha sido enviado y está en camino.",
    "entregado": "Tu pedido ha sido entregado. ¡Gracias por tu compra!",
    "cancelado": "Tu pedido ha sido cancelado.",
}


class NotificationServiceError(Exception):
    """Error base del servicio de notificaciones."""

    def __init__(self, message: str, code: str = "NOTIFICATION_SERVICE_ERROR"):
        self.message = message
        self.code = code
        super().__init__(message)


class NotificationService:
    """Servicio de notificaciones en tiempo real via Firestore."""

    def __init__(self, notification_repository: Optional[NotificationRepository] = None):
        self._repo = notification_repository or NotificationRepository()

    def notify_order_status_change(
        self,
        user_id: str,
        order_id: str,
        new_status: str,
    ) -> dict:
        """
        Crea una notificación de cambio de estado de pedido para el consumidor.

        El frontend consume estas notificaciones en tiempo real via Firestore onSnapshot
        (Req. 19.2).

        Args:
            user_id: UID del consumidor propietario del pedido.
            order_id: ID del pedido cuyo estado cambió.
            new_status: Nuevo estado del pedido.

        Returns:
            Diccionario con los datos de la notificación creada.

        Raises:
            NotificationServiceError: Si ocurre un error al crear la notificación.
        """
        message = _STATUS_MESSAGES.get(
            new_status,
            f"El estado de tu pedido ha cambiado a: {new_status}.",
        )

        try:
            notification = self._repo.create(
                user_id=user_id,
                order_id=order_id,
                message=message,
            )
            logger.info(
                "Notificación creada para usuario '%s', pedido '%s', estado '%s'.",
                user_id, order_id, new_status,
            )
            return notification
        except NotificationRepositoryError as exc:
            logger.error(
                "Error al crear notificación para usuario '%s', pedido '%s': %s",
                user_id, order_id, exc,
            )
            raise NotificationServiceError(exc.message, exc.code) from exc
