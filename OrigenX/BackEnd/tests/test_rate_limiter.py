"""
test_rate_limiter.py – Tests unitarios para el rate limiter de autenticación.

Verifica que el bloqueo por IP funcione correctamente tras 5 intentos fallidos.

Requerimientos: RNF-003.3
"""

import time
from unittest.mock import patch

import pytest
from fastapi import HTTPException

# Los mocks de Firebase se cargan en conftest.py
from middleware.rate_limit import RateLimiter, get_client_ip


class TestRateLimiter:
    """Tests del RateLimiter en memoria (Req. RNF-003.3)."""

    def setup_method(self):
        """Crear una instancia fresca del rate limiter para cada test."""
        self.limiter = RateLimiter(max_attempts=5, lockout_seconds=900)

    def test_no_block_before_limit(self):
        """No debe bloquear antes de alcanzar el límite de intentos."""
        ip = "192.168.1.1"
        for _ in range(4):
            self.limiter.record_failure(ip)
        # No debe lanzar excepción
        self.limiter.check_and_raise(ip)

    def test_blocks_after_max_attempts(self):
        """Debe bloquear la IP tras alcanzar el límite de intentos fallidos (Req. RNF-003.3)."""
        ip = "192.168.1.2"
        for _ in range(5):
            self.limiter.record_failure(ip)
        with pytest.raises(HTTPException) as exc_info:
            self.limiter.check_and_raise(ip)
        assert exc_info.value.status_code == 429

    def test_block_returns_429_status(self):
        """El bloqueo debe retornar HTTP 429 (Req. RNF-003.3)."""
        ip = "192.168.1.3"
        for _ in range(5):
            self.limiter.record_failure(ip)
        with pytest.raises(HTTPException) as exc_info:
            self.limiter.check_and_raise(ip)
        assert exc_info.value.status_code == 429

    def test_block_error_code_in_detail(self):
        """El detalle del error debe incluir el código TOO_MANY_REQUESTS."""
        ip = "192.168.1.4"
        for _ in range(5):
            self.limiter.record_failure(ip)
        with pytest.raises(HTTPException) as exc_info:
            self.limiter.check_and_raise(ip)
        detail = exc_info.value.detail
        assert detail["error"]["code"] == "TOO_MANY_REQUESTS"

    def test_success_clears_failure_count(self):
        """Un login exitoso debe limpiar el contador de intentos fallidos."""
        ip = "192.168.1.5"
        for _ in range(4):
            self.limiter.record_failure(ip)
        self.limiter.record_success(ip)
        # Después del éxito, 4 nuevos fallos no deben bloquear
        for _ in range(4):
            self.limiter.record_failure(ip)
        # No debe lanzar excepción
        self.limiter.check_and_raise(ip)

    def test_different_ips_are_independent(self):
        """El bloqueo de una IP no debe afectar a otras IPs."""
        ip_blocked = "10.0.0.1"
        ip_clean = "10.0.0.2"
        for _ in range(5):
            self.limiter.record_failure(ip_blocked)
        # ip_blocked debe estar bloqueada
        with pytest.raises(HTTPException):
            self.limiter.check_and_raise(ip_blocked)
        # ip_clean no debe estar bloqueada
        self.limiter.check_and_raise(ip_clean)

    def test_new_ip_is_not_blocked(self):
        """Una IP nueva no debe estar bloqueada."""
        ip = "172.16.0.1"
        # No debe lanzar excepción
        self.limiter.check_and_raise(ip)

    def test_lockout_expires_after_time(self):
        """El bloqueo debe expirar después del tiempo configurado."""
        limiter = RateLimiter(max_attempts=5, lockout_seconds=1)
        ip = "192.168.2.1"
        for _ in range(5):
            limiter.record_failure(ip)
        # Verificar que está bloqueado
        with pytest.raises(HTTPException):
            limiter.check_and_raise(ip)
        # Esperar a que expire el bloqueo
        time.sleep(1.1)
        # Ahora no debe estar bloqueado
        limiter.check_and_raise(ip)

    def test_retry_after_header_present(self):
        """La respuesta de bloqueo debe incluir el header Retry-After."""
        ip = "192.168.1.6"
        for _ in range(5):
            self.limiter.record_failure(ip)
        with pytest.raises(HTTPException) as exc_info:
            self.limiter.check_and_raise(ip)
        assert "Retry-After" in exc_info.value.headers

    def test_exactly_5_failures_triggers_block(self):
        """Exactamente 5 fallos deben activar el bloqueo (no 4, sí 5)."""
        ip = "192.168.1.7"
        # 4 fallos: no bloqueado
        for _ in range(4):
            self.limiter.record_failure(ip)
        self.limiter.check_and_raise(ip)  # No debe lanzar
        # 5to fallo: bloqueado
        self.limiter.record_failure(ip)
        with pytest.raises(HTTPException):
            self.limiter.check_and_raise(ip)


class TestGetClientIp:
    """Tests de la función get_client_ip."""

    def test_returns_forwarded_for_ip(self):
        """Debe retornar la primera IP del header X-Forwarded-For."""
        from unittest.mock import MagicMock
        request = MagicMock()
        request.headers = {"X-Forwarded-For": "203.0.113.1, 10.0.0.1"}
        request.client = None
        ip = get_client_ip(request)
        assert ip == "203.0.113.1"

    def test_returns_client_host_without_forwarded_for(self):
        """Sin X-Forwarded-For, debe retornar request.client.host."""
        from unittest.mock import MagicMock
        request = MagicMock()
        request.headers = {}
        request.client.host = "192.168.1.100"
        ip = get_client_ip(request)
        assert ip == "192.168.1.100"

    def test_returns_unknown_without_client(self):
        """Sin cliente ni header, debe retornar 'unknown'."""
        from unittest.mock import MagicMock
        request = MagicMock()
        request.headers = {}
        request.client = None
        ip = get_client_ip(request)
        assert ip == "unknown"
