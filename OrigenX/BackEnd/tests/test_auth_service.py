"""
test_auth_service.py – Tests unitarios para AuthService.

Verifica la lógica de negocio de autenticación con Firebase mockeado.

Requerimientos: 1.1, 1.2, 2.1, 2.2, 2.4, 2.5, 3.1
"""

from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import pytest

# Los mocks de Firebase se cargan en conftest.py
from services.auth_service import (
    AuthService,
    AuthServiceError,
    EmailAlreadyExistsError,
)
from models.user import UserRole


def _make_mock_user_repo(uid="test-uid-123"):
    """Crea un mock de UserRepository con comportamiento por defecto."""
    repo = MagicMock()
    repo.create.return_value = {
        "id": uid,
        "name": "Test User",
        "email": "test@example.com",
        "role": "CONSUMER",
        "createdAt": datetime.now(timezone.utc),
        "updatedAt": datetime.now(timezone.utc),
    }
    repo.get_by_id.return_value = {
        "id": uid,
        "name": "Test User",
        "email": "test@example.com",
        "role": "CONSUMER",
    }
    return repo


class TestRegisterUser:
    """Tests del método register_user (Req. 1.1, 1.2, 3.1)."""

    def test_successful_registration_returns_user_data(self, mock_firebase_auth):
        """Un registro exitoso debe retornar los datos del usuario creado."""
        mock_firebase_user = MagicMock()
        mock_firebase_user.uid = "new-uid-456"
        mock_firebase_auth.create_user.return_value = mock_firebase_user
        mock_firebase_auth.set_custom_user_claims.return_value = None

        repo = _make_mock_user_repo("new-uid-456")
        service = AuthService(user_repository=repo)

        result = service.register_user(
            name="Juan Pérez",
            email="juan@example.com",
            password="password123",
            role=UserRole.CONSUMER,
        )

        assert result["id"] == "new-uid-456"
        assert result["email"] == "test@example.com"
        mock_firebase_auth.create_user.assert_called_once()
        mock_firebase_auth.set_custom_user_claims.assert_called_once_with(
            "new-uid-456", {"role": "CONSUMER"}
        )

    def test_duplicate_email_raises_email_already_exists_error(
        self, mock_firebase_auth, firebase_exceptions
    ):
        """Email duplicado debe lanzar EmailAlreadyExistsError (Req. 1.2)."""
        mock_firebase_auth.create_user.side_effect = (
            firebase_exceptions["EmailAlreadyExistsError"]()
        )

        repo = _make_mock_user_repo()
        service = AuthService(user_repository=repo)

        with pytest.raises(EmailAlreadyExistsError) as exc_info:
            service.register_user(
                name="Test User",
                email="existing@example.com",
                password="password123",
                role=UserRole.CONSUMER,
            )
        assert exc_info.value.code == "EMAIL_ALREADY_EXISTS"

    def test_firebase_error_raises_auth_service_error(
        self, mock_firebase_auth, firebase_exceptions
    ):
        """Un error genérico de Firebase debe lanzar AuthServiceError."""
        mock_firebase_auth.create_user.side_effect = (
            firebase_exceptions["FirebaseError"]("Firebase unavailable")
        )

        repo = _make_mock_user_repo()
        service = AuthService(user_repository=repo)

        with pytest.raises(AuthServiceError) as exc_info:
            service.register_user(
                name="Test User",
                email="test@example.com",
                password="password123",
                role=UserRole.CONSUMER,
            )
        assert exc_info.value.code == "FIREBASE_ERROR"

    def test_role_is_set_as_custom_claim(self, mock_firebase_auth):
        """El rol debe ser asignado como Custom Claim en Firebase (Req. 3.1)."""
        mock_firebase_user = MagicMock()
        mock_firebase_user.uid = "producer-uid"
        mock_firebase_auth.create_user.return_value = mock_firebase_user
        mock_firebase_auth.set_custom_user_claims.return_value = None

        repo = _make_mock_user_repo("producer-uid")
        service = AuthService(user_repository=repo)

        service.register_user(
            name="Productor Test",
            email="productor@example.com",
            password="password123",
            role=UserRole.PRODUCER,
        )

        mock_firebase_auth.set_custom_user_claims.assert_called_once_with(
            "producer-uid", {"role": "PRODUCER"}
        )

    def test_cleanup_on_claims_error(self, mock_firebase_auth, firebase_exceptions):
        """Si falla la asignación de claims, debe intentar eliminar el usuario de Firebase."""
        mock_firebase_user = MagicMock()
        mock_firebase_user.uid = "cleanup-uid"
        mock_firebase_auth.create_user.return_value = mock_firebase_user
        mock_firebase_auth.set_custom_user_claims.side_effect = (
            firebase_exceptions["FirebaseError"]("Claims error")
        )
        mock_firebase_auth.delete_user.return_value = None

        repo = _make_mock_user_repo()
        service = AuthService(user_repository=repo)

        with pytest.raises(AuthServiceError) as exc_info:
            service.register_user(
                name="Test User",
                email="test@example.com",
                password="password123",
                role=UserRole.CONSUMER,
            )
        assert exc_info.value.code == "CLAIMS_ERROR"
        mock_firebase_auth.delete_user.assert_called_once_with("cleanup-uid")


