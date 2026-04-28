"""
test_product_update.py – Tests para el endpoint PUT /api/products/:id y la lógica de negocio.

Cubre:
  - Actualización exitosa (Req. 6.1)
  - Validación de campos obligatorios vacíos (Req. 6.2)
  - Verificación de propiedad – HTTP 403 si no es dueño (Req. 6.3)
  - Registro de updatedAt (Req. 6.4)
  - Producto no encontrado – HTTP 404
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
def producer_token_claims():
    """Claims de un Productor autenticado."""
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
def consumer_token_claims():
    """Claims de un Consumidor autenticado."""
    return {
        "uid": "consumer-uid-789",
        "email": "consumer@example.com",
        "role": "CONSUMER",
    }


@pytest.fixture
def existing_product():
    """Datos de un producto existente en Firestore."""
    return {
        "id": "product-abc",
        "producerId": "producer-uid-123",
        "producerName": "Finca El Paraíso",
        "name": "Café Especial",
        "description": "Café de altura con notas frutales",
        "price": 25000.0,
        "status": "active",
        "createdAt": datetime(2024, 1, 1, tzinfo=timezone.utc),
        "updatedAt": datetime(2024, 1, 1, tzinfo=timezone.utc),
    }


@pytest.fixture
def updated_product(existing_product):
    """Datos del producto después de la actualización."""
    return {
        **existing_product,
        "name": "Café Especial Premium",
        "description": "Café de altura con notas frutales y chocolate",
        "price": 30000.0,
        "updatedAt": datetime(2024, 6, 15, tzinfo=timezone.utc),
    }


# ---------------------------------------------------------------------------
# Tests de integración – PUT /api/products/:id
# ---------------------------------------------------------------------------

class TestUpdateProductEndpoint:
    """Tests del endpoint PUT /api/products/:id (Req. 6.1, 6.2, 6.3, 6.4)."""

    def test_successful_update_returns_200(
        self, client, mock_firebase_auth, producer_token_claims, existing_product, updated_product
    ):
        """Actualización exitosa debe retornar HTTP 200 con los datos actualizados (Req. 6.1)."""
        mock_firebase_auth.verify_id_token.return_value = producer_token_claims

        with patch("routes.products.ProductService") as mock_service_cls:
            mock_service = MagicMock()
            mock_service_cls.return_value = mock_service
            mock_service.update_product.return_value = updated_product

            response = client.put(
                "/api/products/product-abc",
                json={
                    "name": "Café Especial Premium",
                    "description": "Café de altura con notas frutales y chocolate",
                    "price": 30000.0,
                },
                headers={"Authorization": "Bearer valid-producer-token"},
            )

        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "data" in data
        assert data["data"]["name"] == "Café Especial Premium"
        assert data["data"]["price"] == 30000.0

    def test_update_calls_service_with_correct_args(
        self, client, mock_firebase_auth, producer_token_claims, updated_product
    ):
        """El endpoint debe llamar al servicio con los argumentos correctos."""
        mock_firebase_auth.verify_id_token.return_value = producer_token_claims

        with patch("routes.products.ProductService") as mock_service_cls:
            mock_service = MagicMock()
            mock_service_cls.return_value = mock_service
            mock_service.update_product.return_value = updated_product

            client.put(
                "/api/products/product-abc",
                json={
                    "name": "Nuevo Nombre",
                    "description": "Nueva descripción",
                    "price": 15000.0,
                },
                headers={"Authorization": "Bearer valid-producer-token"},
            )

            mock_service.update_product.assert_called_once_with(
                product_id="product-abc",
                producer_id="producer-uid-123",
                name="Nuevo Nombre",
                description="Nueva descripción",
                price=15000.0,
            )

    def test_missing_token_returns_401(self, client):
        """Solicitud sin token debe retornar HTTP 401 (Req. 3.4)."""
        response = client.put(
            "/api/products/product-abc",
            json={
                "name": "Café",
                "description": "Descripción",
                "price": 10000.0,
            },
        )
        assert response.status_code == 401

    def test_consumer_role_returns_403(self, client, mock_firebase_auth, consumer_token_claims):
        """Consumidor no puede actualizar productos – debe retornar HTTP 403 (Req. 3.2)."""
        mock_firebase_auth.verify_id_token.return_value = consumer_token_claims

        response = client.put(
            "/api/products/product-abc",
            json={
                "name": "Café",
                "description": "Descripción",
                "price": 10000.0,
            },
            headers={"Authorization": "Bearer consumer-token"},
        )
        assert response.status_code == 403

    def test_non_owner_producer_returns_403(
        self, client, mock_firebase_auth, other_producer_claims
    ):
        """Productor que no es dueño debe recibir HTTP 403 (Req. 6.3)."""
        mock_firebase_auth.verify_id_token.return_value = other_producer_claims

        with patch("routes.products.ProductService") as mock_service_cls:
            from services.product_service import ProductForbiddenError
            mock_service = MagicMock()
            mock_service_cls.return_value = mock_service
            mock_service.update_product.side_effect = ProductForbiddenError()

            response = client.put(
                "/api/products/product-abc",
                json={
                    "name": "Café",
                    "description": "Descripción",
                    "price": 10000.0,
                },
                headers={"Authorization": "Bearer other-producer-token"},
            )

        assert response.status_code == 403
        data = response.json()
        assert data["detail"]["error"]["code"] == "FORBIDDEN"

    def test_product_not_found_returns_404(
        self, client, mock_firebase_auth, producer_token_claims
    ):
        """Producto inexistente debe retornar HTTP 404."""
        mock_firebase_auth.verify_id_token.return_value = producer_token_claims

        with patch("routes.products.ProductService") as mock_service_cls:
            from services.product_service import ProductNotFoundServiceError
            mock_service = MagicMock()
            mock_service_cls.return_value = mock_service
            mock_service.update_product.side_effect = ProductNotFoundServiceError("nonexistent-id")

            response = client.put(
                "/api/products/nonexistent-id",
                json={
                    "name": "Café",
                    "description": "Descripción",
                    "price": 10000.0,
                },
                headers={"Authorization": "Bearer valid-producer-token"},
            )

        assert response.status_code == 404
        data = response.json()
        assert data["detail"]["error"]["code"] == "PRODUCT_NOT_FOUND"

    def test_empty_name_returns_422(self, client, mock_firebase_auth, producer_token_claims):
        """Nombre vacío debe retornar HTTP 422 (validación Pydantic) (Req. 6.2)."""
        mock_firebase_auth.verify_id_token.return_value = producer_token_claims

        response = client.put(
            "/api/products/product-abc",
            json={
                "name": "",
                "description": "Descripción válida",
                "price": 10000.0,
            },
            headers={"Authorization": "Bearer valid-producer-token"},
        )
        assert response.status_code == 422

    def test_missing_description_returns_422(
        self, client, mock_firebase_auth, producer_token_claims
    ):
        """Descripción ausente debe retornar HTTP 422 (Req. 6.2)."""
        mock_firebase_auth.verify_id_token.return_value = producer_token_claims

        response = client.put(
            "/api/products/product-abc",
            json={
                "name": "Café válido",
                "price": 10000.0,
            },
            headers={"Authorization": "Bearer valid-producer-token"},
        )
        assert response.status_code == 422

    def test_zero_price_returns_422(self, client, mock_firebase_auth, producer_token_claims):
        """Precio igual a cero debe retornar HTTP 422 (Req. 6.2)."""
        mock_firebase_auth.verify_id_token.return_value = producer_token_claims

        response = client.put(
            "/api/products/product-abc",
            json={
                "name": "Café",
                "description": "Descripción",
                "price": 0,
            },
            headers={"Authorization": "Bearer valid-producer-token"},
        )
        assert response.status_code == 422

    def test_negative_price_returns_422(self, client, mock_firebase_auth, producer_token_claims):
        """Precio negativo debe retornar HTTP 422 (Req. 6.2)."""
        mock_firebase_auth.verify_id_token.return_value = producer_token_claims

        response = client.put(
            "/api/products/product-abc",
            json={
                "name": "Café",
                "description": "Descripción",
                "price": -100.0,
            },
            headers={"Authorization": "Bearer valid-producer-token"},
        )
        assert response.status_code == 422

    def test_missing_price_returns_422(self, client, mock_firebase_auth, producer_token_claims):
        """Precio ausente debe retornar HTTP 422 (Req. 6.2)."""
        mock_firebase_auth.verify_id_token.return_value = producer_token_claims

        response = client.put(
            "/api/products/product-abc",
            json={
                "name": "Café",
                "description": "Descripción",
            },
            headers={"Authorization": "Bearer valid-producer-token"},
        )
        assert response.status_code == 422

    def test_response_contains_updated_at(
        self, client, mock_firebase_auth, producer_token_claims, updated_product
    ):
        """La respuesta debe incluir updatedAt (Req. 6.4)."""
        mock_firebase_auth.verify_id_token.return_value = producer_token_claims

        with patch("routes.products.ProductService") as mock_service_cls:
            mock_service = MagicMock()
            mock_service_cls.return_value = mock_service
            mock_service.update_product.return_value = updated_product

            response = client.put(
                "/api/products/product-abc",
                json={
                    "name": "Café Especial Premium",
                    "description": "Descripción actualizada",
                    "price": 30000.0,
                },
                headers={"Authorization": "Bearer valid-producer-token"},
            )

        assert response.status_code == 200
        data = response.json()["data"]
        assert "updatedAt" in data
        assert data["updatedAt"] is not None


# ---------------------------------------------------------------------------
# Tests unitarios – ProductService.update_product
# ---------------------------------------------------------------------------

class TestProductServiceUpdateProduct:
    """Tests unitarios del método ProductService.update_product."""

    def _make_service(self, mock_repo):
        from services.product_service import ProductService
        return ProductService(repository=mock_repo)

    def test_successful_update_returns_updated_data(self, existing_product, updated_product):
        """Actualización exitosa retorna los datos actualizados."""
        mock_repo = MagicMock()
        mock_repo.get_by_id.return_value = existing_product
        mock_repo.update.return_value = updated_product

        service = self._make_service(mock_repo)
        result = service.update_product(
            product_id="product-abc",
            producer_id="producer-uid-123",
            name="Café Especial Premium",
            description="Café de altura con notas frutales y chocolate",
            price=30000.0,
        )

        assert result["name"] == "Café Especial Premium"
        assert result["price"] == 30000.0

    def test_update_calls_repo_with_correct_fields(self, existing_product, updated_product):
        """El servicio debe llamar al repositorio con los campos correctos."""
        mock_repo = MagicMock()
        mock_repo.get_by_id.return_value = existing_product
        mock_repo.update.return_value = updated_product

        service = self._make_service(mock_repo)
        service.update_product(
            product_id="product-abc",
            producer_id="producer-uid-123",
            name="  Café Especial Premium  ",  # con espacios para probar strip
            description="  Descripción  ",
            price=30000.0,
        )

        call_args = mock_repo.update.call_args
        assert call_args[0][0] == "product-abc"
        fields = call_args[0][1]
        assert fields["name"] == "Café Especial Premium"
        assert fields["description"] == "Descripción"
        assert fields["price"] == 30000.0

    def test_non_owner_raises_forbidden(self, existing_product):
        """Productor que no es dueño debe lanzar ProductForbiddenError (Req. 6.3)."""
        from services.product_service import ProductForbiddenError
        mock_repo = MagicMock()
        mock_repo.get_by_id.return_value = existing_product

        service = self._make_service(mock_repo)

        with pytest.raises(ProductForbiddenError):
            service.update_product(
                product_id="product-abc",
                producer_id="different-producer-uid",
                name="Café",
                description="Descripción",
                price=10000.0,
            )

    def test_product_not_found_raises_not_found(self):
        """Producto inexistente debe lanzar ProductNotFoundServiceError."""
        from services.product_service import ProductNotFoundServiceError
        mock_repo = MagicMock()
        mock_repo.get_by_id.return_value = None

        service = self._make_service(mock_repo)

        with pytest.raises(ProductNotFoundServiceError):
            service.update_product(
                product_id="nonexistent",
                producer_id="producer-uid-123",
                name="Café",
                description="Descripción",
                price=10000.0,
            )

    def test_empty_name_raises_validation_error(self, existing_product):
        """Nombre vacío debe lanzar ProductValidationError (Req. 6.2)."""
        from services.product_service import ProductValidationError
        mock_repo = MagicMock()
        mock_repo.get_by_id.return_value = existing_product

        service = self._make_service(mock_repo)

        with pytest.raises(ProductValidationError) as exc_info:
            service.update_product(
                product_id="product-abc",
                producer_id="producer-uid-123",
                name="",
                description="Descripción",
                price=10000.0,
            )

        fields = [f["field"] for f in exc_info.value.fields]
        assert "name" in fields

    def test_empty_description_raises_validation_error(self, existing_product):
        """Descripción vacía debe lanzar ProductValidationError (Req. 6.2)."""
        from services.product_service import ProductValidationError
        mock_repo = MagicMock()
        mock_repo.get_by_id.return_value = existing_product

        service = self._make_service(mock_repo)

        with pytest.raises(ProductValidationError) as exc_info:
            service.update_product(
                product_id="product-abc",
                producer_id="producer-uid-123",
                name="Café",
                description="",
                price=10000.0,
            )

        fields = [f["field"] for f in exc_info.value.fields]
        assert "description" in fields

    def test_zero_price_raises_validation_error(self, existing_product):
        """Precio igual a cero debe lanzar ProductValidationError (Req. 6.2)."""
        from services.product_service import ProductValidationError
        mock_repo = MagicMock()
        mock_repo.get_by_id.return_value = existing_product

        service = self._make_service(mock_repo)

        with pytest.raises(ProductValidationError) as exc_info:
            service.update_product(
                product_id="product-abc",
                producer_id="producer-uid-123",
                name="Café",
                description="Descripción",
                price=0,
            )

        fields = [f["field"] for f in exc_info.value.fields]
        assert "price" in fields

    def test_negative_price_raises_validation_error(self, existing_product):
        """Precio negativo debe lanzar ProductValidationError (Req. 6.2)."""
        from services.product_service import ProductValidationError
        mock_repo = MagicMock()
        mock_repo.get_by_id.return_value = existing_product

        service = self._make_service(mock_repo)

        with pytest.raises(ProductValidationError) as exc_info:
            service.update_product(
                product_id="product-abc",
                producer_id="producer-uid-123",
                name="Café",
                description="Descripción",
                price=-50.0,
            )

        fields = [f["field"] for f in exc_info.value.fields]
        assert "price" in fields

    def test_multiple_invalid_fields_reported(self, existing_product):
        """Múltiples campos inválidos deben reportarse todos (Req. 6.2)."""
        from services.product_service import ProductValidationError
        mock_repo = MagicMock()
        mock_repo.get_by_id.return_value = existing_product

        service = self._make_service(mock_repo)

        with pytest.raises(ProductValidationError) as exc_info:
            service.update_product(
                product_id="product-abc",
                producer_id="producer-uid-123",
                name="",
                description="",
                price=0,
            )

        fields = [f["field"] for f in exc_info.value.fields]
        assert "name" in fields
        assert "description" in fields
        assert "price" in fields

    def test_updated_at_is_set_by_repository(self, existing_product):
        """El repositorio debe registrar updatedAt (Req. 6.4)."""
        mock_repo = MagicMock()
        mock_repo.get_by_id.return_value = existing_product

        updated = {**existing_product, "updatedAt": datetime.now(timezone.utc)}
        mock_repo.update.return_value = updated

        service = self._make_service(mock_repo)
        result = service.update_product(
            product_id="product-abc",
            producer_id="producer-uid-123",
            name="Café",
            description="Descripción",
            price=10000.0,
        )

        assert result["updatedAt"] is not None
        # updatedAt debe ser posterior o igual a createdAt
        assert result["updatedAt"] >= existing_product["createdAt"]


# ---------------------------------------------------------------------------
# Tests unitarios – ProductRepository
# ---------------------------------------------------------------------------

class TestProductRepository:
    """Tests unitarios del ProductRepository."""

    def test_get_by_id_returns_none_when_not_found(self):
        """get_by_id debe retornar None si el documento no existe."""
        from repositories.product_repository import ProductRepository

        mock_db = MagicMock()
        mock_doc = MagicMock()
        mock_doc.exists = False
        mock_db.collection.return_value.document.return_value.get.return_value = mock_doc

        repo = ProductRepository.__new__(ProductRepository)
        repo._db = mock_db

        result = repo.get_by_id("nonexistent-id")
        assert result is None

    def test_get_by_id_returns_data_with_id(self):
        """get_by_id debe retornar el documento con el campo 'id' incluido."""
        from repositories.product_repository import ProductRepository

        mock_db = MagicMock()
        mock_doc = MagicMock()
        mock_doc.exists = True
        mock_doc.id = "product-abc"
        mock_doc.to_dict.return_value = {
            "name": "Café",
            "producerId": "producer-uid-123",
            "price": 25000.0,
        }
        mock_db.collection.return_value.document.return_value.get.return_value = mock_doc

        repo = ProductRepository.__new__(ProductRepository)
        repo._db = mock_db

        result = repo.get_by_id("product-abc")
        assert result is not None
        assert result["id"] == "product-abc"
        assert result["name"] == "Café"

    def test_update_sets_updated_at(self):
        """update debe incluir updatedAt en los campos actualizados (Req. 6.4)."""
        from repositories.product_repository import ProductRepository

        mock_db = MagicMock()
        mock_doc_ref = MagicMock()
        mock_existing_doc = MagicMock()
        mock_existing_doc.exists = True

        mock_updated_doc = MagicMock()
        mock_updated_doc.id = "product-abc"
        mock_updated_doc.to_dict.return_value = {
            "name": "Café Actualizado",
            "price": 30000.0,
            "updatedAt": datetime.now(timezone.utc),
        }

        mock_doc_ref.get.side_effect = [mock_existing_doc, mock_updated_doc]
        mock_db.collection.return_value.document.return_value = mock_doc_ref

        repo = ProductRepository.__new__(ProductRepository)
        repo._db = mock_db

        fields = {"name": "Café Actualizado", "price": 30000.0}
        result = repo.update("product-abc", fields)

        # Verificar que update fue llamado con updatedAt
        call_args = mock_doc_ref.update.call_args[0][0]
        assert "updatedAt" in call_args
        assert isinstance(call_args["updatedAt"], datetime)

    def test_update_raises_not_found_when_doc_missing(self):
        """update debe lanzar ProductNotFoundError si el documento no existe."""
        from repositories.product_repository import ProductRepository, ProductNotFoundError

        mock_db = MagicMock()
        mock_doc_ref = MagicMock()
        mock_existing_doc = MagicMock()
        mock_existing_doc.exists = False

        mock_doc_ref.get.return_value = mock_existing_doc
        mock_db.collection.return_value.document.return_value = mock_doc_ref

        repo = ProductRepository.__new__(ProductRepository)
        repo._db = mock_db

        with pytest.raises(ProductNotFoundError):
            repo.update("nonexistent-id", {"name": "Café"})
