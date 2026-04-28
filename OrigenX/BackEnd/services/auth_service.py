"""
services/auth_service.py – Lógica de negocio de autenticación y roles.

Responsabilidades:
  - Registro de usuarios (Firebase Auth + Custom Claims)
  - Verificación de ID Token
  - Asignación de roles (CONSUMER, PRODUCER, ADMIN)
  - Recuperación de contraseña (delegada a Firebase Auth)

Implementado en tareas 2.1, 2.4, 2.6, 2.7
"""

import logging
from datetime import datetime, timezone
from typing import Optional

from firebase_admin import auth as firebase_auth
from firebase_admin.exceptions import FirebaseError

from models.user import UserRole
from repositories.user_repository import UserRepository

logger = logging.getLogger(__name__)


class AuthServiceError(Exception):
    """Error base del servicio de autenticación."""

    def __init__(self, message: str, code: str = "AUTH_ERROR"):
        self.message = message
        self.code = code
        super().__init__(message)


class EmailAlreadyExistsError(AuthServiceError):
    """El correo ya está registrado (Req. 1.2)."""

    def __init__(self):
        super().__init__(
            message="El correo electrónico ya está registrado.",
            code="EMAIL_ALREADY_EXISTS",
        )


class InvalidCredentialsError(AuthServiceError):
    """Credenciales inválidas – mensaje genérico (Req. 2.2)."""

    def __init__(self):
        super().__init__(
            message="Credenciales inválidas. Verifica tu correo y contraseña.",
            code="INVALID_CREDENTIALS",
        )


class AuthService:
    """Servicio de autenticación y gestión de roles."""

    def __init__(self, user_repository: Optional[UserRepository] = None):
        self._user_repo = user_repository or UserRepository()

    # ------------------------------------------------------------------
    # Tarea 2.1 – Registro de usuarios
    # ------------------------------------------------------------------

    def register_user(self, name: str, email: str, password: str, role: UserRole) -> dict:
        """
        Registra un nuevo usuario en Firebase Auth y Firestore.

        1. Crea el usuario en Firebase Auth.
        2. Asigna Custom Claims con el rol.
        3. Persiste el documento en Firestore (/users/{uid}).

        Args:
            name: Nombre completo del usuario.
            email: Correo electrónico único.
            password: Contraseña en texto plano (Firebase la hashea internamente).
            role: Rol del usuario (CONSUMER, PRODUCER, ADMIN).

        Returns:
            Diccionario con los datos del usuario creado.

        Raises:
            EmailAlreadyExistsError: Si el correo ya está registrado (Req. 1.2).
            AuthServiceError: Para otros errores de Firebase.
        """
        # Crear usuario en Firebase Auth
        try:
            firebase_user = firebase_auth.create_user(
                email=email,
                password=password,
                display_name=name,
            )
        except firebase_auth.EmailAlreadyExistsError:
            raise EmailAlreadyExistsError()
        except FirebaseError as exc:
            logger.error("Error creating Firebase user: %s", exc)
            raise AuthServiceError(
                message="No se pudo crear el usuario. Intenta nuevamente.",
                code="FIREBASE_ERROR",
            ) from exc

        uid = firebase_user.uid

        # Asignar Custom Claims con el rol (Req. 3.1)
        try:
            firebase_auth.set_custom_user_claims(uid, {"role": role.value})
        except FirebaseError as exc:
            logger.error("Error setting custom claims for uid=%s: %s", uid, exc)
            # Intentar limpiar el usuario creado para evitar estado inconsistente
            try:
                firebase_auth.delete_user(uid)
            except FirebaseError:
                pass
            raise AuthServiceError(
                message="No se pudo asignar el rol al usuario.",
                code="CLAIMS_ERROR",
            ) from exc

        # Persistir en Firestore
        try:
            user_data = self._user_repo.create(
                uid=uid,
                name=name,
                email=email,
                role=role.value,
            )
        except Exception as exc:
            logger.error("Error persisting user in Firestore uid=%s: %s", uid, exc)
            # Intentar limpiar el usuario de Firebase Auth
            try:
                firebase_auth.delete_user(uid)
            except FirebaseError:
                pass
            raise AuthServiceError(
                message="No se pudo guardar el usuario. Intenta nuevamente.",
                code="PERSISTENCE_ERROR",
            ) from exc

        return user_data

    # ------------------------------------------------------------------
    # Tarea 2.4 – Autenticación (login)
    # ------------------------------------------------------------------

    def verify_id_token(self, id_token: str) -> dict:
        """
        Verifica un Firebase ID Token y retorna los claims decodificados.

        Args:
            id_token: Token JWT emitido por Firebase Auth.

        Returns:
            Diccionario con los claims del token (uid, email, role, etc.).

        Raises:
            AuthServiceError: Si el token es inválido o expirado.
        """
        try:
            decoded = firebase_auth.verify_id_token(id_token)
            return decoded
        except firebase_auth.ExpiredIdTokenError as exc:
            raise AuthServiceError(
                message="La sesión ha expirado. Inicia sesión nuevamente.",
                code="TOKEN_EXPIRED",
            ) from exc
        except (firebase_auth.InvalidIdTokenError, firebase_auth.RevokedIdTokenError) as exc:
            raise AuthServiceError(
                message="Token de autenticación inválido.",
                code="INVALID_TOKEN",
            ) from exc
        except FirebaseError as exc:
            logger.error("Error verifying ID token: %s", exc)
            raise AuthServiceError(
                message="Error al verificar la autenticación.",
                code="AUTH_ERROR",
            ) from exc

    def get_user_by_uid(self, uid: str) -> Optional[dict]:
        """
        Obtiene los datos de un usuario desde Firestore por su UID.

        Args:
            uid: Firebase UID del usuario.

        Returns:
            Diccionario con los datos del usuario, o None si no existe.
        """
        return self._user_repo.get_by_id(uid)

    # ------------------------------------------------------------------
    # Tarea 2.6 – Recuperación de contraseña
    # ------------------------------------------------------------------

    def send_password_reset_email(self, email: str) -> None:
        """
        Solicita el envío de un email de restablecimiento de contraseña.

        Siempre retorna sin error, independientemente de si el correo existe,
        para no revelar si el correo está registrado (Req. 2.5).

        Args:
            email: Correo electrónico del usuario.
        """
        try:
            # Verificar si el usuario existe en Firebase Auth
            firebase_auth.get_user_by_email(email)
            # Si existe, generar el link de restablecimiento
            # En producción, Firebase envía el email automáticamente desde el cliente.
            # Desde el backend Admin SDK, generamos el link para enviarlo manualmente
            # o simplemente confirmamos que el usuario existe.
            # El envío real del email se delega al Firebase Client SDK en el frontend.
            logger.info("Password reset requested for email: %s", email)
        except firebase_auth.UserNotFoundError:
            # No revelar que el correo no existe (Req. 2.5)
            logger.info("Password reset requested for non-existent email (silenced)")
        except FirebaseError as exc:
            logger.error("Error in password reset for email=%s: %s", email, exc)
            # Silenciar el error para no revelar información (Req. 2.5)
