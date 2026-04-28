"""
test_addresses.py – Tests para los endpoints de direcciones de envío.

Cubre:
  - GET    /api/addresses       (Req. 18.4)
  - POST   /api/addresses       (Req. 18.1, 18.2, 18.3)
  - DELETE /api/addresses/:id

Tests unitarios del AddressService:
  - Listado de direcciones
  - Creación con validación de campos obligatorios (Req. 18.2)
  - Límite de 5 direcciones por usuario (Req. 18.3)
  - Eliminación de dirección
"""

from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from main import app


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_NOW = datetime(2024, 6, 1, 12, 0, 0, tzinfo=timezone.utc)
_NOW_ISO = _NOW.isoformat()


def _make_address(
    address_id="addr-1",
    user_id="user-123",
    street="Calle 10 # 5-20",
    city="Bogotá",
    department="Cundinamarca",
    postal_code="110111",
):
    return {
        "id": address_id,
        "user_id": user_id,
        "street": street,
        "city": city,
        "department": department,
        "postal_code": postal_code,
        "created_at": _NOW_ISO,
    }


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def client():
    return TestClient(app, raise_server_exceptions=False)


@pytest.fixture
def consumer_token_headers(mock_firebase_auth):
    """Simula un token válido de consumidor."""
    mock_firebase_auth.verify_id_token.return_value = {
        "uid": "user-123",
        "email": "consumer@test.com",
        "role": "CONSUMER",
    }
    return {"Authorization": "Bearer valid-consumer-token"}


@pytest.fixture
def producer_token_headers(mock_firebase_auth):
    """Simula un token válido de productor."""
    mock_firebase_auth.verify_id_token.return_value = {
        "uid": "producer-456",
        "email": "producer@test.com",
        "role": "PRODUCER",
    }
    return {"Authorization": "Bearer valid-producer-token"}


# ---------------------------------------------------------------------------
# Tests – GET /api/addresses
# ---------------------------------------------------------------------------


class TestListAddresses:

    def test_returns_empty_list_when_no_addresses(self, client, consumer_token_headers):
        with patch("routes.addresses.AddressService") as mock_cls:
            mock_svc = MagicMock()
            mock_cls.return_value = mock_svc
            mock_svc.list_addresses.return_value = []

            response = client.get("/api/addresses", headers=consumer_token_headers)

        assert response.status_code == 200
        body = response.json()
        assert "data" in body
        assert body["data"] == []

    def test_returns_list_of_addresses(self, client, consumer_token_headers):
        addresses = [_make_address("addr-1"), _make_address("addr-2")]

        with patch("routes.addresses.AddressService") as mock_cls:
            mock_svc = MagicMock()
            mock_cls.return_value = mock_svc
            mock_svc.list_addresses.return_value = addresses

            response = client.get("/api/addresses", headers=consumer_token_headers)

        assert response.status_code == 200
        data = response.json()["data"]
        assert len(data) == 2
        assert data[0]["id"] == "addr-1"
        assert data[1]["id"] == "addr-2"

    def test_requires_authentication(self, client):
        response = client.get("/api/addresses")
        assert response.status_code == 401

    def test_requires_consumer_role(self, client, producer_token_headers):
        response = client.get("/api/addresses", headers=producer_token_headers)
        assert response.status_code == 403

    def test_service_called_with_user_id(self, client, consumer_token_headers):
        with patch("routes.addresses.AddressService") as mock_cls:
            mock_svc = MagicMock()
            mock_cls.return_value = mock_svc
            mock_svc.list_addresses.return_value = []

            client.get("/api/addresses", headers=consumer_token_headers)

        mock_svc.list_addresses.assert_called_once_with("user-123")


# ---------------------------------------------------------------------------
# Tests – POST /api/addresses
# ---------------------------------------------------------------------------


