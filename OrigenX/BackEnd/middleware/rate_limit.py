"""
middleware/rate_limit.py – Rate limiting para el endpoint de autenticación.

Tarea 2.4 – Bloquear IP tras 5 intentos fallidos consecutivos (RNF-003.3).

Implementación en memoria (adecuada para desarrollo y despliegues de instancia única).
Para producción con múltiples instancias, reemplazar con Redis.
"""

import logging
import os
import time
from collections import defaultdict
from threading import Lock
from typing import Dict, Tuple

from fastapi import HTTPException, Request, status

logger = logging.getLogger(__name__)

# Configuración desde variables de entorno
MAX_FAILED_ATTEMPTS = int(os.getenv("AUTH_MAX_FAILED_ATTEMPTS", "5"))
LOCKOUT_SECONDS = int(os.getenv("AUTH_LOCKOUT_MINUTES", "15")) * 60


class RateLimiter:
    """
    Rate limiter en memoria para el endpoint de autenticación.

    Rastrea intentos fallidos por IP y bloquea temporalmente tras superar el límite.
    Thread-safe mediante Lock.
    """

    def __init__(
        self,
        max_attempts: int = MAX_FAILED_ATTEMPTS,
        lockout_seconds: int = LOCKOUT_SECONDS,
    ):
        self._max_attempts = max_attempts
        self._lockout_seconds = lockout_seconds
        # {ip: (failed_count, lockout_until_timestamp)}
        self._records: Dict[str, Tuple[int, float]] = defaultdict(lambda: (0, 0.0))
        self._lock = Lock()

    def check_and_raise(self, ip: str) -> None:
        """
        Verifica si la IP está bloqueada. Lanza HTTP 429 si lo está.

        Args:
            ip: Dirección IP del cliente.

        Raises:
            HTTPException 429: Si la IP está bloqueada por demasiados intentos fallidos.
        """
        with self._lock:
            failed_count, lockout_until = self._records[ip]

            if lockout_until > time.time():
                remaining = int(lockout_until - time.time())
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail={
                        "error": {
                            "code": "TOO_MANY_REQUESTS",
                            "message": (
                                f"Demasiados intentos fallidos. "
                                f"Intenta nuevamente en {remaining} segundos."
                            ),
                        }
                    },
                    headers={"Retry-After": str(remaining)},
                )

    def record_failure(self, ip: str) -> None:
        """
        Registra un intento fallido para la IP. Activa el bloqueo si se supera el límite.

        Args:
            ip: Dirección IP del cliente.
        """
        with self._lock:
            failed_count, lockout_until = self._records[ip]

            # Si el bloqueo anterior ya expiró, reiniciar contador
            if lockout_until > 0 and lockout_until <= time.time():
                failed_count = 0
                lockout_until = 0.0

            failed_count += 1

            if failed_count >= self._max_attempts:
                lockout_until = time.time() + self._lockout_seconds
                logger.warning(
                    "IP %s blocked after %d failed login attempts. Lockout until %s",
                    ip,
                    failed_count,
                    lockout_until,
                )
            self._records[ip] = (failed_count, lockout_until)

    def record_success(self, ip: str) -> None:
        """
        Limpia el registro de intentos fallidos tras un login exitoso.

        Args:
            ip: Dirección IP del cliente.
        """
        with self._lock:
            self._records[ip] = (0, 0.0)


def get_client_ip(request: Request) -> str:
    """
    Extrae la IP real del cliente, considerando proxies (X-Forwarded-For).

    Args:
        request: Objeto Request de FastAPI.

    Returns:
        Dirección IP del cliente como string.
    """
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        # Tomar la primera IP de la cadena (IP original del cliente)
        return forwarded_for.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


# Instancia global del rate limiter (singleton)
auth_rate_limiter = RateLimiter()
