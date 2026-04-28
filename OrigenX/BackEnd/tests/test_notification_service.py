"""
test_notification_service.py – Tests unitarios para el servicio de notificaciones.

Verifica que al cambiar el estado de un pedido se escriba correctamente
un documento en la colección 'notifications' de Firestore con los campos
userId, orderId, message y read=False.

Requerimientos: 19.2
"""

import pytest
from unittest.mock import MagicMock, patch

# Firebase mocks se cargan en conftest.py antes de estos imports
from services.notification_service import NotificationService, NotificationServiceError
from repositories.notification_repository import (
    NotificationRepository,
    NotificationRepositoryError,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def mock_repo():
    """Repositorio de notificaciones mockeado."""
    return MagicMock(spec=NotificationRepository)


@pytest.fixture
def service(mock_repo):
    """NotificationService con repositorio mockeado."""
    return NotificationService(notification_repository=mock_repo)


# ---------------------------------------------------------------------------
# Tests de NotificationService.notify_order_status_change
# ---------------------------------------------------------------------------

class TestNotifyOrderStatusChange:
    """Tests del método notify_order_status_change (Req. 19.2)."""

    def test_creates_notification_with_correct_fields(self, service, mock_repo):
        """Debe crear una notificación con userId, orderId, message y read=False."""
        mock_repo.create.return_value = {
            "id": "notif-123",
            "userId": "user-abc",
            "orderId": "order-xyz",
            "message": "Tu pedido ha sido pagado exitosamente y está siendo procesado.",
            "read": False,
        }

        result = service.notify_order_status_change(
            user_id="user-abc",
            order_id="order-xyz",
            new_status="pagado",
        )

        mock_repo.create.assert_called_once_with(
            user_id="user-abc",
            order_id="order-xyz",
            message="Tu pedido ha sido pagado exitosamente y está siendo procesado.",
        )
        assert result["userId"] == "user-abc"
        assert result["orderId"] == "order-xyz"
        assert result["read"] is False

    def test_message_for_pagado_status(self, service, mock_repo):
        """El mensaje para estado 'pagado' debe ser el correcto."""
        mock_repo.create.return_value = {"id": "n1", "read": False}

        service.notify_order_status_change("u1", "o1", "pagado")

        _, kwargs = mock_repo.create.call_args
        assert "pagado" in kwargs["message"].lower() or "procesado" in kwargs["message"].lower()

    def test_message_for_en_preparacion_status(self, service, mock_repo):
        """El mensaje para estado 'en_preparacion' debe mencionar preparación."""
        mock_repo.create.return_value = {"id": "n1", "read": False}

        service.notify_order_status_change("u1", "o1", "en_preparacion")

        _, kwargs = mock_repo.create.call_args
        assert "preparad" in kwargs["message"].lower()

    def test_message_for_enviado_status(self, service, mock_repo):
        """El mensaje para estado 'enviado' debe mencionar envío."""
        mock_repo.create.return_value = {"id": "n1", "read": False}

        service.notify_order_status_change("u1", "o1", "enviado")

        _, kwargs = mock_repo.create.call_args
        assert "enviado" in kwargs["message"].lower() or "camino" in kwargs["message"].lower()

    def test_message_for_entregado_status(self, service, mock_repo):
        """El mensaje para estado 'entregado' debe mencionar entrega."""
        mock_repo.create.return_value = {"id": "n1", "read": False}

        service.notify_order_status_change("u1", "o1", "entregado")

        _, kwargs = mock_repo.create.call_args
        assert "entregado" in kwargs["message"].lower()

    def test_message_for_cancelado_status(self, service, mock_repo):
        """El mensaje para estado 'cancelado' debe mencionar cancelación."""
        mock_repo.create.return_value = {"id": "n1", "read": False}

        service.notify_order_status_change("u1", "o1", "cancelado")

        _, kwargs = mock_repo.create.call_args
        assert "cancelado" in kwargs["message"].lower()

    def test_unknown_status_uses_fallback_message(self, service, mock_repo):
        """Un estado desconocido debe usar un mensaje genérico con el nombre del estado."""
        mock_repo.create.return_value = {"id": "n1", "read": False}

        service.notify_order_status_change("u1", "o1", "estado_raro")

        _, kwargs = mock_repo.create.call_args
        assert "estado_raro" in kwargs["message"]

    def test_raises_notification_service_error_on_repo_failure(self, service, mock_repo):
        """Si el repositorio falla, debe lanzar NotificationServiceError."""
        mock_repo.create.side_effect = NotificationRepositoryError(
            "Error de Firestore", "FIRESTORE_WRITE_ERROR"
        )

        with pytest.raises(NotificationServiceError) as exc_info:
            service.notify_order_status_change("u1", "o1", "pagado")

        assert exc_info.value.code == "FIRESTORE_WRITE_ERROR"

    def test_returns_notification_data(self, service, mock_repo):
        """El método debe retornar los datos de la notificación creada."""
        expected = {
            "id": "notif-999",
            "userId": "user-1",
            "orderId": "order-1",
            "message": "Tu pedido ha sido enviado y está en camino.",
            "read": False,
        }
        mock_repo.create.return_value = expected

        result = service.notify_order_status_change("user-1", "order-1", "enviado")

        assert result == expected


# ---------------------------------------------------------------------------
# Tests de NotificationRepository.create (con Firestore mockeado)
# ---------------------------------------------------------------------------

class TestNotificationRepository:
    """Tests del repositorio de notificaciones con Firestore mockeado."""

    def test_create_writes_correct_fields_to_firestore(self):
        """El repositorio debe escribir userId, orderId, message y read=False en Firestore."""
        mock_db = MagicMock()
        mock_doc_ref = MagicMock()
        mock_db.collection.return_value.document.return_value = mock_doc_ref

        repo = NotificationRepository.__new__(NotificationRepository)
        repo._db = mock_db

        result = repo.create(
            user_id="user-abc",
            order_id="order-xyz",
            message="Tu pedido ha sido pagado.",
        )

        # Verificar que se llamó a set() con los campos correctos
        mock_doc_ref.set.assert_called_once()
        written_data = mock_doc_ref.set.call_args[0][0]

        assert written_data["userId"] == "user-abc"
        assert written_data["orderId"] == "order-xyz"
        assert written_data["message"] == "Tu pedido ha sido pagado."
        assert written_data["read"] is False
        assert "createdAt" in written_data

    def test_create_returns_notification_with_id(self):
        """El repositorio debe retornar los datos con el id generado."""
        mock_db = MagicMock()
        mock_doc_ref = MagicMock()
        mock_db.collection.return_value.document.return_value = mock_doc_ref

        repo = NotificationRepository.__new__(NotificationRepository)
        repo._db = mock_db

        result = repo.create(
            user_id="user-1",
            order_id="order-1",
            message="Mensaje de prueba.",
        )

        assert "id" in result
        assert result["userId"] == "user-1"
        assert result["orderId"] == "order-1"
        assert result["read"] is False

    def test_create_raises_repository_error_on_firestore_failure(self):
        """Si Firestore falla, debe lanzar NotificationRepositoryError."""
        mock_db = MagicMock()
        mock_doc_ref = MagicMock()
        mock_doc_ref.set.side_effect = Exception("Firestore connection error")
        mock_db.collection.return_value.document.return_value = mock_doc_ref

        repo = NotificationRepository.__new__(NotificationRepository)
        repo._db = mock_db

        with pytest.raises(NotificationRepositoryError) as exc_info:
            repo.create("u1", "o1", "msg")

        assert exc_info.value.code == "FIRESTORE_WRITE_ERROR"


# ---------------------------------------------------------------------------
# Tests de integración: OrderService llama a NotificationService (Req. 19.2)
# ---------------------------------------------------------------------------

class TestOrderServiceNotificationIntegration:
    """Verifica que OrderService notifica al consumidor al cambiar el estado (Req. 19.2)."""

    def test_update_order_status_calls_notification_service(self):
        """Al actualizar el estado, OrderService debe llamar a notify_order_status_change."""
        from services.order_service import OrderService

        mock_order_repo = MagicMock()
        mock_notification_svc = MagicMock(spec=NotificationService)
        mock_product_repo = MagicMock()

        mock_order_repo.get_by_id.return_value = {
            "id": "order-1",
            "consumerId": "consumer-1",
            "status": "pagado",
            "items": [],
        }
        mock_order_repo.update_order.return_value = {
            "id": "order-1",
            "consumerId": "consumer-1",
            "status": "en_preparacion",
        }

        service = OrderService(
            order_repository=mock_order_repo,
            notification_service=mock_notification_svc,
            product_repository=mock_product_repo,
        )

        service.update_order_status(
            order_id="order-1",
            new_status="en_preparacion",
            requester_id="admin-1",
            requester_role="ADMIN",
        )

        mock_notification_svc.notify_order_status_change.assert_called_once_with(
            user_id="consumer-1",
            order_id="order-1",
            new_status="en_preparacion",
        )

    def test_update_order_status_does_not_fail_if_notification_fails(self):
        """Si la notificación falla, la actualización del pedido no debe fallar."""
        from services.order_service import OrderService

        mock_order_repo = MagicMock()
        mock_notification_svc = MagicMock(spec=NotificationService)
        mock_product_repo = MagicMock()

        mock_order_repo.get_by_id.return_value = {
            "id": "order-1",
            "consumerId": "consumer-1",
            "status": "pagado",
            "items": [],
        }
        mock_order_repo.update_order.return_value = {
            "id": "order-1",
            "status": "en_preparacion",
        }
        mock_notification_svc.notify_order_status_change.side_effect = NotificationServiceError(
            "Firestore error", "FIRESTORE_WRITE_ERROR"
        )

        service = OrderService(
            order_repository=mock_order_repo,
            notification_service=mock_notification_svc,
            product_repository=mock_product_repo,
        )

        # No debe lanzar excepción aunque la notificación falle
        result = service.update_order_status(
            order_id="order-1",
            new_status="en_preparacion",
            requester_id="admin-1",
            requester_role="ADMIN",
        )

        assert result["status"] == "en_preparacion"
