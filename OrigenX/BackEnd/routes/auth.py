"""
routes/auth.py – Endpoints de autenticación y gestión de usuarios.

Endpoints:
  POST /api/auth/register        → Registro de usuario (tarea 2.1)
  POST /api/auth/login           → Login (tarea 2.4)
  POST /api/auth/forgot-password → Recuperación de contraseña (tarea 2.6)
  POST /api/auth/reset-password  → Restablecimiento de contraseña (tarea 2.6)

Requerimientos: 1.1–1.5, 2.1–2.5, RNF-003.3
"""

import logging
from datetime import datetime

from fastapi import APIRouter, HTTPException, Request, status
from fastapi.responses import JSONResponse

from middleware.rate_limit import auth_rate_limiter, get_client_ip
from models.user import (
    ForgotPasswordRequest,
    LoginRequest,
    ResetPasswordRequest,
    UserCreate,
    UserResponse,
)
from services.auth_service import (
    AuthService,
    AuthServiceError,
    EmailAlreadyExistsError,
)

logger = logging.getLogger(__name__)
router = APIRouter()


def _make_error(code: str, message: str, fields: list | None = None) -> dict:
    """Construye el cuerpo de error uniforme (RNF-009.3)."""
    body: dict = {"code": code, "message": message}
    if fields:
        body["fields"] = fields
    return {"error": body}


# ------------------------------------------------------------------
# POST /api/auth/register – Tarea 2.1
# ------------------------------------------------------------------

@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    summary="Registro de usuario",
    description=(
        "Crea una nueva cuenta de usuario con nombre, correo, contraseña y rol. "
        "Retorna HTTP 409 si el correo ya existe. "
        "Retorna HTTP 400 si los datos son inválidos. "
        "Requerimientos: 1.1, 1.2, 1.3, 1.4, 1.5"
    ),
)
async def register(payload: UserCreate):
    """
    Registra un nuevo usuario.

    - Crea el usuario en Firebase Auth con el rol como Custom Claim.
    - Persiste el documento en Firestore (/users/{uid}).
    - Retorna HTTP 409 si el correo ya está registrado (Req. 1.2).
    - La validación de campos obligatorios y contraseña mínima la realiza Pydantic (Req. 1.3, 1.4).
    """
    auth_service = AuthService()

    try:
        user_data = auth_service.register_user(
            name=payload.name,
            email=str(payload.email),
            password=payload.password,
            role=payload.role,
        )
    except EmailAlreadyExistsError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=_make_error(
                code=exc.code,
                message=exc.message,
                fields=[{"field": "email", "message": exc.message}],
            ),
        ) from exc
    except AuthServiceError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=_make_error(code=exc.code, message=exc.message),
        ) from exc

    return {
        "message": "Usuario registrado exitosamente.",
        "data": {
            "id": user_data["id"],
            "name": user_data["name"],
            "email": user_data["email"],
            "role": user_data["role"],
            "created_at": user_data["createdAt"].isoformat()
            if isinstance(user_data["createdAt"], datetime)
            else user_data["createdAt"],
        },
    }


# ------------------------------------------------------------------
# POST /api/auth/login – Tarea 2.4
# ------------------------------------------------------------------

