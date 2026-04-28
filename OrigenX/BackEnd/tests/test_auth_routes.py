"""
test_auth_routes.py – Tests de integración para los endpoints de autenticación.

Verifica el comportamiento HTTP de los endpoints usando TestClient de FastAPI.

Requerimientos: 1.1, 1.2, 1.3, 1.4, 2.1, 2.2, 2.4, 2.5, RNF-003.3, RNF-009.3
"""

from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

# Los mocks de Firebase se cargan en conftest.py antes de importar la app
from main import app
from middleware.rate_limit import auth_rate_limiter
from services.auth_service import (
    AuthServiceError,
    EmailAlreadyExistsError,
)


@pytest.fixture(autouse=True)
def reset_rate_limiter():
    """Resetear el rate limiter antes de cada test para evitar interferencias."""
    auth_rate_limiter._records.clear()
    yield
    auth_rate_limiter._records.clear()


@pytest.fixture
def client():
    """Cliente de prueba para la aplicación FastAPI."""
    return TestClient(app, raise_server_exceptions=False)


@pytest.fixture
def mock_auth_service():
    """Mock del AuthService para inyectar en los tests de rutas."""
    with patch("routes.auth.AuthService") as mock_cls:
        mock_instance = MagicMock()
        mock_cls.return_value = mock_instance
        yield mock_instance


# ---------------------------------------------------------------------------
# Tests de POST /api/auth/register
# ---------------------------------------------------------------------------

class TestRegisterEndpoint:
    """Tests del endpoint POST /api/auth/register (Req. 1.1, 1.2, 1.3, 1.4)."""

    def test_successful_registration_returns_201(self, client, mock_auth_service):
        """Registro exitoso debe retornar HTTP 201 (Req. 1.1)."""
        mock_auth_service.register_user.return_value = {
            "id": "new-uid",
            "name": "Juan Pérez",
            "email": "juan@example.com",
            "role": "CONSUMER",
            "createdAt": datetime.now(timezone.utc),
            "updatedAt": datetime.now(timezone.utc),
        }

        response = client.post(
            "/api/auth/register",
            json={
                "name": "Juan Pérez",
                "email": "juan@example.com",
                "password": "password123",
                "role": "CONSUMER",
            },
        )

        assert response.status_code == 201
        data = response.json()
        assert "message" in data
        assert "data" in data
        assert data["data"]["email"] == "juan@example.com"

    def test_duplicate_email_returns_409(self, client, mock_auth_service):
        """Email duplicado debe retornar HTTP 409 (Req. 1.2)."""
        mock_auth_service.register_user.side_effect = EmailAlreadyExistsError()

        response = client.post(
            "/api/auth/register",
            json={
                "name": "Test User",
                "email": "existing@example.com",
                "password": "password123",
                "role": "CONSUMER",
            },
        )

        assert response.status_code == 409
        data = response.json()
        assert "error" in data["detail"]
        assert data["detail"]["error"]["code"] == "EMAIL_ALREADY_EXISTS"

    def test_missing_name_returns_422(self, client):
        """Nombre ausente debe retornar HTTP 422 (validación Pydantic) (Req. 1.3)."""
        response = client.post(
            "/api/auth/register",
            json={
                "email": "test@example.com",
                "password": "password123",
            },
        )
        assert response.status_code == 422

    def test_missing_email_returns_422(self, client):
        """Email ausente debe retornar HTTP 422 (Req. 1.3)."""
        response = client.post(
            "/api/auth/register",
            json={
                "name": "Test User",
                "password": "password123",
            },
        )
        assert response.status_code == 422

    def test_short_password_returns_422(self, client):
        """Contraseña corta debe retornar HTTP 422 (Req. 1.4)."""
        response = client.post(
            "/api/auth/register",
            json={
                "name": "Test User",
                "email": "test@example.com",
                "password": "short",
            },
        )
        assert response.status_code == 422

    def test_invalid_email_format_returns_422(self, client):
        """Email con formato inválido debe retornar HTTP 422."""
        response = client.post(
            "/api/auth/register",
            json={
                "name": "Test User",
                "email": "not-an-email",
                "password": "password123",
            },
        )
        assert response.status_code == 422

    def test_invalid_role_returns_422(self, client):
        """Rol inválido debe retornar HTTP 422 (Req. 3.1)."""
        response = client.post(
            "/api/auth/register",
            json={
                "name": "Test User",
                "email": "test@example.com",
                "password": "password123",
                "role": "SUPERADMIN",
            },
        )
        assert response.status_code == 422

    def test_registration_response_contains_user_data(self, client, mock_auth_service):
        """La respuesta de registro debe contener los datos del usuario (Req. 1.1)."""
        mock_auth_service.register_user.return_value = {
            "id": "uid-789",
            "name": "María García",
            "email": "maria@example.com",
            "role": "PRODUCER",
            "createdAt": datetime.now(timezone.utc),
            "updatedAt": datetime.now(timezone.utc),
        }

        response = client.post(
            "/api/auth/register",
            json={
                "name": "María García",
                "email": "maria@example.com",
                "password": "securepass",
                "role": "PRODUCER",
            },
        )

        assert response.status_code == 201
        data = response.json()["data"]
        assert data["id"] == "uid-789"
        assert data["role"] == "PRODUCER"


