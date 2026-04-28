"""
services/producer_service.py – Lógica de negocio del perfil de productor.

Responsabilidades:
  - Obtener perfil de productor (GET)
  - Crear/actualizar perfil de productor (PUT)
  - Validar campo obligatorio farmName (Req. 4.3)
  - Verificar que solo el dueño pueda actualizar su perfil (Req. 4.2)

Requerimientos: 4.1, 4.2, 4.3, 4.4
"""

import logging
from typing import Optional

from repositories.producer_repository import ProducerRepository, ProducerRepositoryError

logger = logging.getLogger(__name__)


class ProducerServiceError(Exception):
    """Error base del servicio de productores."""

    def __init__(self, message: str, code: str = "PRODUCER_SERVICE_ERROR"):
        self.message = message
        self.code = code
        super().__init__(message)


class ProducerNotFoundError(ProducerServiceError):
    """El perfil de productor no existe."""

    def __init__(self, user_id: str):
        super().__init__(
            message=f"Perfil de productor para el usuario '{user_id}' no encontrado.",
            code="PRODUCER_NOT_FOUND",
        )


class ProducerForbiddenError(ProducerServiceError):
    """El usuario autenticado no es el dueño del perfil (Req. 4.2)."""

    def __init__(self):
        super().__init__(
            message="No tienes permiso para modificar este perfil.",
            code="FORBIDDEN",
        )


class ProducerValidationError(ProducerServiceError):
    """Error de validación de campos del perfil (Req. 4.3)."""

    def __init__(self, message: str, fields: Optional[list] = None):
        super().__init__(message=message, code="VALIDATION_ERROR")
        self.fields = fields or []


