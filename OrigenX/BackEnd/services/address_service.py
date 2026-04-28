"""
services/address_service.py – Lógica de negocio para direcciones de envío.

Responsabilidades:
  - Listar direcciones del consumidor (Req. 18.4)
  - Crear dirección con validación de campos obligatorios (Req. 18.1, 18.2)
  - Limitar a 5 direcciones por usuario (Req. 18.3)
  - Eliminar dirección del consumidor

Requerimientos: 18.1, 18.2, 18.3, 18.4
"""

import logging
from datetime import datetime, timezone
from typing import Optional

from repositories.address_repository import (
    AddressNotFoundError,
    AddressRepository,
    AddressRepositoryError,
    MAX_ADDRESSES_PER_USER,
)

logger = logging.getLogger(__name__)


class AddressServiceError(Exception):
    """Error base del servicio de direcciones."""

    def __init__(self, message: str, code: str = "ADDRESS_SERVICE_ERROR"):
        self.message = message
        self.code = code
        super().__init__(message)


class AddressNotFoundServiceError(AddressServiceError):
    """La dirección no existe o no pertenece al usuario."""

    def __init__(self, address_id: str):
        super().__init__(
            message=f"Dirección con id '{address_id}' no encontrada.",
            code="ADDRESS_NOT_FOUND",
        )


class AddressLimitExceededError(AddressServiceError):
    """El usuario ya tiene el máximo de direcciones permitidas (Req. 18.3)."""

    def __init__(self):
        super().__init__(
            message=(
                f"Has alcanzado el límite máximo de {MAX_ADDRESSES_PER_USER} "
                "direcciones de envío. Elimina una dirección antes de agregar otra."
            ),
            code="ADDRESS_LIMIT_EXCEEDED",
        )


def _serialize_address(data: dict) -> dict:
    """Convierte los campos de Firestore al formato de respuesta de la API."""
    created_at = data.get("createdAt")
    if isinstance(created_at, datetime):
        created_at = created_at.isoformat()

    return {
        "id": data.get("id"),
        "user_id": data.get("userId"),
        "street": data.get("street"),
        "city": data.get("city"),
        "department": data.get("department"),
        "postal_code": data.get("postalCode"),
        "created_at": created_at,
    }


class AddressService:
    """Servicio de gestión de direcciones de envío."""

    def __init__(self, address_repository: Optional[AddressRepository] = None):
        self._address_repo = address_repository or AddressRepository()

    # ------------------------------------------------------------------
    # GET /api/addresses – Listar direcciones (Req. 18.4)
    # ------------------------------------------------------------------

    def list_addresses(self, user_id: str) -> list[dict]:
        """
        Retorna todas las direcciones de envío del consumidor.

        Args:
            user_id: UID del consumidor autenticado.

        Returns:
            Lista de diccionarios con los datos de cada dirección.

        Raises:
            AddressServiceError: Si ocurre un error al acceder al repositorio.
        """
        try:
            addresses = self._address_repo.get_by_user(user_id)
        except AddressRepositoryError as exc:
            raise AddressServiceError(exc.message, exc.code) from exc

        return [_serialize_address(addr) for addr in addresses]

    # ------------------------------------------------------------------
    # POST /api/addresses – Crear dirección (Req. 18.1, 18.2, 18.3)
    # ------------------------------------------------------------------

    def create_address(
        self,
        user_id: str,
        street: str,
        city: str,
        department: str,
        postal_code: Optional[str] = None,
    ) -> dict:
        """
        Crea una nueva dirección de envío para el consumidor.

        Reglas de negocio:
          - street, city y department son obligatorios (Req. 18.2).
          - El usuario no puede tener más de 5 direcciones (Req. 18.3).
          - Persiste la dirección en Firestore asociada al userId (Req. 18.1).

        Args:
            user_id: UID del consumidor.
            street: Calle (obligatorio).
            city: Ciudad (obligatorio).
            department: Departamento (obligatorio).
            postal_code: Código postal (opcional).

        Returns:
            Diccionario con los datos de la dirección creada.

        Raises:
            AddressLimitExceededError: Si el usuario ya tiene 5 direcciones (Req. 18.3).
            AddressServiceError: Si ocurre un error al acceder al repositorio.
        """
        # Verificar límite de 5 direcciones (Req. 18.3)
        try:
            count = self._address_repo.count_by_user(user_id)
        except AddressRepositoryError as exc:
            raise AddressServiceError(exc.message, exc.code) from exc

        if count >= MAX_ADDRESSES_PER_USER:
            raise AddressLimitExceededError()

        # Crear la dirección en Firestore (Req. 18.1)
        try:
            address = self._address_repo.create(
                user_id=user_id,
                street=street,
                city=city,
                department=department,
                postal_code=postal_code,
            )
        except AddressRepositoryError as exc:
            raise AddressServiceError(exc.message, exc.code) from exc

        return _serialize_address(address)

    # ------------------------------------------------------------------
    # DELETE /api/addresses/:id – Eliminar dirección
    # ------------------------------------------------------------------

    def delete_address(self, user_id: str, address_id: str) -> None:
        """
        Elimina una dirección de envío del consumidor.

        Args:
            user_id: UID del consumidor autenticado.
            address_id: ID de la dirección a eliminar.

        Raises:
            AddressNotFoundServiceError: Si la dirección no existe o no pertenece al usuario.
            AddressServiceError: Si ocurre un error al acceder al repositorio.
        """
        try:
            self._address_repo.delete(address_id=address_id, user_id=user_id)
        except AddressNotFoundError as exc:
            raise AddressNotFoundServiceError(address_id) from exc
        except AddressRepositoryError as exc:
            raise AddressServiceError(exc.message, exc.code) from exc
