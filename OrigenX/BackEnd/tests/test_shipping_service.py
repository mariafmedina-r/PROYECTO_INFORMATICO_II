"""
test_shipping_service.py – Tests unitarios para ShippingService.

Verifica la lógica de opciones de envío.

Requerimientos: 14.1, 14.2, 14.3, 14.4
"""

import os
from unittest.mock import patch

import pytest

from services.shipping_service import (
    ShippingService,
    ShippingServiceUnavailableError,
)


# ---------------------------------------------------------------------------
# Tests – get_options (Req. 14.1, 14.3)
# ---------------------------------------------------------------------------

class TestGetOptions:
    """Tests del método get_options (Req. 14.1, 14.3)."""

    def test_returns_list_of_shipping_options(self):
        """Debe retornar una lista de empresas de envío disponibles (Req. 14.1)."""
        service = ShippingService()
        with patch.dict(os.environ, {"SHIPPING_SERVICE_ENABLED": "true"}):
            options = service.get_options()

        assert isinstance(options, list)
        assert len(options) > 0

    def test_each_option_has_required_fields(self):
        """Cada opción debe tener id, name, estimated_days, cost y description (Req. 14.1)."""
        service = ShippingService()
        with patch.dict(os.environ, {"SHIPPING_SERVICE_ENABLED": "true"}):
            options = service.get_options()

        for option in options:
            assert "id" in option
            assert "name" in option
            assert "estimated_days" in option
            assert "cost" in option
            assert "description" in option

    def test_options_have_positive_costs(self):
        """Todas las opciones deben tener costos positivos (Req. 14.2)."""
        service = ShippingService()
        with patch.dict(os.environ, {"SHIPPING_SERVICE_ENABLED": "true"}):
            options = service.get_options()

        for option in options:
            assert option["cost"] > 0

    def test_options_have_positive_estimated_days(self):
        """Todas las opciones deben tener tiempos estimados positivos."""
        service = ShippingService()
        with patch.dict(os.environ, {"SHIPPING_SERVICE_ENABLED": "true"}):
            options = service.get_options()

        for option in options:
            assert option["estimated_days"] > 0

    def test_raises_unavailable_when_disabled(self):
        """Debe lanzar ShippingServiceUnavailableError cuando el servicio está deshabilitado (Req. 14.3)."""
        service = ShippingService()
        with patch.dict(os.environ, {"SHIPPING_SERVICE_ENABLED": "false"}):
            with pytest.raises(ShippingServiceUnavailableError) as exc_info:
                service.get_options()

        assert exc_info.value.code == "SHIPPING_SERVICE_UNAVAILABLE"

    def test_raises_unavailable_when_disabled_uppercase(self):
        """Debe lanzar error cuando SHIPPING_SERVICE_ENABLED=FALSE (case insensitive)."""
        service = ShippingService()
        with patch.dict(os.environ, {"SHIPPING_SERVICE_ENABLED": "FALSE"}):
            with pytest.raises(ShippingServiceUnavailableError):
                service.get_options()

    def test_returns_copy_of_options(self):
        """Debe retornar una copia de la lista, no la referencia original."""
        service = ShippingService()
        with patch.dict(os.environ, {"SHIPPING_SERVICE_ENABLED": "true"}):
            options1 = service.get_options()
            options2 = service.get_options()

        # Modificar la primera lista no debe afectar la segunda
        options1.clear()
        assert len(options2) > 0

    def test_includes_known_shipping_companies(self):
        """Debe incluir las empresas de envío configuradas."""
        service = ShippingService()
        with patch.dict(os.environ, {"SHIPPING_SERVICE_ENABLED": "true"}):
            options = service.get_options()

        option_ids = [o["id"] for o in options]
        # Verificar que al menos una empresa conocida está presente
        assert any(oid in option_ids for oid in ["servientrega", "coordinadora", "interrapidisimo", "deprisa"])


# ---------------------------------------------------------------------------
# Tests – get_option_by_id (Req. 14.1, 14.4)
# ---------------------------------------------------------------------------

class TestGetOptionById:
    """Tests del método get_option_by_id (Req. 14.4)."""

    def test_returns_option_for_valid_id(self):
        """Debe retornar la opción correcta para un ID válido (Req. 14.4)."""
        service = ShippingService()
        with patch.dict(os.environ, {"SHIPPING_SERVICE_ENABLED": "true"}):
            options = service.get_options()
            first_id = options[0]["id"]
            result = service.get_option_by_id(first_id)

        assert result is not None
        assert result["id"] == first_id

    def test_returns_none_for_invalid_id(self):
        """Debe retornar None para un ID que no existe."""
        service = ShippingService()
        with patch.dict(os.environ, {"SHIPPING_SERVICE_ENABLED": "true"}):
            result = service.get_option_by_id("nonexistent-company")

        assert result is None

    def test_raises_unavailable_when_service_disabled(self):
        """Debe lanzar ShippingServiceUnavailableError cuando el servicio está deshabilitado (Req. 14.3)."""
        service = ShippingService()
        with patch.dict(os.environ, {"SHIPPING_SERVICE_ENABLED": "false"}):
            with pytest.raises(ShippingServiceUnavailableError):
                service.get_option_by_id("servientrega")

    def test_returns_correct_cost_for_option(self):
        """La opción retornada debe tener el costo correcto (Req. 14.2)."""
        service = ShippingService()
        with patch.dict(os.environ, {"SHIPPING_SERVICE_ENABLED": "true"}):
            options = service.get_options()
            first_option = options[0]
            result = service.get_option_by_id(first_option["id"])

        assert result["cost"] == first_option["cost"]
        assert result["estimated_days"] == first_option["estimated_days"]

    def test_returns_servientrega_when_exists(self):
        """Debe retornar Servientrega si está configurada."""
        service = ShippingService()
        with patch.dict(os.environ, {"SHIPPING_SERVICE_ENABLED": "true"}):
            result = service.get_option_by_id("servientrega")

        if result is not None:
            assert result["name"] == "Servientrega"
            assert result["cost"] > 0