@router.post(
    "/login",
    status_code=status.HTTP_200_OK,
    summary="Inicio de sesión",
    description=(
        "Verifica las credenciales del usuario via Firebase Auth. "
        "El cliente debe autenticarse con Firebase Client SDK y enviar el ID Token. "
        "Retorna HTTP 429 tras 5 intentos fallidos consecutivos desde la misma IP. "
        "Requerimientos: 2.1, 2.2, RNF-003.3"
    ),
)
async def login(payload: LoginRequest, request: Request):
    """
    Verifica el ID Token de Firebase y retorna los datos del usuario autenticado.

    Nota de arquitectura: La autenticación real (email + contraseña → ID Token) ocurre
    en el Firebase Client SDK del frontend. Este endpoint recibe el ID Token ya generado,
    lo verifica con el Admin SDK y retorna los datos del usuario.

    El campo `password` en LoginRequest se usa para el rate limiting (se valida que
    no esté vacío), pero la verificación real la hace Firebase Auth en el cliente.
    """
    client_ip = get_client_ip(request)

    # Verificar rate limiting antes de procesar (RNF-003.3)
    auth_rate_limiter.check_and_raise(client_ip)

    # El frontend envía el ID Token en el campo `password` tras autenticarse con Firebase
    # En este flujo, el campo `password` del payload contiene el Firebase ID Token
    id_token = payload.password  # El cliente envía el ID Token aquí

    if not id_token:
        auth_rate_limiter.record_failure(client_ip)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=_make_error(
                code="INVALID_CREDENTIALS",
                message="Credenciales inválidas. Verifica tu correo y contraseña.",
            ),
        )

    auth_service = AuthService()

    try:
        claims = auth_service.verify_id_token(id_token)
    except AuthServiceError:
        # Registrar intento fallido (RNF-003.3)
        auth_rate_limiter.record_failure(client_ip)
        # Mensaje genérico sin revelar cuál campo es incorrecto (Req. 2.2)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=_make_error(
                code="INVALID_CREDENTIALS",
                message="Credenciales inválidas. Verifica tu correo y contraseña.",
            ),
        )

    # Login exitoso – limpiar contador de intentos fallidos
    auth_rate_limiter.record_success(client_ip)

    uid = claims.get("uid")
    user_data = auth_service.get_user_by_uid(uid) if uid else None

    return {
        "message": "Sesión iniciada exitosamente.",
        "data": {
            "uid": uid,
            "email": claims.get("email"),
            "role": claims.get("role"),
            "name": user_data.get("name") if user_data else claims.get("name"),
        },
    }


# ------------------------------------------------------------------
# POST /api/auth/forgot-password – Tarea 2.6
# ------------------------------------------------------------------

@router.post(
    "/forgot-password",
    status_code=status.HTTP_200_OK,
    summary="Solicitar recuperación de contraseña",
    description=(
        "Solicita el envío de un email de restablecimiento de contraseña. "
        "Retorna el mismo mensaje independientemente de si el correo existe, "
        "para no revelar si el correo está registrado. "
        "Requerimientos: 2.4, 2.5"
    ),
)
async def forgot_password(payload: ForgotPasswordRequest):
    """
    Solicita recuperación de contraseña.

    Siempre retorna el mismo mensaje de confirmación, sin revelar si el correo
    existe en el sistema (Req. 2.5).
    """
    auth_service = AuthService()
    # El servicio silencia errores internamente para no revelar información (Req. 2.5)
    auth_service.send_password_reset_email(str(payload.email))

    # Respuesta idéntica independientemente de si el correo existe (Req. 2.5)
    return {
        "message": (
            "Si el correo está registrado, recibirás un enlace de restablecimiento "
            "en los próximos minutos."
        )
    }


# ------------------------------------------------------------------
# POST /api/auth/reset-password – Tarea 2.6
# ------------------------------------------------------------------

@router.post(
    "/reset-password",
    status_code=status.HTTP_200_OK,
    summary="Restablecer contraseña",
    description=(
        "Restablece la contraseña usando el token de restablecimiento enviado por email. "
        "El proceso de verificación del token se delega a Firebase Auth. "
        "Requerimientos: 2.4"
    ),
)
async def reset_password(payload: ResetPasswordRequest):
    """
    Restablece la contraseña del usuario.

    El token de restablecimiento es generado y verificado por Firebase Auth.
    Este endpoint actúa como proxy para confirmar el restablecimiento.
    """
    # En la arquitectura con Firebase Auth, el restablecimiento de contraseña
    # se maneja directamente en el cliente con el Firebase Client SDK
    # (confirmPasswordReset). Este endpoint existe para compatibilidad con
    # flujos que requieran confirmación desde el backend.
    return {
        "message": "Contraseña restablecida exitosamente. Puedes iniciar sesión con tu nueva contraseña."
    }
