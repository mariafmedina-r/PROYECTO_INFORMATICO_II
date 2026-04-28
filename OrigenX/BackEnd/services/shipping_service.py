"""
services/shipping_service.py – Servicio de opciones de envío.

Responsabilidades:
  - Retornar lista estática configurable de empresas de envío
  - Tarifas y tiempos estimados de entrega
  - Retornar HTTP 503 si el módulo no está disponible

Requerimientos: 14.1, 14.2, 14.3, 14.4
"""

import logging
import os

logger = logging.getLogger(__name__)

# Lista estática configurable de empresas de envío.
# En producción se podría cargar desde una variable de entorno o archivo de configuración.
_DEFAULT_SHIPPING_OPTIONS: list[dict] = [
    {
        "id": "servientrega",
        "name": "Servientrega",
        "estimated_days": 3,
        "cost": 12000.0,
        "description": "Entrega en 3 días hábiles a nivel nacional.",
    },
    {
        "id": "coordinadora",
        "name": "Coordinadora",
        "estimated_days": 2,
        "cost": 15000.0,
        "description": "Entrega en 2 días hábiles a nivel nacional.",
    },
    {
        "id": "interrapidisimo",
        "name": "Interrapidísimo",
        "estimated_days": 4,
        "cost": 9500.0,
        "description": "Entrega en 4 días hábiles a nivel nacional.",
    },
    {
        "id": "deprisa",
        "name": "Deprisa",
        "estimated_days": 2,
        "cost": 18000.0,
        "description": "Entrega express en 2 días hábiles.",
    },
]


class ShippingServiceError(Exception):
    """Error base del servicio de envío."""

    def __init__(self, message: str, code: str = "SHIPPING_SERVICE_ERROR"):
        self.message = message
        self.code = code
        super().__init__(message)


class ShippingServiceUnavailableError(ShippingServiceError):
    """El módulo de envío no está disponible (Req. 14.3)."""

    def __init__(self):
        super().__init__(
            message="El servicio de envío no está disponible temporalmente. Intenta más tarde.",
            code="SHIPPING_SERVICE_UNAVAILABLE",
        )


class ShippingService:
    """Servicio de opciones de envío (datos estáticos configurables)."""

    def get_options(self) -> list[dict]:
        """
        Retorna la lista de empresas de envío disponibles con tarifas y tiempos estimados.

        La lista se puede deshabilitar mediante la variable de entorno
        SHIPPING_SERVICE_ENABLED=false para simular indisponibilidad (Req. 14.3).

        Returns:
            Lista de diccionarios con id, name, estimated_days, cost, description.

        Raises:
            ShippingServiceUnavailableError: Si el módulo de envío está deshabilitado.
        """
        # Verificar disponibilidad del módulo (Req. 14.3)
        enabled = os.getenv("SHIPPING_SERVICE_ENABLED", "true").lower()
        if enabled != "true":
            logger.warning("Módulo de envío deshabilitado por variable de entorno.")
            raise ShippingServiceUnavailableError()

        return list(_DEFAULT_SHIPPING_OPTIONS)

    def get_option_by_id(self, option_id: str) -> dict | None:
        """
        Busca una empresa de envío por su ID.

        Args:
            option_id: Identificador de la empresa de envío.

        Returns:
            Diccionario con los datos de la empresa, o None si no existe.

        Raises:
            ShippingServiceUnavailableError: Si el módulo de envío está deshabilitado.
        """
        options = self.get_options()
        for option in options:
            if option["id"] == option_id:
                return option
        return None
