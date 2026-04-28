"""
test_product_create.py – Tests para el endpoint POST /api/products y la lógica de negocio.

Cubre:
  - Creación exitosa con estado inicial 'inactive' (Req. 5.1, 5.4)
  - Validación de campos obligatorios vacíos (Req. 5.2)
  - Precio no positivo rechazado (Req. 5.3)
  - Registro de createdAt y updatedAt (Req. 5.5)
  - Asociación al producerId del token (Req. 5.1)
  - Acceso sin token – HTTP 401
  - Acceso con rol incorrecto (CONSUMER) – HTTP 403
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
    """Claims de un Productor autenticado."""
    return {
        "uid": "producer-uid-123",
        "email": "producer@example.com",
        "name": "Finca El Paraíso",
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
def created_product():
    """Datos de un producto recién creado."""
    return {
        "id": "new-product-id",
        "producerId": "producer-uid-123",
        "producerName": "Finca El Paraíso",
        "name": "Café Especial",
        "description": "Café de altura con notas frutales",
        "price": 25000.0,
        "status": "inactive",
        "createdAt": datetime(2024, 6, 1, tzinfo=timezone.utc),
        "updatedAt": datetime(2024, 6, 1, tzinfo=timezone.utc),
    }


# ---------------------------------------------------------------------------
# Tests de integración – POST /api/products
# ---------------------------------------------------------------------------

class TestCreateProductEndpoint:
    """Tests del endpoint POST /api/products (Req. 5.1–5.5)."""

    def test_successful_creation_returns_201(
        self, client, mock_firebase_auth, producer_claims, created_product
    ):
        """Creación exitosa debe retornar HTTP 201 con los datos del producto (Req. 5.1)."""
        mock_firebase_auth.verify_id_token.return_value = producer_claims

        with patch("routes.products.ProductService") as mock_service_cls:
            mock_service = MagicMock()
            mock_service_cls.return_value = mock_service
            mock_service.create_product.return_value = created_product

            response = client.post(
                "/api/products",
                json={
                    "name": "Café Especial",
                    "description": "Café de altura con notas frutales",
                    "price": 25000.0,
                },
                headers={"Authorization": "Bearer valid-producer-token"},
            )

        assert response.status_code == 201
        data = response.json()
        assert "message" in data
        assert "data" in data
        assert data["data"]["name"] == "Café Especial"
        assert data["data"]["price"] == 25000.0

    def test_initial_status_is_inactive(
        self, client, mock_firebase_auth, producer_claims, created_product
    ):
        """El estado inicial del producto debe ser 'inactive' (Req. 5.4)."""
        mock_firebase_auth.verify_id_token.return_value = producer_claims

        with patch("routes.products.ProductService") as mock_service_cls:
            mock_service = MagicMock()
            mock_service_cls.return_value = mock_service
            mock_service.create_product.return_value = created_product

            response = client.post(
                "/api/products",
                json={
                    "name": "Café Especial",
                    "description": "Descripción",
                    "price": 25000.0,
                },
                headers={"Authorization": "Bearer valid-producer-token"},
            )

        assert response.status_code == 201
        assert response.json()["data"]["status"] == "inactive"

    def test_response_contains_timestamps(
        self, client, mock_firebase_auth, producer_claims, created_product
    ):
        """La respuesta debe incluir createdAt y updatedAt (Req. 5.5)."""
        mock_firebase_auth.verify_id_token.return_value = producer_claims

        with patch("routes.products.ProductService") as mock_service_cls:
            mock_service = MagicMock()
            mock_service_cls.return_value = mock_service
            mock_service.create_product.return_value = created_product

            response = client.post(
                "/api/products",
                json={
                    "name": "Café Especial",
                    "description": "Descripción",
                    "price": 25000.0,
                },
                headers={"Authorization": "Bearer valid-producer-token"},
            )

        data = response.json()["data"]
        assert "createdAt" in data
        assert "updatedAt" in data
        assert data["createdAt"] is not None
        assert data["updatedAt"] is not None

    def test_product_associated_to_producer(
        self, client, mock_firebase_auth, producer_claims, created_product
    ):
        """El producto debe asociarse al producerId del token (Req. 5.1)."""
        mock_firebase_auth.verify_id_token.return_value = producer_claims

        with patch("routes.products.ProductService") as mock_service_cls:
            mock_service = MagicMock()
            mock_service_cls.return_value = mock_service
            mock_service.create_product.return_value = created_product

            client.post(
                "/api/products",
                json={
                    "name": "Café Especial",
                    "description": "Descripción",
                    "price": 25000.0,
                },
                headers={"Authorization": "Bearer valid-producer-token"},
            )

            call_kwargs = mock_service.create_product.call_args[1]
            assert call_kwargs["producer_id"] == "producer-uid-123"

    def test_missing_token_returns_401(self, client):
        """Solicitud sin token debe retornar HTTP 401."""
        response = client.post(
            "/api/products",
            json={
                "name": "Café",
                "description": "Descripción",
                "price": 10000.0,
            },
        )
        assert response.status_code == 401

    def test_consumer_role_returns_403(self, client, mock_firebase_auth, consumer_claims):
        """Consumidor no puede crear productos – debe retornar HTTP 403 (Req. 3.2)."""
        mock_firebase_auth.verify_id_token.return_value = consumer_claims

        response = client.post(
            "/api/products",
            json={
                "name": "Café",
                "description": "Descripción",
                "price": 10000.0,
            },
            headers={"Authorization": "Bearer consumer-token"},
        )
        assert response.status_code == 403

    def test_empty_name_returns_422(self, client, mock_firebase_auth, producer_claims):
        """Nombre vacío debe retornar HTTP 422 (validación Pydantic) (Req. 5.2)."""
        mock_firebase_auth.verify_id_token.return_value = producer_claims

        response = client.post(
            "/api/products",
            json={
                "name": "",
                "description": "Descripción válida",
                "price": 10000.0,
            },
            headers={"Authorization": "Bearer valid-producer-token"},
        )
        assert response.status_code == 422

    def test_missing_description_returns_422(self, client, mock_firebase_auth, producer_claims):
        """Descripción ausente debe retornar HTTP 422 (Req. 5.2)."""
        mock_firebase_auth.verify_id_token.return_value = producer_claims

        response = client.post(
            "/api/products",
            json={
                "name": "Café válido",
                "price": 10000.0,
            },
            headers={"Authorization": "Bearer valid-producer-token"},
        )
        assert response.status_code == 422

    def test_zero_price_returns_422(self, client, mock_firebase_auth, producer_claims):
        """Precio igual a cero debe retornar HTTP 422 (Req. 5.3)."""
        mock_firebase_auth.verify_id_token.return_value = producer_claims

        response = client.post(
            "/api/products",
            json={
                "name": "Café",
                "description": "Descripción",
                "price": 0,
            },
            headers={"Authorization": "Bearer valid-producer-token"},
        )
        assert response.status_code == 422

    def test_negative_price_returns_422(self, client, mock_firebase_auth, producer_claims):
        """Precio negativo debe retornar HTTP 422 (Req. 5.3)."""
        mock_firebase_auth.verify_id_token.return_value = producer_claims

        response = client.post(
            "/api/products",
            json={
                "name": "Café",
                "description": "Descripción",
                "price": -500.0,
            },
            headers={"Authorization": "Bearer valid-producer-token"},
        )
        assert response.status_code == 422

    def test_missing_name_returns_422(self, client, mock_firebase_auth, producer_claims):
        """Nombre ausente debe retornar HTTP 422 (Req. 5.2)."""
        mock_firebase_auth.verify_id_token.return_value = producer_claims

        response = client.post(
            "/api/products",
            json={
                "description": "Descripción",
                "price": 10000.0,
            },
            headers={"Authorization": "Bearer valid-producer-token"},
        )
        assert response.status_code == 422


# ---------------------------------------------------------------------------
# Tests unitarios – ProductService.create_product
# ---------------------------------------------------------------------------

class TestProductServiceCreateProduct:
    """Tests unitarios del método ProductService.create_product (Req. 5.1–5.5)."""

    def _make_service(self, mock_repo):
        from services.product_service import ProductService
        return ProductService(repository=mock_repo)

    def test_successful_creation_returns_product_data(self):
        """Creación exitosa retorna los datos del producto."""
        mock_repo = MagicMock()
        now = datetime.now(timezone.utc)
        mock_repo.create.return_value = {
            "id": "new-id",
            "producerId": "producer-uid-123",
            "producerName": "Finca El Paraíso",
            "name": "Café Especial",
            "description": "Descripción",
            "price": 25000.0,
            "status": "inactive",
            "createdAt": now,
            "updatedAt": now,
        }

        service = self._make_service(mock_repo)
        result = service.create_product(
            producer_id="producer-uid-123",
            producer_name="Finca El Paraíso",
            name="Café Especial",
            description="Descripción",
            price=25000.0,
        )

        assert result["name"] == "Café Especial"
        assert result["status"] == "inactive"
        assert result["producerId"] == "producer-uid-123"

    def test_initial_status_is_always_inactive(self):
        """El estado inicial debe ser 'inactive' independientemente de la entrada (Req. 5.4)."""
        mock_repo = MagicMock()
        mock_repo.create.return_value = {
            "id": "new-id",
            "status": "inactive",
            "createdAt": datetime.now(timezone.utc),
            "updatedAt": datetime.now(timezone.utc),
        }

        service = self._make_service(mock_repo)
        service.create_product(
            producer_id="producer-uid-123",
            producer_name="Finca",
            name="Café",
            description="Descripción",
            price=10000.0,
        )

        call_fields = mock_repo.create.call_args[0][0]
        assert call_fields["status"] == "inactive"

    def test_product_associated_to_producer_id(self):
        """El producto debe asociarse al producerId del token (Req. 5.1)."""
        mock_repo = MagicMock()
        mock_repo.create.return_value = {
            "id": "new-id",
            "producerId": "producer-uid-123",
            "status": "inactive",
            "createdAt": datetime.now(timezone.utc),
            "updatedAt": datetime.now(timezone.utc),
        }

        service = self._make_service(mock_repo)
        service.create_product(
            producer_id="producer-uid-123",
            producer_name="Finca",
            name="Café",
            description="Descripción",
            price=10000.0,
        )

        call_fields = mock_repo.create.call_args[0][0]
        assert call_fields["producerId"] == "producer-uid-123"

    def test_empty_name_raises_validation_error(self):
        """Nombre vacío debe lanzar ProductValidationError (Req. 5.2)."""
        from services.product_service import ProductValidationError
        mock_repo = MagicMock()
        service = self._make_service(mock_repo)

        with pytest.raises(ProductValidationError) as exc_info:
            service.create_product(
                producer_id="producer-uid-123",
                producer_name="Finca",
                name="",
                description="Descripción",
                price=10000.0,
            )

        fields = [f["field"] for f in exc_info.value.fields]
        assert "name" in fields

    def test_empty_description_raises_validation_error(self):
        """Descripción vacía debe lanzar ProductValidationError (Req. 5.2)."""
        from services.product_service import ProductValidationError
        mock_repo = MagicMock()
        service = self._make_service(mock_repo)

        with pytest.raises(ProductValidationError) as exc_info:
            service.create_product(
                producer_id="producer-uid-123",
                producer_name="Finca",
                name="Café",
                description="",
                price=10000.0,
            )

        fields = [f["field"] for f in exc_info.value.fields]
        assert "description" in fields

    def test_zero_price_raises_validation_error(self):
        """Precio igual a cero debe lanzar ProductValidationError (Req. 5.3)."""
        from services.product_service import ProductValidationError
        mock_repo = MagicMock()
        service = self._make_service(mock_repo)

        with pytest.raises(ProductValidationError) as exc_info:
            service.create_product(
                producer_id="producer-uid-123",
                producer_name="Finca",
                name="Café",
                description="Descripción",
                price=0,
            )

        fields = [f["field"] for f in exc_info.value.fields]
        assert "price" in fields

    def test_negative_price_raises_validation_error(self):
        """Precio negativo debe lanzar ProductValidationError (Req. 5.3)."""
        from services.product_service import ProductValidationError
        mock_repo = MagicMock()
        service = self._make_service(mock_repo)

        with pytest.raises(ProductValidationError) as exc_info:
            service.create_product(
                producer_id="producer-uid-123",
                producer_name="Finca",
                name="Café",
                description="Descripción",
                price=-100.0,
            )

        fields = [f["field"] for f in exc_info.value.fields]
        assert "price" in fields

    def test_multiple_invalid_fields_all_reported(self):
        """Múltiples campos inválidos deben reportarse todos (Req. 5.2)."""
        from services.product_service import ProductValidationError
        mock_repo = MagicMock()
        service = self._make_service(mock_repo)

        with pytest.raises(ProductValidationError) as exc_info:
            service.create_product(
                producer_id="producer-uid-123",
                producer_name="Finca",
                name="",
                description="",
                price=0,
            )

        fields = [f["field"] for f in exc_info.value.fields]
        assert "name" in fields
        assert "description" in fields
        assert "price" in fields

    def test_name_is_stripped(self):
        """El nombre debe ser guardado sin espacios extra."""
        mock_repo = MagicMock()
        mock_repo.create.return_value = {
            "id": "new-id",
            "status": "inactive",
            "createdAt": datetime.now(timezone.utc),
            "updatedAt": datetime.now(timezone.utc),
        }

        service = self._make_service(mock_repo)
        service.create_product(
            producer_id="producer-uid-123",
            producer_name="Finca",
            name="  Café Especial  ",
            description="  Descripción  ",
            price=10000.0,
        )

        call_fields = mock_repo.create.call_args[0][0]
        assert call_fields["name"] == "Café Especial"
        assert call_fields["description"] == "Descripción"