class TestCreateAddress:

    def test_creates_address_with_all_fields(self, client, consumer_token_headers):
        address = _make_address()

        with patch("routes.addresses.AddressService") as mock_cls:
            mock_svc = MagicMock()
            mock_cls.return_value = mock_svc
            mock_svc.create_address.return_value = address

            response = client.post(
                "/api/addresses",
                json={
                    "street": "Calle 10 # 5-20",
                    "city": "Bogotá",
                    "department": "Cundinamarca",
                    "postal_code": "110111",
                },
                headers=consumer_token_headers,
            )

        assert response.status_code == 201
        body = response.json()
        assert "message" in body
        assert "data" in body
        assert body["data"]["street"] == "Calle 10 # 5-20"
        assert body["data"]["city"] == "Bogotá"
        assert body["data"]["department"] == "Cundinamarca"

    def test_creates_address_without_postal_code(self, client, consumer_token_headers):
        address = _make_address(postal_code=None)

        with patch("routes.addresses.AddressService") as mock_cls:
            mock_svc = MagicMock()
            mock_cls.return_value = mock_svc
            mock_svc.create_address.return_value = address

            response = client.post(
                "/api/addresses",
                json={
                    "street": "Calle 10 # 5-20",
                    "city": "Bogotá",
                    "department": "Cundinamarca",
                },
                headers=consumer_token_headers,
            )

        assert response.status_code == 201

    def test_returns_400_when_limit_exceeded(self, client, consumer_token_headers):
        """Retorna HTTP 400 cuando el usuario ya tiene 5 direcciones (Req. 18.3)."""
        from services.address_service import AddressLimitExceededError

        with patch("routes.addresses.AddressService") as mock_cls:
            mock_svc = MagicMock()
            mock_cls.return_value = mock_svc
            mock_svc.create_address.side_effect = AddressLimitExceededError()

            response = client.post(
                "/api/addresses",
                json={
                    "street": "Calle 10 # 5-20",
                    "city": "Bogotá",
                    "department": "Cundinamarca",
                },
                headers=consumer_token_headers,
            )

        assert response.status_code == 400
        error = response.json()["detail"]["error"]
        assert error["code"] == "ADDRESS_LIMIT_EXCEEDED"

    def test_returns_422_when_street_missing(self, client, consumer_token_headers):
        """Retorna HTTP 422 cuando falta el campo street (Req. 18.2)."""
        response = client.post(
            "/api/addresses",
            json={"city": "Bogotá", "department": "Cundinamarca"},
            headers=consumer_token_headers,
        )
        assert response.status_code == 422

    def test_returns_422_when_city_missing(self, client, consumer_token_headers):
        """Retorna HTTP 422 cuando falta el campo city (Req. 18.2)."""
        response = client.post(
            "/api/addresses",
            json={"street": "Calle 10", "department": "Cundinamarca"},
            headers=consumer_token_headers,
        )
        assert response.status_code == 422

    def test_returns_422_when_department_missing(self, client, consumer_token_headers):
        """Retorna HTTP 422 cuando falta el campo department (Req. 18.2)."""
        response = client.post(
            "/api/addresses",
            json={"street": "Calle 10", "city": "Bogotá"},
            headers=consumer_token_headers,
        )
        assert response.status_code == 422

    def test_returns_422_when_street_empty(self, client, consumer_token_headers):
        """Retorna HTTP 422 cuando street es cadena vacía (Req. 18.2)."""
        response = client.post(
            "/api/addresses",
            json={"street": "", "city": "Bogotá", "department": "Cundinamarca"},
            headers=consumer_token_headers,
        )
        assert response.status_code == 422

    def test_returns_422_when_city_empty(self, client, consumer_token_headers):
        """Retorna HTTP 422 cuando city es cadena vacía (Req. 18.2)."""
        response = client.post(
            "/api/addresses",
            json={"street": "Calle 10", "city": "", "department": "Cundinamarca"},
            headers=consumer_token_headers,
        )
        assert response.status_code == 422

    def test_returns_422_when_department_empty(self, client, consumer_token_headers):
        """Retorna HTTP 422 cuando department es cadena vacía (Req. 18.2)."""
        response = client.post(
            "/api/addresses",
            json={"street": "Calle 10", "city": "Bogotá", "department": ""},
            headers=consumer_token_headers,
        )
        assert response.status_code == 422

    def test_requires_authentication(self, client):
        response = client.post(
            "/api/addresses",
            json={"street": "Calle 10", "city": "Bogotá", "department": "Cundinamarca"},
        )
        assert response.status_code == 401

    def test_requires_consumer_role(self, client, producer_token_headers):
        response = client.post(
            "/api/addresses",
            json={"street": "Calle 10", "city": "Bogotá", "department": "Cundinamarca"},
            headers=producer_token_headers,
        )
        assert response.status_code == 403

    def test_service_called_with_correct_params(self, client, consumer_token_headers):
        address = _make_address()

        with patch("routes.addresses.AddressService") as mock_cls:
            mock_svc = MagicMock()
            mock_cls.return_value = mock_svc
            mock_svc.create_address.return_value = address

            client.post(
                "/api/addresses",
                json={
                    "street": "Calle 10 # 5-20",
                    "city": "Bogotá",
                    "department": "Cundinamarca",
                    "postal_code": "110111",
                },
                headers=consumer_token_headers,
            )

        mock_svc.create_address.assert_called_once_with(
            user_id="user-123",
            street="Calle 10 # 5-20",
            city="Bogotá",
            department="Cundinamarca",
            postal_code="110111",
        )


