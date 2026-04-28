"""
services/payment_service.py – Simulador de pagos interno.

Responsabilidades:
  - Simular procesamiento de pagos (sin pasarela real)
  - Lógica de simulación:
      * cardNumber termina en '0000' → fallo simulado
      * Cualquier otro número de 16 dígitos → éxito simulado
  - Generar transaction_id con formato SIM-{uuid}
  - Actualizar estado del pedido a 'pagado' y registrar transaction_id
  - NO almacenar datos de tarjeta en Firestore

Requerimientos: 17.1, 17.2, 17.3, 17.4, 17.5
"""

import logging
import uuid
from datetime import datetime, timezone
from typing import Optional

from repositories.order_repository import OrderRepository, OrderRepositoryError

logger = logging.getLogger(__name__)


class PaymentServiceError(Exception):
    """Error base del servicio de pagos."""

    def __init__(self, message: str, code: str = "PAYMENT_SERVICE_ERROR"):
        self.message = message
        self.code = code
        super().__init__(message)


class PaymentOrderNotFoundError(PaymentServiceError):
    """El pedido no existe."""

    def __init__(self, order_id: str):
        super().__init__(
            message=f"Pedido con id '{order_id}' no encontrado.",
            code="ORDER_NOT_FOUND",
        )


class PaymentOrderNotPendingError(PaymentServiceError):
    """El pedido no está en estado 'pendiente'."""

    def __init__(self, order_id: str, current_status: str):
        super().__init__(
            message=(
                f"El pedido '{order_id}' no puede ser pagado porque su estado actual es "
                f"'{current_status}'. Solo se pueden pagar pedidos en estado 'pendiente'."
            ),
            code="ORDER_NOT_PENDING",
        )


class PaymentOrderForbiddenError(PaymentServiceError):
    """El pedido no pertenece al consumidor autenticado."""

    def __init__(self):
        super().__init__(
            message="No tienes permiso para pagar este pedido.",
            code="PAYMENT_FORBIDDEN",
        )


class PaymentSimulatedFailureError(PaymentServiceError):
    """Fallo de pago simulado (cardNumber termina en '0000')."""

    def __init__(self):
        super().__init__(
            message=(
                "El pago fue rechazado (simulación). "
                "Usa un número de tarjeta diferente para simular un pago exitoso."
            ),
            code="PAYMENT_DECLINED",
        )


class PaymentService:
    """Simulador de pagos interno (Req. 17.1 – 17.5)."""

    def __init__(self, order_repository: Optional[OrderRepository] = None):
        self._order_repo = order_repository or OrderRepository()

    def simulate_payment(
        self,
        consumer_id: str,
        order_id: str,
        card_number: str,
        card_holder: str,
        expiry_date: str,
        cvv: str,
        amount: float,
    ) -> dict:
        """
        Simula el procesamiento de un pago para un pedido.

        Lógica de simulación (Req. 17.2, 17.3):
          - Si card_number termina en '0000' → fallo simulado.
            El pedido permanece en estado 'pendiente'.
          - Cualquier otro número de 16 dígitos → éxito simulado.
            El pedido se actualiza a 'pagado' y se registra el transaction_id.

        Los datos de tarjeta (card_number, card_holder, expiry_date, cvv) NO se
        almacenan en Firestore (Req. 17.4).

        Args:
            consumer_id: UID del consumidor autenticado.
            order_id: ID del pedido a pagar.
            card_number: Número de tarjeta de 16 dígitos (ficticio).
            card_holder: Nombre del titular (ficticio).
            expiry_date: Fecha de vencimiento MM/YY (ficticia).
            cvv: Código de seguridad (ficticio).
            amount: Monto a cobrar.

        Returns:
            Diccionario con:
              - success (bool)
              - transaction_id (str | None): SIM-{uuid} si exitoso
              - message (str)
              - order_status (str)

        Raises:
            PaymentOrderNotFoundError: Si el pedido no existe.
            PaymentOrderForbiddenError: Si el pedido no pertenece al consumidor.
            PaymentOrderNotPendingError: Si el pedido no está en estado 'pendiente'.
            PaymentSimulatedFailureError: Si card_number termina en '0000'.
            PaymentServiceError: Para otros errores internos.
        """
        # 1. Obtener el pedido
        try:
            order = self._order_repo.get_by_id(order_id)
        except OrderRepositoryError as exc:
            raise PaymentServiceError(exc.message, exc.code) from exc

        if order is None:
            raise PaymentOrderNotFoundError(order_id)

        # 2. Verificar que el pedido pertenece al consumidor (Req. 17.4)
        if order.get("consumerId") != consumer_id:
            raise PaymentOrderForbiddenError()

        # 3. Verificar que el pedido está en estado 'pendiente'
        current_status = order.get("status")
        if current_status != "pendiente":
            raise PaymentOrderNotPendingError(order_id, current_status)

        # 4. Lógica de simulación (Req. 17.2, 17.3)
        # Los datos de tarjeta se usan solo para la simulación, NO se persisten
        if card_number.endswith("0000"):
            # Fallo simulado – el pedido permanece en 'pendiente'
            raise PaymentSimulatedFailureError()

        # Éxito simulado – generar transaction_id con formato SIM-{uuid} (Req. 17.5)
        transaction_id = f"SIM-{uuid.uuid4()}"
        now = datetime.now(timezone.utc)

        # 5. Actualizar pedido a 'pagado' y registrar transaction_id (Req. 17.2)
        # Solo se persiste el transaction_id, NO los datos de tarjeta (Req. 17.4)
        try:
            self._order_repo.update_order(
                order_id,
                {
                    "status": "pagado",
                    "transactionId": transaction_id,
                    "updatedAt": now,
                },
            )
        except OrderRepositoryError as exc:
            raise PaymentServiceError(exc.message, exc.code) from exc

        logger.info(
            "Pago simulado exitoso para pedido '%s'. transaction_id='%s'.",
            order_id, transaction_id,
        )

        return {
            "success": True,
            "transaction_id": transaction_id,
            "message": "Pago procesado exitosamente (simulación).",
            "order_status": "pagado",
        }
