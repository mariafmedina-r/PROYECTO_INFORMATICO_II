"""
test_payment_service.py – Tests unitarios para PaymentService.

Verifica la lógica de simulación de pagos sin pasarela real.

Requerimientos: 17.1, 17.2, 17.3, 17.4, 17.5
"""

from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import pytest

from services.payment_service import (
    PaymentService,
    PaymentServiceError,
    PaymentOrderNotFoundError,
    PaymentOrderForbiddenError,
    PaymentOrderNotPendingError,
    PaymentSimulatedFailureError,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_order(
    order_id="order-1",
    consumer_id="consumer-123",
    status="pendiente",
    transaction_id=None,
):
    return {
        "id": order_id,
        "consumerId": consumer_id,
        "status": status,
        "transactionId": transaction_id,
        "total": 75000.0,
        "createdAt": datetime(2024, 6, 1, tzinfo=timezone.utc),
        "updatedAt": datetime(2024, 6, 1, tzinfo=timezone.utc),
    }


def _make_service(mock_order_repo):
    return PaymentService(order_repository=mock_order_repo)


# ---------------------------------------------------------------------------
# Tests – simulate_payment (Req. 17.1–17.5)
# ---------------------------------------------------------------------------

class TestSimulatePaymentSuccess:
    """Tests para el flujo de pago exitoso (Req. 17.2, 17.5)."""

    def test_successful_payment_returns_success_true(self):
        """Pago exitoso debe retornar success=True (Req. 17.2)."""
        mock_repo = MagicMock()
        mock_repo.get_by_id.return_value = _make_order()
        mock_repo.update_order.return_value = _make_order(status="pagado")

        service = _make_service(mock_repo)
        result = service.simulate_payment(
            consumer_id="consumer-123",
            order_id="order-1",
            card_number="1234567890123456",
            card_holder="Juan Pérez",
            expiry_date="12/26",
            cvv="123",
            amount=75000.0,
        )

        assert result["success"] is True
        assert result["order_status"] == "pagado"

    def test_successful_payment_generates_sim_transaction_id(self):
        """Pago exitoso debe generar transaction_id con formato SIM-{uuid} (Req. 17.5)."""
        mock_repo = MagicMock()
        mock_repo.get_by_id.return_value = _make_order()
        mock_repo.update_order.return_value = _make_order(status="pagado")

        service = _make_service(mock_repo)
        result = service.simulate_payment(
            consumer_id="consumer-123",
            order_id="order-1",
            card_number="1234567890123456",
            card_holder="Juan Pérez",
            expiry_date="12/26",
            cvv="123",
            amount=75000.0,
        )

        assert result["transaction_id"].startswith("SIM-")
        # UUID format: SIM-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
        parts = result["transaction_id"].split("-")
        assert parts[0] == "SIM"
        assert len(parts) == 6  # SIM + 5 UUID parts

    def test_successful_payment_updates_order_to_pagado(self):
        """Pago exitoso debe actualizar el pedido a estado 'pagado' (Req. 17.2)."""
        mock_repo = MagicMock()
        mock_repo.get_by_id.return_value = _make_order()
        mock_repo.update_order.return_value = _make_order(status="pagado")

        service = _make_service(mock_repo)
        service.simulate_payment(
            consumer_id="consumer-123",
            order_id="order-1",
            card_number="9999999999999999",
            card_holder="Test User",
            expiry_date="01/27",
            cvv="456",
            amount=75000.0,
        )

        mock_repo.update_order.assert_called_once()
        call_args = mock_repo.update_order.call_args
        assert call_args[0][0] == "order-1"
        update_data = call_args[0][1]
        assert update_data["status"] == "pagado"
        assert update_data["transactionId"].startswith("SIM-")

    def test_card_data_not_stored_in_firestore(self):
        """Los datos de tarjeta NO deben almacenarse en Firestore (Req. 17.4)."""
        mock_repo = MagicMock()
        mock_repo.get_by_id.return_value = _make_order()
        mock_repo.update_order.return_value = _make_order(status="pagado")

        service = _make_service(mock_repo)
        service.simulate_payment(
            consumer_id="consumer-123",
            order_id="order-1",
            card_number="1234567890123456",
            card_holder="Juan Pérez",
            expiry_date="12/26",
            cvv="123",
            amount=75000.0,
        )

        # Verificar que los datos de tarjeta NO están en la llamada a update_order
        call_args = mock_repo.update_order.call_args
        update_data = call_args[0][1]
        assert "cardNumber" not in update_data
        assert "card_number" not in update_data
        assert "cardHolder" not in update_data
        assert "cvv" not in update_data
        assert "expiryDate" not in update_data


class TestSimulatePaymentFailure:
    """Tests para el flujo de pago fallido (Req. 17.3)."""

    def test_card_ending_0000_raises_simulated_failure(self):
        """Tarjeta terminada en '0000' debe lanzar PaymentSimulatedFailureError (Req. 17.3)."""
        mock_repo = MagicMock()
        mock_repo.get_by_id.return_value = _make_order()

        service = _make_service(mock_repo)

        with pytest.raises(PaymentSimulatedFailureError) as exc_info:
            service.simulate_payment(
                consumer_id="consumer-123",
                order_id="order-1",
                card_number="1234567890120000",
                card_holder="Juan Pérez",
                expiry_date="12/26",
                cvv="123",
                amount=75000.0,
            )

        assert exc_info.value.code == "PAYMENT_DECLINED"

    def test_failed_payment_does_not_update_order(self):
        """Pago fallido NO debe actualizar el estado del pedido (Req. 17.3)."""
        mock_repo = MagicMock()
        mock_repo.get_by_id.return_value = _make_order()

        service = _make_service(mock_repo)

        with pytest.raises(PaymentSimulatedFailureError):
            service.simulate_payment(
                consumer_id="consumer-123",
                order_id="order-1",
                card_number="0000000000000000",
                card_holder="Test",
                expiry_date="01/27",
                cvv="000",
                amount=75000.0,
            )

        # El pedido NO debe ser actualizado
        mock_repo.update_order.assert_not_called()

    def test_card_not_ending_0000_succeeds(self):
        """Tarjeta que NO termina en '0000' debe procesar exitosamente."""
        mock_repo = MagicMock()
        mock_repo.get_by_id.return_value = _make_order()
        mock_repo.update_order.return_value = _make_order(status="pagado")

        service = _make_service(mock_repo)
        result = service.simulate_payment(
            consumer_id="consumer-123",
            order_id="order-1",
            card_number="1234567890120001",  # termina en 0001, no 0000
            card_holder="Test",
            expiry_date="01/27",
            cvv="123",
            amount=75000.0,
        )

        assert result["success"] is True


class TestSimulatePaymentValidation:
    """Tests de validación de pedido antes del pago."""

    def test_order_not_found_raises_error(self):
        """Pedido inexistente debe lanzar PaymentOrderNotFoundError."""
        mock_repo = MagicMock()
        mock_repo.get_by_id.return_value = None

        service = _make_service(mock_repo)

        with pytest.raises(PaymentOrderNotFoundError) as exc_info:
            service.simulate_payment(
                consumer_id="consumer-123",
                order_id="nonexistent",
                card_number="1234567890123456",
                card_holder="Test",
                expiry_date="01/27",
                cvv="123",
                amount=75000.0,
            )

        assert exc_info.value.code == "ORDER_NOT_FOUND"

    def test_order_belonging_to_other_consumer_raises_forbidden(self):
        """Pedido de otro consumidor debe lanzar PaymentOrderForbiddenError."""
        mock_repo = MagicMock()
        mock_repo.get_by_id.return_value = _make_order(consumer_id="other-consumer")

        service = _make_service(mock_repo)

        with pytest.raises(PaymentOrderForbiddenError) as exc_info:
            service.simulate_payment(
                consumer_id="consumer-123",
                order_id="order-1",
                card_number="1234567890123456",
                card_holder="Test",
                expiry_date="01/27",
                cvv="123",
                amount=75000.0,
            )

        assert exc_info.value.code == "PAYMENT_FORBIDDEN"

    def test_order_not_pending_raises_error(self):
        """Pedido que no está en estado 'pendiente' debe lanzar PaymentOrderNotPendingError."""
        mock_repo = MagicMock()
        mock_repo.get_by_id.return_value = _make_order(status="pagado")

        service = _make_service(mock_repo)

        with pytest.raises(PaymentOrderNotPendingError) as exc_info:
            service.simulate_payment(
                consumer_id="consumer-123",
                order_id="order-1",
                card_number="1234567890123456",
                card_holder="Test",
                expiry_date="01/27",
                cvv="123",
                amount=75000.0,
            )

        assert exc_info.value.code == "ORDER_NOT_PENDING"

    def test_order_in_preparacion_raises_not_pending(self):
        """Pedido en estado 'en_preparacion' no puede ser pagado."""
        mock_repo = MagicMock()
        mock_repo.get_by_id.return_value = _make_order(status="en_preparacion")

        service = _make_service(mock_repo)

        with pytest.raises(PaymentOrderNotPendingError):
            service.simulate_payment(
                consumer_id="consumer-123",
                order_id="order-1",
                card_number="1234567890123456",
                card_holder="Test",
                expiry_date="01/27",
                cvv="123",
                amount=75000.0,
            )

    def test_repository_error_raises_payment_service_error(self):
        """Error del repositorio debe lanzar PaymentServiceError."""
        from repositories.order_repository import OrderRepositoryError

        mock_repo = MagicMock()
        mock_repo.get_by_id.side_effect = OrderRepositoryError(
            "Firestore error", "FIRESTORE_READ_ERROR"
        )

        service = _make_service(mock_repo)

        with pytest.raises(PaymentServiceError) as exc_info:
            service.simulate_payment(
                consumer_id="consumer-123",
                order_id="order-1",
                card_number="1234567890123456",
                card_holder="Test",
                expiry_date="01/27",
                cvv="123",
                amount=75000.0,
            )

        assert exc_info.value.code == "FIRESTORE_READ_ERROR"

    def test_update_order_error_raises_payment_service_error(self):
        """Error al actualizar el pedido debe lanzar PaymentServiceError."""
        from repositories.order_repository import OrderRepositoryError

        mock_repo = MagicMock()
        mock_repo.get_by_id.return_value = _make_order()
        mock_repo.update_order.side_effect = OrderRepositoryError(
            "Firestore write error", "FIRESTORE_WRITE_ERROR"
        )

        service = _make_service(mock_repo)

        with pytest.raises(PaymentServiceError) as exc_info:
            service.simulate_payment(
                consumer_id="consumer-123",
                order_id="order-1",
                card_number="1234567890123456",
                card_holder="Test",
                expiry_date="01/27",
                cvv="123",
                amount=75000.0,
            )

        assert exc_info.value.code == "FIRESTORE_WRITE_ERROR"