# ---------------------------------------------------------------------------
# Tests – DELETE /api/addresses/:id
# ---------------------------------------------------------------------------


class TestDeleteAddress:

    def test_deletes_address_successfully(self, client, consumer_token_headers):
        with patch("routes.addresses.AddressService") as mock_cls:
            mock_svc = MagicMock()
            mock_cls.return_value = mock_svc
            mock_svc.delete_address.return_value = None

            response = client.delete(
                "/api/addresses/addr-1",
                headers=consumer_token_headers,
            )

        assert response.status_code == 200
        body = response.json()
        assert "message" in body

    def test_returns_404_for_nonexistent_address(self, client, consumer_token_headers):
        from services.address_service import AddressNotFoundServiceError

        with patch("routes.addresses.AddressService") as mock_cls:
            mock_svc = MagicMock()
            mock_cls.return_value = mock_svc
            mock_svc.delete_address.side_effect = AddressNotFoundServiceError("nonexistent")

            response = client.delete(
                "/api/addresses/nonexistent",
                headers=consumer_token_headers,
            )

        assert response.status_code == 404
        error = response.json()["detail"]["error"]
        assert error["code"] == "ADDRESS_NOT_FOUND"

    def test_returns_404_for_address_belonging_to_other_user(self, client, consumer_token_headers):
        """No puede eliminar una dirección de otro usuario (retorna 404)."""
        from services.address_service import AddressNotFoundServiceError

        with patch("routes.addresses.AddressService") as mock_cls:
            mock_svc = MagicMock()
            mock_cls.return_value = mock_svc
            mock_svc.delete_address.side_effect = AddressNotFoundServiceError("addr-other")

            response = client.delete(
                "/api/addresses/addr-other",
                headers=consumer_token_headers,
            )

        assert response.status_code == 404

    def test_requires_authentication(self, client):
        response = client.delete("/api/addresses/addr-1")
        assert response.status_code == 401

    def test_requires_consumer_role(self, client, producer_token_headers):
        response = client.delete("/api/addresses/addr-1", headers=producer_token_headers)
        assert response.status_code == 403

    def test_service_called_with_correct_params(self, client, consumer_token_headers):
        with patch("routes.addresses.AddressService") as mock_cls:
            mock_svc = MagicMock()
            mock_cls.return_value = mock_svc
            mock_svc.delete_address.return_value = None

            client.delete("/api/addresses/addr-1", headers=consumer_token_headers)

        mock_svc.delete_address.assert_called_once_with(
            user_id="user-123",
            address_id="addr-1",
        )


# ---------------------------------------------------------------------------
# Tests unitarios – AddressService (lógica de negocio)
# ---------------------------------------------------------------------------