# ---------------------------------------------------------------------------
# Tests de POST /api/auth/login
# ---------------------------------------------------------------------------

class TestLoginEndpoint:
    """Tests del endpoint POST /api/auth/login (Req. 2.1, 2.2, RNF-003.3)."""

    def test_valid_token_returns_200(self, client, mock_auth_service):
        """Token válido debe retornar HTTP 200 con datos del usuario (Req. 2.1)."""
        mock_auth_service.verify_id_token.return_value = {
            "uid": "user-uid",
            "email": "user@example.com",
            "role": "CONSUMER",
        }
        mock_auth_service.get_user_by_uid.return_value = {
            "id": "user-uid",
            "name": "Test User",
            "email": "user@example.com",
            "role": "CONSUMER",
        }

        response = client.post(
            "/api/auth/login",
            json={
                "email": "user@example.com",
                "password": "valid-firebase-id-token",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert data["data"]["email"] == "user@example.com"

    def test_invalid_token_returns_401(self, client, mock_auth_service):
        """Token inválido debe retornar HTTP 401 con mensaje genérico (Req. 2.2)."""
        mock_auth_service.verify_id_token.side_effect = AuthServiceError(
            "Token inválido", "INVALID_TOKEN"
        )

        response = client.post(
            "/api/auth/login",
            json={
                "email": "user@example.com",
                "password": "invalid-token",
            },
        )

        assert response.status_code == 401
        data = response.json()
        # El mensaje debe ser genérico, sin revelar cuál campo es incorrecto (Req. 2.2)
        assert "detail" in data
        assert data["detail"]["error"]["code"] == "INVALID_CREDENTIALS"

    def test_error_message_is_generic(self, client, mock_auth_service):
        """El mensaje de error no debe revelar si el email o contraseña son incorrectos (Req. 2.2)."""
        mock_auth_service.verify_id_token.side_effect = AuthServiceError(
            "Token inválido", "INVALID_TOKEN"
        )

        response = client.post(
            "/api/auth/login",
            json={
                "email": "user@example.com",
                "password": "wrong-token",
            },
        )

        assert response.status_code == 401
        message = response.json()["detail"]["error"]["message"]
        # El mensaje no debe mencionar "email" ni "contraseña" específicamente
        assert "email" not in message.lower() or "contraseña" not in message.lower()
        # Debe ser el mensaje genérico
        assert "Credenciales inválidas" in message

    def test_rate_limiting_after_5_failures(self, client, mock_auth_service):
        """Debe retornar HTTP 429 tras 5 intentos fallidos desde la misma IP (Req. RNF-003.3)."""
        mock_auth_service.verify_id_token.side_effect = AuthServiceError(
            "Token inválido", "INVALID_TOKEN"
        )

        # Realizar 5 intentos fallidos
        for _ in range(5):
            client.post(
                "/api/auth/login",
                json={"email": "user@example.com", "password": "bad-token"},
                headers={"X-Forwarded-For": "10.10.10.10"},
            )

        # El 6to intento debe ser bloqueado
        response = client.post(
            "/api/auth/login",
            json={"email": "user@example.com", "password": "bad-token"},
            headers={"X-Forwarded-For": "10.10.10.10"},
        )

        assert response.status_code == 429

    def test_empty_password_returns_401(self, client, mock_auth_service):
        """Password vacío debe retornar HTTP 401."""
        response = client.post(
            "/api/auth/login",
            json={"email": "user@example.com", "password": ""},
        )
        assert response.status_code == 401


# ---------------------------------------------------------------------------
# Tests de POST /api/auth/forgot-password
# ---------------------------------------------------------------------------

class TestForgotPasswordEndpoint:
    """Tests del endpoint POST /api/auth/forgot-password (Req. 2.4, 2.5)."""

    def test_existing_email_returns_200(self, client, mock_auth_service):
        """Email existente debe retornar HTTP 200 con mensaje de confirmación (Req. 2.4)."""
        mock_auth_service.send_password_reset_email.return_value = None

        response = client.post(
            "/api/auth/forgot-password",
            json={"email": "existing@example.com"},
        )

        assert response.status_code == 200
        assert "message" in response.json()

    def test_nonexistent_email_returns_same_200(self, client, mock_auth_service):
        """Email no existente debe retornar el mismo HTTP 200 (Req. 2.5)."""
        mock_auth_service.send_password_reset_email.return_value = None

        response = client.post(
            "/api/auth/forgot-password",
            json={"email": "nonexistent@example.com"},
        )

        assert response.status_code == 200

    def test_same_message_for_existing_and_nonexistent_email(
        self, client, mock_auth_service
    ):
        """El mensaje debe ser idéntico para emails existentes y no existentes (Req. 2.5)."""
        mock_auth_service.send_password_reset_email.return_value = None

        response_existing = client.post(
            "/api/auth/forgot-password",
            json={"email": "existing@example.com"},
        )
        response_nonexistent = client.post(
            "/api/auth/forgot-password",
            json={"email": "nonexistent@example.com"},
        )

        assert response_existing.json()["message"] == response_nonexistent.json()["message"]

    def test_invalid_email_returns_422(self, client):
        """Email inválido debe retornar HTTP 422."""
        response = client.post(
            "/api/auth/forgot-password",
            json={"email": "not-an-email"},
        )
        assert response.status_code == 422

    def test_missing_email_returns_422(self, client):
        """Email ausente debe retornar HTTP 422."""
        response = client.post(
            "/api/auth/forgot-password",
            json={},
        )
        assert response.status_code == 422


# ---------------------------------------------------------------------------
# Tests de POST /api/auth/reset-password
# ---------------------------------------------------------------------------

class TestResetPasswordEndpoint:
    """Tests del endpoint POST /api/auth/reset-password (Req. 2.4)."""

    def test_reset_password_returns_200(self, client):
        """El endpoint de reset debe retornar HTTP 200."""
        response = client.post(
            "/api/auth/reset-password",
            json={
                "token": "reset-token-123",
                "new_password": "newpassword123",
            },
        )
        assert response.status_code == 200
        assert "message" in response.json()

    def test_short_new_password_returns_422(self, client):
        """Nueva contraseña corta debe retornar HTTP 422."""
        response = client.post(
            "/api/auth/reset-password",
            json={
                "token": "reset-token-123",
                "new_password": "short",
            },
        )
        assert response.status_code == 422


# ---------------------------------------------------------------------------
# Tests del middleware de autorización (RBAC)
# ---------------------------------------------------------------------------

class TestAuthMiddleware:
    """Tests del middleware de autorización por roles (Req. 3.1, 3.2, 3.3, 3.4)."""

    def test_missing_token_returns_401(self, client):
        """Solicitud sin token debe retornar HTTP 401 (Req. 3.4)."""
        # Usar un endpoint protegido – el health check no está protegido,
        # pero podemos verificar el comportamiento del middleware directamente
        # a través de get_current_user
        from fastapi import FastAPI, Depends
        from fastapi.testclient import TestClient
        from middleware.auth_middleware import get_current_user

        test_app = FastAPI()

        @test_app.get("/protected")
        async def protected(user: dict = Depends(get_current_user)):
            return {"user": user}

        test_client = TestClient(test_app, raise_server_exceptions=False)
        response = test_client.get("/protected")
        assert response.status_code == 401

    def test_invalid_token_returns_401(self, mock_firebase_auth, firebase_exceptions):
        """Token inválido debe retornar HTTP 401 (Req. 3.4)."""
        from fastapi import FastAPI, Depends
        from fastapi.testclient import TestClient
        from middleware.auth_middleware import get_current_user

        mock_firebase_auth.verify_id_token.side_effect = (
            firebase_exceptions["InvalidIdTokenError"]()
        )

        test_app = FastAPI()

        @test_app.get("/protected")
        async def protected(user: dict = Depends(get_current_user)):
            return {"user": user}

        test_client = TestClient(test_app, raise_server_exceptions=False)
        response = test_client.get(
            "/protected",
            headers={"Authorization": "Bearer invalid-token"},
        )
        assert response.status_code == 401

    def test_wrong_role_returns_403(self, mock_firebase_auth):
        """Rol incorrecto debe retornar HTTP 403 (Req. 3.2, 3.3)."""
        from fastapi import FastAPI, Depends
        from fastapi.testclient import TestClient
        from middleware.auth_middleware import require_roles
        from models.user import UserRole

        # Token válido pero con rol CONSUMER
        mock_firebase_auth.verify_id_token.return_value = {
            "uid": "consumer-uid",
            "email": "consumer@example.com",
            "role": "CONSUMER",
        }

        test_app = FastAPI()

        @test_app.get("/producer-only")
        async def producer_only(
            user: dict = Depends(require_roles(UserRole.PRODUCER))
        ):
            return {"user": user}

        test_client = TestClient(test_app, raise_server_exceptions=False)
        response = test_client.get(
            "/producer-only",
            headers={"Authorization": "Bearer consumer-token"},
        )
        assert response.status_code == 403

    def test_correct_role_returns_200(self, mock_firebase_auth):
        """Rol correcto debe permitir el acceso (Req. 3.2)."""
        from fastapi import FastAPI, Depends
        from fastapi.testclient import TestClient
        from middleware.auth_middleware import require_roles
        from models.user import UserRole

        mock_firebase_auth.verify_id_token.return_value = {
            "uid": "producer-uid",
            "email": "producer@example.com",
            "role": "PRODUCER",
        }

        test_app = FastAPI()

        @test_app.get("/producer-only")
        async def producer_only(
            user: dict = Depends(require_roles(UserRole.PRODUCER))
        ):
            return {"user": user}

        test_client = TestClient(test_app, raise_server_exceptions=False)
        response = test_client.get(
            "/producer-only",
            headers={"Authorization": "Bearer producer-token"},
        )
        assert response.status_code == 200

    def test_admin_cannot_access_consumer_only_endpoint(self, mock_firebase_auth):
        """Admin no debe acceder a endpoints exclusivos de Consumer (Req. 3.3)."""
        from fastapi import FastAPI, Depends
        from fastapi.testclient import TestClient
        from middleware.auth_middleware import require_roles
        from models.user import UserRole

        mock_firebase_auth.verify_id_token.return_value = {
            "uid": "admin-uid",
            "email": "admin@example.com",
            "role": "ADMIN",
        }

        test_app = FastAPI()

        @test_app.get("/consumer-only")
        async def consumer_only(
            user: dict = Depends(require_roles(UserRole.CONSUMER))
        ):
            return {"user": user}

        test_client = TestClient(test_app, raise_server_exceptions=False)
        response = test_client.get(
            "/consumer-only",
            headers={"Authorization": "Bearer admin-token"},
        )
        assert response.status_code == 403
