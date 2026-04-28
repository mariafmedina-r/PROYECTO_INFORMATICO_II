"""
middleware/auth_middleware.py – Middleware de autenticación y autorización por roles (RBAC).

Tarea 2.7 – Implementar middleware de autorización por roles.

Responsabilidades:
  - Verificar el Firebase ID Token en cada solicitud protegida.
  - Leer el Custom Claim de rol del token.
  - Retornar HTTP 401 si el token es ausente o inválido.
  - Retornar HTTP 403 si el rol no tiene permiso.

Requerimientos: 3.1, 3.2, 3.3, 3.4, 3.5
"""

import logging
from functools import wraps
from typing import List, Optional

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from models.user import UserRole
from services.auth_service import AuthService, AuthServiceError

logger = logging.getLogger(__name__)

# Esquema de seguridad Bearer Token
_bearer_scheme = HTTPBearer(auto_error=False)


def _get_auth_service() -> AuthService:
    """Dependency factory para AuthService."""
    return AuthService()


async def get_current_user(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(_bearer_scheme),
    auth_service: AuthService = Depends(_get_auth_service),
) -> dict:
    """
    Dependencia FastAPI que verifica el Firebase ID Token y retorna los claims.

    Retorna HTTP 401 si el token es ausente o inválido (Req. 3.4).

    Returns:
        Diccionario con los claims del token decodificado:
        {
            "uid": "...",
            "email": "...",
            "role": "CONSUMER" | "PRODUCER" | "ADMIN",
            ...
        }
    """
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error": {
                    "code": "MISSING_TOKEN",
                    "message": "Se requiere autenticación. Incluye el token en el header Authorization.",
                }
            },
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        claims = auth_service.verify_id_token(credentials.credentials)
    except AuthServiceError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error": {
                    "code": exc.code,
                    "message": exc.message,
                }
            },
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc

    # Adjuntar claims al request state para uso posterior
    request.state.user = claims
    return claims


def require_roles(*allowed_roles: UserRole):
    """
    Dependencia FastAPI que verifica que el usuario autenticado tenga uno de los roles permitidos.

    Retorna HTTP 403 si el rol no tiene permiso (Req. 3.2, 3.3).

    Args:
        *allowed_roles: Roles que tienen acceso al endpoint.

    Usage:
        @router.get("/admin-only")
        async def admin_endpoint(
            current_user: dict = Depends(require_roles(UserRole.ADMIN))
        ):
            ...
    """
    async def _check_role(
        current_user: dict = Depends(get_current_user),
    ) -> dict:
        user_role = current_user.get("role")

        if user_role not in [r.value for r in allowed_roles]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "error": {
                        "code": "FORBIDDEN",
                        "message": "No tienes permiso para acceder a este recurso.",
                    }
                },
            )
        return current_user

    return _check_role


# Dependencias de conveniencia para cada rol
require_consumer = require_roles(UserRole.CONSUMER)
require_producer = require_roles(UserRole.PRODUCER)
require_admin = require_roles(UserRole.ADMIN)
require_producer_or_admin = require_roles(UserRole.PRODUCER, UserRole.ADMIN)
require_any_authenticated = require_roles(UserRole.CONSUMER, UserRole.PRODUCER, UserRole.ADMIN)
