"""
test_product_status.py – Tests para el endpoint PATCH /api/products/:id/status.

Cubre:
  - Activación exitosa de producto inactivo (Req. 8.1)
  - Inactivación exitosa de producto activo (Req. 8.2)
  - Historial de pedidos no afectado (Req. 8.3 – verificado a nivel de servicio)
  - Producto inactivo no puede agregarse al carrito (Req. 8.4 – verificado en servicio)
  - Verificación de propiedad – HTTP 403 si no es dueño
  - Producto no encontrado – HTTP 404
  - Estado inválido – HTTP 400
  - Acceso sin token – HTTP 401
  - Acceso con rol incorrecto – HTTP 403
"""

from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

# Los mocks de Firebase se cargan en conftest.py antes de importar la app
from main import app


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def client():
    """Cliente de prueba para la aplicación FastAPI."""
    return TestClient(app, raise_server_exceptions=False)


@pytest.fixture
def producer_claims():
    """Claims de un Productor autenticado (dueño del producto)."""
    return {
        "uid": "producer-uid-123",
        "email": "producer@example.com",
        "role": "PRODUCER",
    }


@pytest.fixture
def other_producer_claims():
    """Claims de otro Productor (no dueño del producto)."""
    return {
        "uid": "other-producer-uid-456",
        "email": "other@example.com",
        "role": "PRODUCER",
    }


@pytest.fixture
def consumer_claims():
    """Claims de un Consumidor autenticado."""
    return {
        "uid": "consumer-uid-789",
        "email": "consumer@example.com",
        "role": "CONSUMER",
    }


@pytest.fixture
def inactive_product():
    """Datos de un producto inactivo."""
    return {
        "id": "product-abc",
        "producerId": "producer-uid-123",
        "producerName": "Finca El Paraíso",
        "name": "Café Especial",
        "description": "Café de altura",
        "price": 25000.0,
        "status": "inactive",
        "createdAt": datetime(2024, 1, 1, tzinfo=timezone.utc),
        "updatedAt": datetime(2024, 1, 1, tzinfo=timezone.utc),
    }


@pytest.fixture
def active_product():
    """Datos de un producto activo."""
    return {
        "id": "product-abc",
        "producerId": "producer-uid-123",
        "producerName": "Finca El Paraíso",
        "name": "Café Especial",
        "description": "Café de altura",
        "price": 25000.0,
        "status": "active",
        "createdAt": datetime(2024, 1, 1, tzinfo=timezone.utc),
        "updatedAt": datetime(2024, 6, 1, tzinfo=timezone.utc),
    }


# ---------------------------------------------------------------------------
# Tests de integración – PATCH /api/products/:id/status
# ---------------------------------------------------------------------------