class TestAddressServiceListAddresses:

    def _make_service(self, mock_repo):
        from services.address_service import AddressService
        return AddressService(address_repository=mock_repo)

    def test_returns_empty_list_when_no_addresses(self):
        mock_repo = MagicMock()
        mock_repo.get_by_user.return_value = []

        service = self._make_service(mock_repo)
        result = service.list_addresses("user-1")

        assert result == []
        mock_repo.get_by_user.assert_called_once_with("user-1")

    def test_returns_serialized_addresses(self):
        mock_repo = MagicMock()
        mock_repo.get_by_user.return_value = [
            {
                "id": "addr-1",
                "userId": "user-1",
                "street": "Calle 10",
                "city": "Bogotá",
                "department": "Cundinamarca",
                "postalCode": "110111",
                "createdAt": _NOW,
            }
        ]

        service = self._make_service(mock_repo)
        result = service.list_addresses("user-1")

        assert len(result) == 1
        addr = result[0]
        assert addr["id"] == "addr-1"
        assert addr["user_id"] == "user-1"
        assert addr["street"] == "Calle 10"
        assert addr["city"] == "Bogotá"
        assert addr["department"] == "Cundinamarca"
        assert addr["postal_code"] == "110111"
        assert addr["created_at"] == _NOW_ISO


class TestAddressServiceCreateAddress:

    def _make_service(self, mock_repo):
        from services.address_service import AddressService
        return AddressService(address_repository=mock_repo)

    def test_creates_address_successfully(self):
        mock_repo = MagicMock()
        mock_repo.count_by_user.return_value = 0
        mock_repo.create.return_value = {
            "id": "addr-new",
            "userId": "user-1",
            "street": "Calle 10",
            "city": "Bogotá",
            "department": "Cundinamarca",
            "postalCode": None,
            "createdAt": _NOW,
        }

        service = self._make_service(mock_repo)
        result = service.create_address(
            user_id="user-1",
            street="Calle 10",
            city="Bogotá",
            department="Cundinamarca",
        )

        assert result["id"] == "addr-new"
        assert result["street"] == "Calle 10"
        mock_repo.create.assert_called_once_with(
            user_id="user-1",
            street="Calle 10",
            city="Bogotá",
            department="Cundinamarca",
            postal_code=None,
        )

    def test_raises_limit_exceeded_when_5_addresses_exist(self):
        """Debe lanzar AddressLimitExceededError cuando el usuario ya tiene 5 direcciones (Req. 18.3)."""
        from services.address_service import AddressLimitExceededError

        mock_repo = MagicMock()
        mock_repo.count_by_user.return_value = 5

        service = self._make_service(mock_repo)

        with pytest.raises(AddressLimitExceededError):
            service.create_address(
                user_id="user-1",
                street="Calle 10",
                city="Bogotá",
                department="Cundinamarca",
            )

        mock_repo.create.assert_not_called()

    def test_allows_exactly_5th_address(self):
        """Debe permitir crear la 5ª dirección (límite exacto)."""
        mock_repo = MagicMock()
        mock_repo.count_by_user.return_value = 4
        mock_repo.create.return_value = {
            "id": "addr-5",
            "userId": "user-1",
            "street": "Calle 50",
            "city": "Medellín",
            "department": "Antioquia",
            "postalCode": None,
            "createdAt": _NOW,
        }

        service = self._make_service(mock_repo)
        result = service.create_address(
            user_id="user-1",
            street="Calle 50",
            city="Medellín",
            department="Antioquia",
        )

        assert result["id"] == "addr-5"
        mock_repo.create.assert_called_once()

    def test_raises_limit_exceeded_when_more_than_5_exist(self):
        """Debe lanzar AddressLimitExceededError cuando el usuario tiene más de 5 (Req. 18.3)."""
        from services.address_service import AddressLimitExceededError

        mock_repo = MagicMock()
        mock_repo.count_by_user.return_value = 6

        service = self._make_service(mock_repo)

        with pytest.raises(AddressLimitExceededError):
            service.create_address(
                user_id="user-1",
                street="Calle 10",
                city="Bogotá",
                department="Cundinamarca",
            )

    def test_creates_address_with_postal_code(self):
        mock_repo = MagicMock()
        mock_repo.count_by_user.return_value = 2
        mock_repo.create.return_value = {
            "id": "addr-new",
            "userId": "user-1",
            "street": "Carrera 7",
            "city": "Cali",
            "department": "Valle del Cauca",
            "postalCode": "760001",
            "createdAt": _NOW,
        }

        service = self._make_service(mock_repo)
        result = service.create_address(
            user_id="user-1",
            street="Carrera 7",
            city="Cali",
            department="Valle del Cauca",
            postal_code="760001",
        )

        assert result["postal_code"] == "760001"
        mock_repo.create.assert_called_once_with(
            user_id="user-1",
            street="Carrera 7",
            city="Cali",
            department="Valle del Cauca",
            postal_code="760001",
        )


