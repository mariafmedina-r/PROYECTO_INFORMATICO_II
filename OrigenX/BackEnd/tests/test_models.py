"""
test_models.py – Tests unitarios para los modelos Pydantic de autenticación.

Verifica que la validación de campos obligatorios y restricciones funcione
correctamente sin necesidad de Firebase.

Requerimientos: 1.1, 1.2, 1.3, 1.4, 3.1
"""

import pytest
from pydantic import ValidationError

# Los mocks de Firebase se cargan en conftest.py antes de estos imports
from models.user import (
    ForgotPasswordRequest,
    LoginRequest,
    ResetPasswordRequest,
    UserCreate,
    UserRole,
)


# ---------------------------------------------------------------------------
# Tests de UserCreate – Registro de usuario
# ---------------------------------------------------------------------------

class TestUserCreateValidation:
    """Tests de validación del modelo UserCreate (Req. 1.1, 1.3, 1.4)."""

    def test_valid_consumer_registration(self):
        """Un registro válido con todos los campos debe crear el modelo correctamente."""
        user = UserCreate(
            name="Juan Pérez",
            email="juan@example.com",
            password="password123",
            role=UserRole.CONSUMER,
        )
        assert user.name == "Juan Pérez"
        assert str(user.email) == "juan@example.com"
        assert user.role == UserRole.CONSUMER

    def test_valid_producer_registration(self):
        """Un registro válido con rol PRODUCER debe funcionar."""
        user = UserCreate(
            name="Finca El Paraíso",
            email="finca@example.com",
            password="securepass",
            role=UserRole.PRODUCER,
        )
        assert user.role == UserRole.PRODUCER

    def test_default_role_is_consumer(self):
        """El rol por defecto debe ser CONSUMER (Req. 1.1)."""
        user = UserCreate(
            name="Test User",
            email="test@example.com",
            password="password123",
        )
        assert user.role == UserRole.CONSUMER

    def test_missing_name_raises_validation_error(self):
        """Nombre vacío debe lanzar ValidationError (Req. 1.3)."""
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(
                name="",
                email="test@example.com",
                password="password123",
            )
        errors = exc_info.value.errors()
        assert any(e["loc"] == ("name",) for e in errors)

    def test_missing_email_raises_validation_error(self):
        """Email ausente debe lanzar ValidationError (Req. 1.3)."""
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(
                name="Test User",
                password="password123",
            )
        errors = exc_info.value.errors()
        assert any(e["loc"] == ("email",) for e in errors)

    def test_invalid_email_format_raises_validation_error(self):
        """Email con formato inválido debe lanzar ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(
                name="Test User",
                email="not-an-email",
                password="password123",
            )
        errors = exc_info.value.errors()
        assert any(e["loc"] == ("email",) for e in errors)

    def test_password_too_short_raises_validation_error(self):
        """Contraseña con menos de 8 caracteres debe lanzar ValidationError (Req. 1.4)."""
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(
                name="Test User",
                email="test@example.com",
                password="short",
            )
        errors = exc_info.value.errors()
        assert any(e["loc"] == ("password",) for e in errors)

    def test_password_exactly_7_chars_is_rejected(self):
        """Contraseña de exactamente 7 caracteres debe ser rechazada (Req. 1.4)."""
        with pytest.raises(ValidationError):
            UserCreate(
                name="Test User",
                email="test@example.com",
                password="1234567",
            )

    def test_password_exactly_8_chars_is_accepted(self):
        """Contraseña de exactamente 8 caracteres debe ser aceptada (Req. 1.4)."""
        user = UserCreate(
            name="Test User",
            email="test@example.com",
            password="12345678",
        )
        assert user.password == "12345678"

    def test_empty_password_raises_validation_error(self):
        """Contraseña vacía debe lanzar ValidationError (Req. 1.3, 1.4)."""
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(
                name="Test User",
                email="test@example.com",
                password="",
            )
        errors = exc_info.value.errors()
        assert any(e["loc"] == ("password",) for e in errors)

    def test_invalid_role_raises_validation_error(self):
        """Rol inválido debe lanzar ValidationError (Req. 3.1)."""
        with pytest.raises(ValidationError):
            UserCreate(
                name="Test User",
                email="test@example.com",
                password="password123",
                role="SUPERADMIN",
            )

    def test_all_valid_roles_accepted(self):
        """Los tres roles válidos deben ser aceptados (Req. 3.1)."""
        for role in [UserRole.CONSUMER, UserRole.PRODUCER, UserRole.ADMIN]:
            user = UserCreate(
                name="Test User",
                email=f"test_{role.value.lower()}@example.com",
                password="password123",
                role=role,
            )
            assert user.role == role


# ---------------------------------------------------------------------------
# Tests de LoginRequest
# ---------------------------------------------------------------------------

class TestLoginRequestValidation:
    """Tests de validación del modelo LoginRequest (Req. 2.1)."""

    def test_valid_login_request(self):
        """Un request de login válido debe crearse correctamente."""
        req = LoginRequest(email="user@example.com", password="mytoken123")
        assert str(req.email) == "user@example.com"

    def test_missing_email_raises_validation_error(self):
        """Email ausente en login debe lanzar ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            LoginRequest(password="mytoken123")
        errors = exc_info.value.errors()
        assert any(e["loc"] == ("email",) for e in errors)

    def test_missing_password_raises_validation_error(self):
        """Password ausente en login debe lanzar ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            LoginRequest(email="user@example.com")
        errors = exc_info.value.errors()
        assert any(e["loc"] == ("password",) for e in errors)

    def test_invalid_email_in_login_raises_validation_error(self):
        """Email inválido en login debe lanzar ValidationError."""
        with pytest.raises(ValidationError):
            LoginRequest(email="not-valid", password="mytoken123")


# ---------------------------------------------------------------------------
# Tests de ForgotPasswordRequest
# ---------------------------------------------------------------------------

class TestForgotPasswordRequestValidation:
    """Tests de validación del modelo ForgotPasswordRequest (Req. 2.4)."""

    def test_valid_forgot_password_request(self):
        """Un request de recuperación válido debe crearse correctamente."""
        req = ForgotPasswordRequest(email="user@example.com")
        assert str(req.email) == "user@example.com"

    def test_missing_email_raises_validation_error(self):
        """Email ausente en recuperación debe lanzar ValidationError."""
        with pytest.raises(ValidationError):
            ForgotPasswordRequest()

    def test_invalid_email_raises_validation_error(self):
        """Email inválido en recuperación debe lanzar ValidationError."""
        with pytest.raises(ValidationError):
            ForgotPasswordRequest(email="not-an-email")


# ---------------------------------------------------------------------------
# Tests de UserRole enum
# ---------------------------------------------------------------------------

class TestUserRoleEnum:
    """Tests del enum UserRole (Req. 3.1)."""

    def test_role_values(self):
        """Los valores del enum deben ser los strings correctos."""
        assert UserRole.CONSUMER.value == "CONSUMER"
        assert UserRole.PRODUCER.value == "PRODUCER"
        assert UserRole.ADMIN.value == "ADMIN"

    def test_role_count(self):
        """Deben existir exactamente 3 roles (Req. 3.1)."""
        assert len(UserRole) == 3