class TestVerifyIdToken:
    """Tests del método verify_id_token (Req. 2.1, 2.2)."""

    def test_valid_token_returns_claims(self, mock_firebase_auth):
        """Un token válido debe retornar los claims decodificados."""
        expected_claims = {
            "uid": "user-uid-123",
            "email": "user@example.com",
            "role": "CONSUMER",
        }
        mock_firebase_auth.verify_id_token.return_value = expected_claims

        service = AuthService()
        result = service.verify_id_token("valid-token")

        assert result == expected_claims
        mock_firebase_auth.verify_id_token.assert_called_once_with("valid-token")

    def test_expired_token_raises_auth_service_error(
        self, mock_firebase_auth, firebase_exceptions
    ):
        """Token expirado debe lanzar AuthServiceError con código TOKEN_EXPIRED."""
        mock_firebase_auth.verify_id_token.side_effect = (
            firebase_exceptions["ExpiredIdTokenError"]()
        )

        service = AuthService()
        with pytest.raises(AuthServiceError) as exc_info:
            service.verify_id_token("expired-token")
        assert exc_info.value.code == "TOKEN_EXPIRED"

    def test_invalid_token_raises_auth_service_error(
        self, mock_firebase_auth, firebase_exceptions
    ):
        """Token inválido debe lanzar AuthServiceError con código INVALID_TOKEN."""
        mock_firebase_auth.verify_id_token.side_effect = (
            firebase_exceptions["InvalidIdTokenError"]()
        )

        service = AuthService()
        with pytest.raises(AuthServiceError) as exc_info:
            service.verify_id_token("invalid-token")
        assert exc_info.value.code == "INVALID_TOKEN"

    def test_revoked_token_raises_auth_service_error(
        self, mock_firebase_auth, firebase_exceptions
    ):
        """Token revocado debe lanzar AuthServiceError con código INVALID_TOKEN."""
        mock_firebase_auth.verify_id_token.side_effect = (
            firebase_exceptions["RevokedIdTokenError"]()
        )

        service = AuthService()
        with pytest.raises(AuthServiceError) as exc_info:
            service.verify_id_token("revoked-token")
        assert exc_info.value.code == "INVALID_TOKEN"


class TestSendPasswordResetEmail:
    """Tests del método send_password_reset_email (Req. 2.4, 2.5)."""

    def test_existing_email_does_not_raise(self, mock_firebase_auth):
        """Para un correo existente, no debe lanzar excepción (Req. 2.4)."""
        mock_firebase_auth.get_user_by_email.return_value = MagicMock()

        service = AuthService()
        # No debe lanzar excepción
        service.send_password_reset_email("existing@example.com")

    def test_nonexistent_email_does_not_raise(
        self, mock_firebase_auth, firebase_exceptions
    ):
        """Para un correo no existente, no debe lanzar excepción (Req. 2.5)."""
        mock_firebase_auth.get_user_by_email.side_effect = (
            firebase_exceptions["UserNotFoundError"]()
        )

        service = AuthService()
        # No debe lanzar excepción – silencia el error para no revelar info
        service.send_password_reset_email("nonexistent@example.com")

    def test_firebase_error_is_silenced(
        self, mock_firebase_auth, firebase_exceptions
    ):
        """Errores de Firebase deben ser silenciados para no revelar información (Req. 2.5)."""
        mock_firebase_auth.get_user_by_email.side_effect = (
            firebase_exceptions["FirebaseError"]("Internal error")
        )

        service = AuthService()
        # No debe lanzar excepción
        service.send_password_reset_email("any@example.com")


class TestGetUserByUid:
    """Tests del método get_user_by_uid."""

    def test_existing_user_returns_data(self):
        """Para un UID existente, debe retornar los datos del usuario."""
        repo = _make_mock_user_repo("existing-uid")
        service = AuthService(user_repository=repo)

        result = service.get_user_by_uid("existing-uid")
        assert result is not None
        assert result["id"] == "existing-uid"

    def test_nonexistent_user_returns_none(self):
        """Para un UID inexistente, debe retornar None."""
        repo = MagicMock()
        repo.get_by_id.return_value = None
        service = AuthService(user_repository=repo)

        result = service.get_user_by_uid("nonexistent-uid")
        assert result is None