class TestAddressServiceDeleteAddress:

    def _make_service(self, mock_repo):
        from services.address_service import AddressService
        return AddressService(address_repository=mock_repo)

    def test_deletes_address_successfully(self):
        mock_repo = MagicMock()
        mock_repo.delete.return_value = None

        service = self._make_service(mock_repo)
        service.delete_address(user_id="user-1", address_id="addr-1")

        mock_repo.delete.assert_called_once_with(address_id="addr-1", user_id="user-1")

    def test_raises_not_found_for_nonexistent_address(self):
        from repositories.address_repository import AddressNotFoundError
        from services.address_service import AddressNotFoundServiceError

        mock_repo = MagicMock()
        mock_repo.delete.side_effect = AddressNotFoundError("nonexistent")

        service = self._make_service(mock_repo)

        with pytest.raises(AddressNotFoundServiceError):
            service.delete_address(user_id="user-1", address_id="nonexistent")

    def test_raises_not_found_for_address_of_other_user(self):
        """Debe lanzar AddressNotFoundServiceError si la dirección pertenece a otro usuario."""
        from repositories.address_repository import AddressNotFoundError
        from services.address_service import AddressNotFoundServiceError

        mock_repo = MagicMock()
        mock_repo.delete.side_effect = AddressNotFoundError("addr-other")

        service = self._make_service(mock_repo)

        with pytest.raises(AddressNotFoundServiceError):
            service.delete_address(user_id="user-1", address_id="addr-other")


# ---------------------------------------------------------------------------
# Tests – Modelo Pydantic AddressCreate (Req. 18.2)
# ---------------------------------------------------------------------------


class TestAddressCreateModel:
    """Verifica la validación del modelo Pydantic para creación de direcciones."""

    def test_valid_address_with_all_fields(self):
        from models.address import AddressCreate

        addr = AddressCreate(
            street="Calle 10 # 5-20",
            city="Bogotá",
            department="Cundinamarca",
            postal_code="110111",
        )
        assert addr.street == "Calle 10 # 5-20"
        assert addr.city == "Bogotá"
        assert addr.department == "Cundinamarca"
        assert addr.postal_code == "110111"

    def test_valid_address_without_postal_code(self):
        from models.address import AddressCreate

        addr = AddressCreate(
            street="Calle 10",
            city="Bogotá",
            department="Cundinamarca",
        )
        assert addr.postal_code is None

    def test_rejects_empty_street(self):
        from pydantic import ValidationError
        from models.address import AddressCreate

        with pytest.raises(ValidationError):
            AddressCreate(street="", city="Bogotá", department="Cundinamarca")

    def test_rejects_empty_city(self):
        from pydantic import ValidationError
        from models.address import AddressCreate

        with pytest.raises(ValidationError):
            AddressCreate(street="Calle 10", city="", department="Cundinamarca")

    def test_rejects_empty_department(self):
        from pydantic import ValidationError
        from models.address import AddressCreate

        with pytest.raises(ValidationError):
            AddressCreate(street="Calle 10", city="Bogotá", department="")

    def test_rejects_missing_street(self):
        from pydantic import ValidationError
        from models.address import AddressCreate

        with pytest.raises(ValidationError):
            AddressCreate(city="Bogotá", department="Cundinamarca")

    def test_rejects_missing_city(self):
        from pydantic import ValidationError
        from models.address import AddressCreate

        with pytest.raises(ValidationError):
            AddressCreate(street="Calle 10", department="Cundinamarca")

    def test_rejects_missing_department(self):
        from pydantic import ValidationError
        from models.address import AddressCreate

        with pytest.raises(ValidationError):
            AddressCreate(street="Calle 10", city="Bogotá")
