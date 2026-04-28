"""
test_producer_service.py – Tests unitarios para ProducerService.

Verifica la lógica de negocio del perfil de productor.

Requerimientos: 4.1, 4.2, 4.3, 4.4
"""

from unittest.mock import MagicMock

import pytest

from services.producer_service import (
    ProducerService,
    ProducerServiceError,
    ProducerNotFoundError,
    ProducerForbiddenError,
    ProducerValidationError,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_profile(
    producer_id="producer-123",
    farm_name="Finca El Paraíso",
    region="Huila",
    description="Café de altura",
    contact_info="contacto@finca.com",
):
    return {
        "id": producer_id,
        "userId": producer_id,
        "farmName": farm_name,
        "region": region,
        "description": description,
        "contactInfo": contact_info,
    }


def _make_service(mock_repo):
    return ProducerService(repository=mock_repo)


# ---------------------------------------------------------------------------
# Tests – get_profile (Req. 4.1, 4.4)
# ---------------------------------------------------------------------------

class TestGetProfile:
    """Tests del método get_profile (Req. 4.1)."""

    def test_returns_profile_for_existing_producer(self):
        """Debe retornar el perfil del productor existente."""
        mock_repo = MagicMock()
        mock_repo.get_by_user_id.return_value = _make_profile()

        service = _make_service(mock_repo)
        result = service.get_profile("producer-123")

        assert result["farmName"] == "Finca El Paraíso"
        assert result["region"] == "Huila"
        mock_repo.get_by_user_id.assert_called_once_with("producer-123")

    def test_raises_not_found_for_nonexistent_producer(self):
        """Debe lanzar ProducerNotFoundError si el perfil no existe."""
        mock_repo = MagicMock()
        mock_repo.get_by_user_id.return_value = None

        service = _make_service(mock_repo)

        with pytest.raises(ProducerNotFoundError) as exc_info:
            service.get_profile("nonexistent-producer")

        assert exc_info.value.code == "PRODUCER_NOT_FOUND"

    def test_raises_service_error_on_repository_failure(self):
        """Debe lanzar ProducerServiceError si el repositorio falla."""
        from repositories.producer_repository import ProducerRepositoryError

        mock_repo = MagicMock()
        mock_repo.get_by_user_id.side_effect = ProducerRepositoryError(
            "Firestore error", "FIRESTORE_READ_ERROR"
        )

        service = _make_service(mock_repo)

        with pytest.raises(ProducerServiceError) as exc_info:
            service.get_profile("producer-123")

        assert exc_info.value.code == "FIRESTORE_READ_ERROR"

    def test_profile_includes_all_fields(self):
        """El perfil debe incluir todos los campos del productor (Req. 4.1)."""
        mock_repo = MagicMock()
        mock_repo.get_by_user_id.return_value = _make_profile(
            farm_name="Finca La Esperanza",
            region="Nariño",
            description="Café orgánico",
            contact_info="info@finca.com",
        )

        service = _make_service(mock_repo)
        result = service.get_profile("producer-123")

        assert result["farmName"] == "Finca La Esperanza"
        assert result["region"] == "Nariño"
        assert result["description"] == "Café orgánico"
        assert result["contactInfo"] == "info@finca.com"


# ---------------------------------------------------------------------------
# Tests – update_profile (Req. 4.2, 4.3)
# ---------------------------------------------------------------------------

class TestUpdateProfile:
    """Tests del método update_profile (Req. 4.2, 4.3)."""

    def test_owner_can_update_profile(self):
        """El productor dueño puede actualizar su propio perfil (Req. 4.2)."""
        mock_repo = MagicMock()
        mock_repo.upsert.return_value = _make_profile(farm_name="Finca Nueva")

        service = _make_service(mock_repo)
        result = service.update_profile(
            producer_id="producer-123",
            requesting_user_id="producer-123",
            farm_name="Finca Nueva",
            region="Huila",
        )

        assert result["farmName"] == "Finca Nueva"
        mock_repo.upsert.assert_called_once()

    def test_non_owner_raises_forbidden(self):
        """Otro usuario no puede actualizar el perfil (Req. 4.2)."""
        mock_repo = MagicMock()

        service = _make_service(mock_repo)

        with pytest.raises(ProducerForbiddenError) as exc_info:
            service.update_profile(
                producer_id="producer-123",
                requesting_user_id="other-user-456",
                farm_name="Finca Ajena",
            )

        assert exc_info.value.code == "FORBIDDEN"
        mock_repo.upsert.assert_not_called()

    def test_empty_farm_name_raises_validation_error(self):
        """farmName vacío debe lanzar ProducerValidationError (Req. 4.3)."""
        mock_repo = MagicMock()

        service = _make_service(mock_repo)

        with pytest.raises(ProducerValidationError) as exc_info:
            service.update_profile(
                producer_id="producer-123",
                requesting_user_id="producer-123",
                farm_name="",
            )

        assert exc_info.value.code == "VALIDATION_ERROR"
        fields = [f["field"] for f in exc_info.value.fields]
        assert "farm_name" in fields

    def test_whitespace_only_farm_name_raises_validation_error(self):
        """farmName con solo espacios debe lanzar ProducerValidationError (Req. 4.3)."""
        mock_repo = MagicMock()

        service = _make_service(mock_repo)

        with pytest.raises(ProducerValidationError):
            service.update_profile(
                producer_id="producer-123",
                requesting_user_id="producer-123",
                farm_name="   ",
            )

    def test_farm_name_is_stripped(self):
        """El farmName debe guardarse sin espacios extra."""
        mock_repo = MagicMock()
        mock_repo.upsert.return_value = _make_profile(farm_name="Finca El Paraíso")

        service = _make_service(mock_repo)
        service.update_profile(
            producer_id="producer-123",
            requesting_user_id="producer-123",
            farm_name="  Finca El Paraíso  ",
        )

        call_args = mock_repo.upsert.call_args
        fields = call_args[0][1]
        assert fields["farmName"] == "Finca El Paraíso"

    def test_optional_fields_included_when_provided(self):
        """Los campos opcionales se incluyen cuando se proporcionan."""
        mock_repo = MagicMock()
        mock_repo.upsert.return_value = _make_profile()

        service = _make_service(mock_repo)
        service.update_profile(
            producer_id="producer-123",
            requesting_user_id="producer-123",
            farm_name="Finca El Paraíso",
            region="Huila",
            description="Café de altura",
            contact_info="contacto@finca.com",
        )

        call_args = mock_repo.upsert.call_args
        fields = call_args[0][1]
        assert fields["farmName"] == "Finca El Paraíso"
        assert fields["region"] == "Huila"
        assert fields["description"] == "Café de altura"
        assert fields["contactInfo"] == "contacto@finca.com"

    def test_none_optional_fields_excluded(self):
        """Los campos opcionales con valor None no se incluyen en la actualización."""
        mock_repo = MagicMock()
        mock_repo.upsert.return_value = _make_profile()

        service = _make_service(mock_repo)
        service.update_profile(
            producer_id="producer-123",
            requesting_user_id="producer-123",
            farm_name="Finca El Paraíso",
            region=None,
            description=None,
            contact_info=None,
        )

        call_args = mock_repo.upsert.call_args
        fields = call_args[0][1]
        assert "region" not in fields
        assert "description" not in fields
        assert "contactInfo" not in fields

    def test_repository_error_raises_service_error(self):
        """Error del repositorio debe lanzar ProducerServiceError."""
        from repositories.producer_repository import ProducerRepositoryError

        mock_repo = MagicMock()
        mock_repo.upsert.side_effect = ProducerRepositoryError(
            "Firestore error", "FIRESTORE_WRITE_ERROR"
        )

        service = _make_service(mock_repo)

        with pytest.raises(ProducerServiceError) as exc_info:
            service.update_profile(
                producer_id="producer-123",
                requesting_user_id="producer-123",
                farm_name="Finca El Paraíso",
            )

        assert exc_info.value.code == "FIRESTORE_WRITE_ERROR"

    def test_upsert_called_with_producer_id(self):
        """El repositorio debe ser llamado con el producer_id correcto."""
        mock_repo = MagicMock()
        mock_repo.upsert.return_value = _make_profile()

        service = _make_service(mock_repo)
        service.update_profile(
            producer_id="producer-123",
            requesting_user_id="producer-123",
            farm_name="Finca El Paraíso",
        )

        call_args = mock_repo.upsert.call_args
        assert call_args[0][0] == "producer-123"
