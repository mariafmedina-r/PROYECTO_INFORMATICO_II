"""
conftest.py – Fixtures compartidos para los tests del backend.

Configura mocks de Firebase Admin SDK para que los tests no requieran
credenciales reales de Firebase.
"""

import sys
import os
from unittest.mock import MagicMock, patch

import pytest

# ---------------------------------------------------------------------------
# Mockear firebase_admin ANTES de que cualquier módulo del proyecto lo importe.
# Esto evita que se necesiten credenciales reales de Firebase en los tests.
# ---------------------------------------------------------------------------

# Crear módulos mock para firebase_admin y sus submódulos
firebase_admin_mock = MagicMock()
firebase_admin_auth_mock = MagicMock()
firebase_admin_firestore_mock = MagicMock()
firebase_admin_storage_mock = MagicMock()
firebase_admin_credentials_mock = MagicMock()
firebase_admin_exceptions_mock = MagicMock()

# Definir excepciones reales para que los tests puedan capturarlas
class _FirebaseError(Exception):
    pass

class _EmailAlreadyExistsError(_FirebaseError):
    pass

class _UserNotFoundError(_FirebaseError):
    pass

class _ExpiredIdTokenError(_FirebaseError):
    pass

class _InvalidIdTokenError(_FirebaseError):
    pass

class _RevokedIdTokenError(_FirebaseError):
    pass

# Asignar excepciones al mock de auth
firebase_admin_auth_mock.EmailAlreadyExistsError = _EmailAlreadyExistsError
firebase_admin_auth_mock.UserNotFoundError = _UserNotFoundError
firebase_admin_auth_mock.ExpiredIdTokenError = _ExpiredIdTokenError
firebase_admin_auth_mock.InvalidIdTokenError = _InvalidIdTokenError
firebase_admin_auth_mock.RevokedIdTokenError = _RevokedIdTokenError

# Asignar excepción base al mock de exceptions
firebase_admin_exceptions_mock.FirebaseError = _FirebaseError

# Registrar los mocks en sys.modules
sys.modules["firebase_admin"] = firebase_admin_mock
sys.modules["firebase_admin.auth"] = firebase_admin_auth_mock
sys.modules["firebase_admin.firestore"] = firebase_admin_firestore_mock
sys.modules["firebase_admin.storage"] = firebase_admin_storage_mock
sys.modules["firebase_admin.credentials"] = firebase_admin_credentials_mock
sys.modules["firebase_admin.exceptions"] = firebase_admin_exceptions_mock

# Configurar firebase_admin._apps para simular que ya está inicializado
firebase_admin_mock._apps = {"[DEFAULT]": MagicMock()}
firebase_admin_mock.auth = firebase_admin_auth_mock
firebase_admin_mock.firestore = firebase_admin_firestore_mock
firebase_admin_mock.storage = firebase_admin_storage_mock
firebase_admin_mock.credentials = firebase_admin_credentials_mock
firebase_admin_mock.exceptions = firebase_admin_exceptions_mock


@pytest.fixture
def mock_firebase_auth():
    """Fixture que expone el mock de firebase_admin.auth para configurarlo en cada test.

    Resetea el estado del mock antes de cada test para evitar contaminación entre tests.
    """
    # Resetear side_effects y return_values de los métodos más usados
    firebase_admin_auth_mock.create_user.reset_mock(side_effect=True, return_value=True)
    firebase_admin_auth_mock.set_custom_user_claims.reset_mock(side_effect=True, return_value=True)
    firebase_admin_auth_mock.delete_user.reset_mock(side_effect=True, return_value=True)
    firebase_admin_auth_mock.verify_id_token.reset_mock(side_effect=True, return_value=True)
    firebase_admin_auth_mock.get_user_by_email.reset_mock(side_effect=True, return_value=True)
    return firebase_admin_auth_mock


@pytest.fixture
def mock_firestore():
    """Fixture que expone el mock de firebase_admin.firestore."""
    return firebase_admin_firestore_mock


@pytest.fixture
def firebase_exceptions():
    """Fixture que expone las clases de excepción de Firebase para usar en tests."""
    return {
        "FirebaseError": _FirebaseError,
        "EmailAlreadyExistsError": _EmailAlreadyExistsError,
        "UserNotFoundError": _UserNotFoundError,
        "ExpiredIdTokenError": _ExpiredIdTokenError,
        "InvalidIdTokenError": _InvalidIdTokenError,
        "RevokedIdTokenError": _RevokedIdTokenError,
    }


@pytest.fixture
def mock_firebase_storage():
    """Fixture que expone el mock de firebase_admin.storage para configurarlo en cada test."""
    firebase_admin_storage_mock.reset_mock(side_effect=True, return_value=True)
    return firebase_admin_storage_mock