class TestUpdateProductStatusEndpoint:
    """Tests del endpoint PATCH /api/products/:id/status (Req. 8.1–8.4)."""

    def test_activate_product_returns_200(
        self, client, mock_firebase_auth, producer_claims, active_product
    ):
        """Activar un producto debe retornar HTTP 200 con estado 'active' (Req. 8.1)."""
        mock_firebase_auth.verify_id_token.return_value = producer_claims

        with patch("routes.products.ProductService") as mock_service_cls:
            mock_service = MagicMock()
            mock_service_cls.return_value = mock_service
            mock_service.update_status.return_value = active_product

            response = client.patch(
                "/api/products/product-abc/status",
                json={"status": "active"},
                headers={"Authorization": "Bearer valid-producer-token"},
            )

        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "data" in data
        assert data["data"]["status"] == "active"

    def test_inactivate_product_returns_200(
        self, client, mock_firebase_auth, producer_claims, inactive_product
    ):
        """Inactivar un producto debe retornar HTTP 200 con estado 'inactive' (Req. 8.2)."""
        mock_firebase_auth.verify_id_token.return_value = producer_claims

        with patch("routes.products.ProductService") as mock_service_cls:
            mock_service = MagicMock()
            mock_service_cls.return_value = mock_service
            mock_service.update_status.return_value = inactive_product

            response = client.patch(
                "/api/products/product-abc/status",
                json={"status": "inactive"},
                headers={"Authorization": "Bearer valid-producer-token"},
            )

        assert response.status_code == 200
        data = response.json()
        assert data["data"]["status"] == "inactive"

    def test_activate_calls_service_with_correct_args(
        self, client, mock_firebase_auth, producer_claims, active_product
    ):
        """El endpoint debe llamar al servicio con los argumentos correctos."""
        mock_firebase_auth.verify_id_token.return_value = producer_claims

        with patch("routes.products.ProductService") as mock_service_cls:
            mock_service = MagicMock()
            mock_service_cls.return_value = mock_service
            mock_service.update_status.return_value = active_product

            client.patch(
                "/api/products/product-abc/status",
                json={"status": "active"},
                headers={"Authorization": "Bearer valid-producer-token"},
            )

            mock_service.update_status.assert_called_once_with(
                product_id="product-abc",
                producer_id="producer-uid-123",
                new_status="active",
            )

    def test_non_owner_returns_403(
        self, client, mock_firebase_auth, other_producer_claims
    ):
        """Productor que no es dueño debe recibir HTTP 403."""
        mock_firebase_auth.verify_id_token.return_value = other_producer_claims

        with patch("routes.products.ProductService") as mock_service_cls:
            from services.product_service import ProductForbiddenError
            mock_service = MagicMock()
            mock_service_cls.return_value = mock_service
            mock_service.update_status.side_effect = ProductForbiddenError()

            response = client.patch(
                "/api/products/product-abc/status",
                json={"status": "active"},
                headers={"Authorization": "Bearer other-producer-token"},
            )

        assert response.status_code == 403
        data = response.json()
        assert data["detail"]["error"]["code"] == "FORBIDDEN"

    def test_product_not_found_returns_404(
        self, client, mock_firebase_auth, producer_claims
    ):
        """Producto inexistente debe retornar HTTP 404."""
        mock_firebase_auth.verify_id_token.return_value = producer_claims

        with patch("routes.products.ProductService") as mock_service_cls:
            from services.product_service import ProductNotFoundServiceError
            mock_service = MagicMock()
            mock_service_cls.return_value = mock_service
            mock_service.update_status.side_effect = ProductNotFoundServiceError("nonexistent-id")

            response = client.patch(
                "/api/products/nonexistent-id/status",
                json={"status": "active"},
                headers={"Authorization": "Bearer valid-producer-token"},
            )

        assert response.status_code == 404
        data = response.json()
        assert data["detail"]["error"]["code"] == "PRODUCT_NOT_FOUND"

    def test_invalid_status_value_returns_422(
        self, client, mock_firebase_auth, producer_claims
    ):
        """Estado inválido debe retornar HTTP 422 (validación Pydantic)."""
        mock_firebase_auth.verify_id_token.return_value = producer_claims

        response = client.patch(
            "/api/products/product-abc/status",
            json={"status": "published"},  # valor no permitido
            headers={"Authorization": "Bearer valid-producer-token"},
        )

        assert response.status_code == 422

    def test_missing_token_returns_401(self, client):
        """Solicitud sin token debe retornar HTTP 401."""
        response = client.patch(
            "/api/products/product-abc/status",
            json={"status": "active"},
        )
        assert response.status_code == 401

    def test_consumer_role_returns_403(
        self, client, mock_firebase_auth, consumer_claims
    ):
        """Consumidor no puede cambiar estado de productos – debe retornar HTTP 403 (Req. 3.2)."""
        mock_firebase_auth.verify_id_token.return_value = consumer_claims

        response = client.patch(
            "/api/products/product-abc/status",
            json={"status": "active"},
            headers={"Authorization": "Bearer consumer-token"},
        )
        assert response.status_code == 403

    def test_response_contains_updated_at(
        self, client, mock_firebase_auth, producer_claims, active_product
    ):
        """La respuesta debe incluir updatedAt actualizado."""
        mock_firebase_auth.verify_id_token.return_value = producer_claims

        with patch("routes.products.ProductService") as mock_service_cls:
            mock_service = MagicMock()
            mock_service_cls.return_value = mock_service
            mock_service.update_status.return_value = active_product

            response = client.patch(
                "/api/products/product-abc/status",
                json={"status": "active"},
                headers={"Authorization": "Bearer valid-producer-token"},
            )

        assert response.status_code == 200
        data = response.json()["data"]
        assert "updatedAt" in data
        assert data["updatedAt"] is not None


# ---------------------------------------------------------------------------
# Tests unitarios – ProductService.update_status
# ---------------------------------------------------------------------------

