"""
routes/payments.py – Endpoints del simulador de pagos.

Endpoints:
  POST /api/payments/simulate → Simular pago (tarea 8.4)

Requerimientos: 17.1, 17.2, 17.3, 17.4, 17.5
"""

import logging

from fastapi import APIRouter, Depends, HTTPException, status

from middleware.auth_middleware import require_consumer
from models.payment import PaymentSimulateRequest, PaymentSimulateResponse
from services.payment_service import (
    PaymentOrderForbiddenError,
    PaymentOrderNotFoundError,
    PaymentOrderNotPendingError,
    PaymentService,
    PaymentServiceError,
    PaymentSimulatedFailureError,
)

logger = logging.getLogger(__name__)
router = APIRouter()


def _make_error(code: str, message: str, fields: list | None = None) -> dict:
    """Construye el cuerpo de error uniforme (RNF-009.3)."""
    body: dict = {"code": code, "message": message}
    if fields:
        body["fields"] = fields
    return {"error": body}


# ------------------------------------------------------------------
# POST /api/payments/simulate – Simular pago (Req. 17.1 – 17.5)
# ------------------------------------------------------------------

@router.post(
    "/simulate",
    status_code=status.HTTP_200_OK,
    response_model=PaymentSimulateResponse,
    summary="Simular pago",
    description=(
        "Simula el procesamiento de un pago para un pedido en estado 'pendiente'. "
        "Si cardNumber termina en '0000' → fallo simulado, pedido permanece en 'pendiente'. "
        "Cualquier otro número de 16 dígitos → pago exitoso, pedido pasa a 'pagado'. "
        "Los datos de tarjeta NO se almacenan en Firestore. "
        "Requiere rol CONSUMER. "
        "Requerimientos: 17.1, 17.2, 17.3, 17.4, 17.5"
    ),
)
async def simulate_payment(
    payload: PaymentSimulateRequest,
    current_user: dict = Depends(require_consumer),
):
    """
    Simula el procesamiento de un pago.

    Lógica de simulación (Req. 17.2, 17.3):
    - cardNumber termina en '0000' → HTTP 402, pedido permanece en 'pendiente'.
    - Cualquier otro número de 16 dígitos → pago exitoso, pedido pasa a 'pagado',
      se registra transaction_id con formato SIM-{uuid} (Req. 17.5).

    Los datos de tarjeta (cardNumber, cardHolder, expiryDate, cvv) NO se persisten
    en Firestore (Req. 17.4). Solo se almacena el transaction_id generado.
    """
    consumer_id = current_user.get("uid")
    service = PaymentService()

    try:
        result = service.simulate_payment(
            consumer_id=consumer_id,
            order_id=payload.order_id,
            card_number=payload.card_number,
            card_holder=payload.card_holder,
            expiry_date=payload.expiry_date,
            cvv=payload.cvv,
            amount=payload.amount,
        )
    except PaymentOrderNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=_make_error(code=exc.code, message=exc.message),
        ) from exc
    except PaymentOrderForbiddenError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=_make_error(code=exc.code, message=exc.message),
        ) from exc
    except PaymentOrderNotPendingError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=_make_error(code=exc.code, message=exc.message),
        ) from exc
    except PaymentSimulatedFailureError as exc:
        # Fallo simulado – el pedido permanece en 'pendiente' (Req. 17.3)
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail=_make_error(code=exc.code, message=exc.message),
        ) from exc
    except PaymentServiceError as exc:
        logger.error(
            "Error en simulador de pagos para consumidor '%s', pedido '%s': %s",
            consumer_id, payload.order_id, exc,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=_make_error(code=exc.code, message=exc.message),
        ) from exc
    except Exception as exc:
        logger.error(
            "Error inesperado en simulador de pagos para consumidor '%s': %s",
            consumer_id, exc,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=_make_error(
                code="INTERNAL_ERROR",
                message="Error interno al procesar el pago.",
            ),
        ) from exc

    return result