class ProducerService:
    """Servicio de gestión del perfil de productor."""

    def __init__(self, repository: Optional[ProducerRepository] = None):
        self._repo = repository or ProducerRepository()

    def get_profile(self, producer_id: str) -> dict:
        """
        Obtiene el perfil público de un productor.

        Args:
            producer_id: UID del productor cuyo perfil se quiere obtener.

        Returns:
            Diccionario con los datos del perfil.

        Raises:
            ProducerNotFoundError: Si el perfil no existe.
        """
        try:
            profile = self._repo.get_by_user_id(producer_id)
        except ProducerRepositoryError as exc:
            raise ProducerServiceError(exc.message, exc.code) from exc

        if profile is None:
            raise ProducerNotFoundError(producer_id)

        return profile

    def update_profile(
        self,
        producer_id: str,
        requesting_user_id: str,
        farm_name: str,
        region: str,
        description: str,
        whatsapp: str,
        show_register_email: bool = True,
        alt_email: Optional[str] = None,
        show_alt_email: bool = False,
        images: Optional[list] = None,
    ) -> dict:
        """
        Crea o actualiza el perfil de un productor.

        Reglas de negocio:
          - Solo el productor dueño puede actualizar su propio perfil (Req. 4.2).
          - farmName es obligatorio (Req. 4.3).
          - Los cambios se reflejan en el catálogo en ≤ 5 s (Req. 4.2) — garantizado
            por escritura directa en Firestore.

        Args:
            producer_id: UID del productor cuyo perfil se actualiza.
            requesting_user_id: UID del usuario autenticado que hace la solicitud.
            farm_name: Nombre de la finca (obligatorio).
            region: Región del productor — Huila, Nariño o Antioquia (obligatorio).
            description: Descripción enriquecida en HTML (obligatorio).
            whatsapp: Número de WhatsApp (obligatorio).
            show_register_email: Si mostrar el correo de registro en el perfil público.
            alt_email: Correo alternativo (opcional).
            show_alt_email: Si mostrar el correo alternativo en el perfil público.
            images: Lista de URLs de imágenes en Firebase Storage (máx. 6, opcional).
        """
        from models.producer import VALID_REGIONS

        if producer_id != requesting_user_id:
            raise ProducerForbiddenError()

        validation_errors = []

        if not farm_name or not farm_name.strip():
            validation_errors.append({"field": "farm_name", "message": "El nombre de finca es obligatorio."})

        if not region or region not in VALID_REGIONS:
            validation_errors.append({"field": "region", "message": "La región debe ser Huila, Nariño o Antioquia."})

        if not description or not description.strip():
            validation_errors.append({"field": "description", "message": "La descripción es obligatoria."})

        if not whatsapp or not whatsapp.strip():
            validation_errors.append({"field": "whatsapp", "message": "El número de WhatsApp es obligatorio."})

        # No puede ocultar el correo de registro si no tiene correo alternativo
        if not show_register_email and not alt_email:
            validation_errors.append({"field": "show_register_email", "message": "Debes tener un correo alternativo para ocultar el correo de registro."})

        if images and len(images) > 6:
            validation_errors.append({"field": "images", "message": "Se permiten máximo 6 imágenes."})

        if validation_errors:
            raise ProducerValidationError(
                message="Hay errores de validación en el perfil.",
                fields=validation_errors,
            )

        fields = {
            "farmName":          farm_name.strip(),
            "region":            region,
            "description":       description.strip(),
            "whatsapp":          whatsapp.strip(),
            "showRegisterEmail": show_register_email,
            "altEmail":          alt_email.strip() if alt_email else None,
            "showAltEmail":      show_alt_email,
            "images":            images or [],
        }
        fields = {k: v for k, v in fields.items() if v is not None or k in ("showRegisterEmail", "showAltEmail", "altEmail")}

        try:
            saved = self._repo.upsert(producer_id, fields)
        except ProducerRepositoryError as exc:
            raise ProducerServiceError(exc.message, exc.code) from exc

        # Propagar el nuevo farmName a todos los productos del productor
        try:
            from repositories.product_repository import ProductRepository
            ProductRepository().update_producer_name(producer_id, farm_name.strip())
        except Exception as exc:
            # No bloqueamos el guardado del perfil si falla la propagación
            logger.warning("No se pudo propagar farmName a productos de '%s': %s", producer_id, exc)

        return saved

    def set_visibility(self, producer_id: str, requesting_user_id: str, is_active: bool) -> dict:
        """
        Activa o desactiva la visibilidad del perfil en el catálogo de productores.

        Solo se puede activar si el perfil tiene todos los datos obligatorios completos
        (farmName, region, description, whatsapp, al menos 1 imagen).

        Raises:
            ProducerForbiddenError: Si el usuario no es el dueño.
            ProducerNotFoundError: Si el perfil no existe.
            ProducerValidationError: Si intenta activar sin datos obligatorios completos.
        """
        if producer_id != requesting_user_id:
            raise ProducerForbiddenError()

        try:
            profile = self._repo.get_by_user_id(producer_id)
        except ProducerRepositoryError as exc:
            raise ProducerServiceError(exc.message, exc.code) from exc

        if profile is None:
            raise ProducerNotFoundError(producer_id)

        if is_active:
            missing = []
            if not profile.get("farmName", "").strip():
                missing.append("Nombre de la finca")
            if not profile.get("region"):
                missing.append("Región")
            if not profile.get("description", "").strip():
                missing.append("Descripción")
            if not profile.get("whatsapp", "").strip():
                missing.append("WhatsApp")
            if not profile.get("images"):
                missing.append("Al menos una imagen")
            if missing:
                raise ProducerValidationError(
                    message=f"Completa los campos obligatorios antes de activar tu perfil: {', '.join(missing)}.",
                    fields=[{"field": f, "message": "Requerido"} for f in missing],
                )

        try:
            return self._repo.set_visibility(producer_id, is_active)
        except ProducerRepositoryError as exc:
            raise ProducerServiceError(exc.message, exc.code) from exc

    def list_all(self) -> list[dict]:
        """
        Retorna todos los perfiles de productor activos con farmName definido.
        """
        try:
            return self._repo.list_all()
        except ProducerRepositoryError as exc:
            raise ProducerServiceError(exc.message, exc.code) from exc