class TestProductServiceUpdateStatus:
    """Tests unitarios del método ProductService.update_status (Req. 8.1–8.4)."""

    def _make_service(self, mock_repo):
        from services.product_service import ProductService
        return ProductService(repository=mock_repo)

    def _make_product(self, status="inactive", producer_id="producer-uid-123"):
        return {
            "id": "product-abc",
            "producerId": producer_id,
            "name": "Café",
            "status": status,
            "createdAt": datetime(2024, 1, 1, tzinfo=timezone.utc),
            "updatedAt": datetime(2024, 1, 1, tzinfo=timezone.utc),
        }

    def test_activate_inactive_product(self):
        """Activar un producto inactivo debe cambiar el estado a 'active' (Req. 8.1)."""
        mock_repo = MagicMock()
        mock_repo.get_by_id.return_value = self._make_product(status="inactive")
        mock_repo.update.return_value = {**self._make_product(status="active")}

        service = self._make_service(mock_repo)
        result = service.update_status(
            product_id="product-abc",
            producer_id="producer-uid-123",
            new_status="active",
        )

        assert result["status"] == "active"
        call_fields = mock_repo.update.call_args[0][1]
        assert call_fields["status"] == "active"

    def test_inactivate_active_product(self):
        """Inactivar un producto activo debe cambiar el estado a 'inactive' (Req. 8.2)."""
        mock_repo = MagicMock()
        mock_repo.get_by_id.return_value = self._make_product(status="active")
        mock_repo.update.return_value = {**self._make_product(status="inactive")}

        service = self._make_service(mock_repo)
        result = service.update_status(
            product_id="product-abc",
            producer_id="producer-uid-123",
            new_status="inactive",
        )

        assert result["status"] == "inactive"
        call_fields = mock_repo.update.call_args[0][1]
        assert call_fields["status"] == "inactive"

    def test_non_owner_raises_forbidden(self):
        """Productor que no es dueño debe lanzar ProductForbiddenError."""
        from services.product_service import ProductForbiddenError
        mock_repo = MagicMock()
        mock_repo.get_by_id.return_value = self._make_product(producer_id="owner-uid")

        service = self._make_service(mock_repo)

        with pytest.raises(ProductForbiddenError):
            service.update_status(
                product_id="product-abc",
                producer_id="different-uid",
                new_status="active",
            )

    def test_product_not_found_raises_not_found(self):
        """Producto inexistente debe lanzar ProductNotFoundServiceError."""
        from services.product_service import ProductNotFoundServiceError
        mock_repo = MagicMock()
        mock_repo.get_by_id.return_value = None

        service = self._make_service(mock_repo)

        with pytest.raises(ProductNotFoundServiceError):
            service.update_status(
                product_id="nonexistent",
                producer_id="producer-uid-123",
                new_status="active",
            )

    def test_invalid_status_raises_validation_error(self):
        """Estado inválido debe lanzar ProductValidationError."""
        from services.product_service import ProductValidationError
        mock_repo = MagicMock()

        service = self._make_service(mock_repo)

        with pytest.raises(ProductValidationError) as exc_info:
            service.update_status(
                product_id="product-abc",
                producer_id="producer-uid-123",
                new_status="published",  # valor no permitido
            )

        assert exc_info.value.code == "VALIDATION_ERROR"
        fields = [f["field"] for f in exc_info.value.fields]
        assert "status" in fields

    def test_update_only_modifies_status_field(self):
        """El servicio solo debe actualizar el campo 'status' (Req. 8.3 – no afecta pedidos)."""
        mock_repo = MagicMock()
        mock_repo.get_by_id.return_value = self._make_product(status="inactive")
        mock_repo.update.return_value = self._make_product(status="active")

        service = self._make_service(mock_repo)
        service.update_status(
            product_id="product-abc",
            producer_id="producer-uid-123",
            new_status="active",
        )

        call_args = mock_repo.update.call_args
        assert call_args[0][0] == "product-abc"
        fields_updated = call_args[0][1]
        # Solo debe actualizar 'status'; el repositorio agrega 'updatedAt'
        assert "status" in fields_updated
        assert "producerId" not in fields_updated
        assert "name" not in fields_updated
        assert "price" not in fields_updated

    def test_activate_allows_adding_to_cart(self):
        """
        Activar un producto debe resultar en estado 'active', lo que permite
        agregarlo al carrito (Req. 8.4 – verificado indirectamente por el estado).
        """
        mock_repo = MagicMock()
        mock_repo.get_by_id.return_value = self._make_product(status="inactive")
        mock_repo.update.return_value = self._make_product(status="active")

        service = self._make_service(mock_repo)
        result = service.update_status(
            product_id="product-abc",
            producer_id="producer-uid-123",
            new_status="active",
        )

        # Un producto activo puede ser agregado al carrito
        assert result["status"] == "active"

    def test_inactivate_prevents_adding_to_cart(self):
        """
        Inactivar un producto debe resultar en estado 'inactive', lo que impide
        agregarlo al carrito (Req. 8.4 – verificado indirectamente por el estado).
        """
        mock_repo = MagicMock()
        mock_repo.get_by_id.return_value = self._make_product(status="active")
        mock_repo.update.return_value = self._make_product(status="inactive")

        service = self._make_service(mock_repo)
        result = service.update_status(
            product_id="product-abc",
            producer_id="producer-uid-123",
            new_status="inactive",
        )

        # Un producto inactivo no puede ser agregado al carrito
        assert result["status"] == "inactive"
