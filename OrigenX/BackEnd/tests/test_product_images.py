"""
test_product_images.py – Tests para los endpoints de gestión de imágenes de productos.

Endpoints cubiertos:
  POST   /api/products/:id/images         → Subir imagen (tarea 4.8)
  DELETE /api/products/:id/images/:imgId  → Eliminar imagen (tarea 4.8)

Cubre:
  - Subida exitosa de imagen JPG/PNG ≤ 5 MB (Req. 7.1)
  - Rechazo de formato inválido (Req. 7.2)
  - Rechazo de imagen > 5 MB (Req. 7.3)
  - Rechazo al superar el límite de 5 imágenes (Req. 7.4)
  - Eliminación exitosa sin afectar pedidos históricos (Req. 7.5)
  - Verificación de propiedad – HTTP 403 si no es dueño
  - Producto no encontrado – HTTP 404
  - Acceso sin token – HTTP 401
"""

from datetime import datetime, timezone
from io import BytesIO
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

# Los mocks de Firebase se cargan en conftest.py antes de importar la app
from main import app


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def client():
    """Cliente de prueba para la aplicación FastAPI."""
    return TestClient(app, raise_server_exceptions=False)


@pytest.fixture
def producer_claims():
    """Claims de un Productor autenticado (dueño del producto)."""
    return {
        "uid": "producer-uid-123",
        "email": "producer@example.com",
        "role": "PRODUCER",
    }


@pytest.fixture
def other_producer_claims():
    """Claims de otro Productor (no dueño del producto)."""
    return {
        "uid": "other-producer-uid-456",
        "email": "other@example.com",
        "role": "PRODUCER",
    }


@pytest.fixture
def existing_product():
    """Datos de un producto existente en Firestore."""
    return {
        "id": "product-abc",
        "producerId": "producer-uid-123",
        "producerName": "Finca El Paraíso",
        "name": "Café Especial",
        "description": "Café de altura",
        "price": 25000.0,
        "status": "active",
        "createdAt": datetime(2024, 1, 1, tzinfo=timezone.utc),
        "updatedAt": datetime(2024, 1, 1, tzinfo=timezone.utc),
    }


@pytest.fixture
def created_image():
    """Datos de una imagen recién creada."""
    return {
        "id": "image-xyz",
        "url": "https://storage.googleapis.com/bucket/products/product-abc/images/image-xyz.jpg",
        "storagePath": "products/product-abc/images/image-xyz.jpg",
        "sortOrder": 0,
        "createdAt": datetime(2024, 6, 1, tzinfo=timezone.utc),
    }


def _make_jpeg_file(size_bytes: int = 1024) -> bytes:
    """Genera contenido binario simulando un JPEG pequeño."""
    # Cabecera JPEG mínima + relleno
    return b"\xff\xd8\xff\xe0" + b"\x00" * (size_bytes - 4)


def _make_png_file(size_bytes: int = 1024) -> bytes:
    """Genera contenido binario simulando un PNG pequeño."""
    # Firma PNG + relleno
    return b"\x89PNG\r\n\x1a\n" + b"\x00" * (size_bytes - 8)


# ---------------------------------------------------------------------------
# Tests de integración – POST /api/products/:id/images
# ---------------------------------------------------------------------------

class TestUploadProductImageEndpoint:
    """Tests del endpoint POST /api/products/:id/images (Req. 7.1–7.4)."""

    def test_upload_jpeg_returns_201(
        self, client, mock_firebase_auth, producer_claims, created_image
    ):
        """Subida exitosa de JPEG debe retornar HTTP 201 con datos de la imagen (Req. 7.1)."""
        mock_firebase_auth.verify_id_token.return_value = producer_claims

        with patch("routes.products.ProductService") as mock_service_cls:
            mock_service = MagicMock()
            mock_service_cls.return_value = mock_service
            mock_service.add_image.return_value = created_image

            response = client.post(
                "/api/products/product-abc/images",
                files={"file": ("photo.jpg", _make_jpeg_file(), "image/jpeg")},
                headers={"Authorization": "Bearer valid-producer-token"},
            )

        assert response.status_code == 201
        data = response.json()
        assert "message" in data
        assert "data" in data
        assert data["data"]["id"] == "image-xyz"
        assert "url" in data["data"]

    def test_upload_png_returns_201(
        self, client, mock_firebase_auth, producer_claims, created_image
    ):
        """Subida exitosa de PNG debe retornar HTTP 201 (Req. 7.1)."""
        mock_firebase_auth.verify_id_token.return_value = producer_claims

        with patch("routes.products.ProductService") as mock_service_cls:
            mock_service = MagicMock()
            mock_service_cls.return_value = mock_service
            mock_service.add_image.return_value = created_image

            response = client.post(
                "/api/products/product-abc/images",
                files={"file": ("photo.png", _make_png_file(), "image/png")},
                headers={"Authorization": "Bearer valid-producer-token"},
            )

        assert response.status_code == 201

    def test_invalid_format_returns_400(
        self, client, mock_firebase_auth, producer_claims
    ):
        """Formato inválido (GIF, PDF, etc.) debe retornar HTTP 400 (Req. 7.2)."""
        mock_firebase_auth.verify_id_token.return_value = producer_claims

        with patch("routes.products.ProductService") as mock_service_cls:
            from services.product_service import ProductValidationError
            mock_service = MagicMock()
            mock_service_cls.return_value = mock_service
            mock_service.add_image.side_effect = ProductValidationError(
                message="Formato de imagen no permitido. Solo se aceptan JPG y PNG.",
                fields=[{"field": "image", "message": "El archivo debe ser JPG o PNG."}],
            )

            response = client.post(
                "/api/products/product-abc/images",
                files={"file": ("photo.gif", b"GIF89a...", "image/gif")},
                headers={"Authorization": "Bearer valid-producer-token"},
            )

        assert response.status_code == 400
        data = response.json()
        assert data["detail"]["error"]["code"] == "VALIDATION_ERROR"

    def test_oversized_image_returns_400(
        self, client, mock_firebase_auth, producer_claims
    ):
        """Imagen > 5 MB debe retornar HTTP 400 (Req. 7.3)."""
        mock_firebase_auth.verify_id_token.return_value = producer_claims

        with patch("routes.products.ProductService") as mock_service_cls:
            from services.product_service import ProductValidationError
            mock_service = MagicMock()
            mock_service_cls.return_value = mock_service
            mock_service.add_image.side_effect = ProductValidationError(
                message="El archivo supera el tamaño máximo permitido de 5 MB.",
                fields=[{"field": "image", "message": "El archivo no puede superar 5 MB."}],
            )

            # Simular archivo de 6 MB
            big_file = b"\xff\xd8\xff\xe0" + b"\x00" * (6 * 1024 * 1024)
            response = client.post(
                "/api/products/product-abc/images",
                files={"file": ("big.jpg", big_file, "image/jpeg")},
                headers={"Authorization": "Bearer valid-producer-token"},
            )

        assert response.status_code == 400
        data = response.json()
        assert data["detail"]["error"]["code"] == "VALIDATION_ERROR"

    def test_image_limit_exceeded_returns_400(
        self, client, mock_firebase_auth, producer_claims
    ):
        """Superar el límite de 5 imágenes debe retornar HTTP 400 (Req. 7.4)."""
        mock_firebase_auth.verify_id_token.return_value = producer_claims

        with patch("routes.products.ProductService") as mock_service_cls:
            from services.product_service import ProductImageLimitError
            mock_service = MagicMock()
            mock_service_cls.return_value = mock_service
            mock_service.add_image.side_effect = ProductImageLimitError()

            response = client.post(
                "/api/products/product-abc/images",
                files={"file": ("photo.jpg", _make_jpeg_file(), "image/jpeg")},
                headers={"Authorization": "Bearer valid-producer-token"},
            )

        assert response.status_code == 400
        data = response.json()
        assert data["detail"]["error"]["code"] == "IMAGE_LIMIT_EXCEEDED"

    def test_non_owner_returns_403(
        self, client, mock_firebase_auth, other_producer_claims
    ):
        """Productor que no es dueño debe recibir HTTP 403."""
        mock_firebase_auth.verify_id_token.return_value = other_producer_claims

        with patch("routes.products.ProductService") as mock_service_cls:
            from services.product_service import ProductForbiddenError
            mock_service = MagicMock()
            mock_service_cls.return_value = mock_service
            mock_service.add_image.side_effect = ProductForbiddenError()

            response = client.post(
                "/api/products/product-abc/images",
                files={"file": ("photo.jpg", _make_jpeg_file(), "image/jpeg")},
                headers={"Authorization": "Bearer other-producer-token"},
            )

        assert response.status_code == 403
        data = response.json()
        assert data["detail"]["error"]["code"] == "FORBIDDEN"

    def test_product_not_found_returns_404(
        self, client, mock_firebase_auth, producer_claims
    ):
        """Producto inexistente debe retornar HTTP 404."""
        mock_firebase_auth.verify_id_token.return_value = producer_claims

        with patch("routes.products.ProductService") as mock_service_cls:
            from services.product_service import ProductNotFoundServiceError
            mock_service = MagicMock()
            mock_service_cls.return_value = mock_service
            mock_service.add_image.side_effect = ProductNotFoundServiceError("nonexistent-id")

            response = client.post(
                "/api/products/nonexistent-id/images",
                files={"file": ("photo.jpg", _make_jpeg_file(), "image/jpeg")},
                headers={"Authorization": "Bearer valid-producer-token"},
            )

        assert response.status_code == 404
        data = response.json()
        assert data["detail"]["error"]["code"] == "PRODUCT_NOT_FOUND"

    def test_missing_token_returns_401(self, client):
        """Solicitud sin token debe retornar HTTP 401."""
        response = client.post(
            "/api/products/product-abc/images",
            files={"file": ("photo.jpg", _make_jpeg_file(), "image/jpeg")},
        )
        assert response.status_code == 401

    def test_upload_calls_service_with_correct_args(
        self, client, mock_firebase_auth, producer_claims, created_image
    ):
        """El endpoint debe llamar al servicio con los argumentos correctos."""
        mock_firebase_auth.verify_id_token.return_value = producer_claims

        with patch("routes.products.ProductService") as mock_service_cls:
            mock_service = MagicMock()
            mock_service_cls.return_value = mock_service
            mock_service.add_image.return_value = created_image

            file_content = _make_jpeg_file(2048)
            client.post(
                "/api/products/product-abc/images",
                files={"file": ("photo.jpg", file_content, "image/jpeg")},
                headers={"Authorization": "Bearer valid-producer-token"},
            )

            call_kwargs = mock_service.add_image.call_args[1]
            assert call_kwargs["product_id"] == "product-abc"
            assert call_kwargs["producer_id"] == "producer-uid-123"
            assert call_kwargs["content_type"] == "image/jpeg"
            assert call_kwargs["filename"] == "photo.jpg"


# ---------------------------------------------------------------------------
# Tests de integración – DELETE /api/products/:id/images/:imgId
# ---------------------------------------------------------------------------

class TestDeleteProductImageEndpoint:
    """Tests del endpoint DELETE /api/products/:id/images/:imgId (Req. 7.5)."""

    def test_delete_image_returns_200(
        self, client, mock_firebase_auth, producer_claims
    ):
        """Eliminación exitosa debe retornar HTTP 200 (Req. 7.5)."""
        mock_firebase_auth.verify_id_token.return_value = producer_claims

        with patch("routes.products.ProductService") as mock_service_cls:
            mock_service = MagicMock()
            mock_service_cls.return_value = mock_service
            mock_service.delete_image.return_value = None  # void

            response = client.delete(
                "/api/products/product-abc/images/image-xyz",
                headers={"Authorization": "Bearer valid-producer-token"},
            )

        assert response.status_code == 200
        data = response.json()
        assert "message" in data

    def test_delete_calls_service_with_correct_args(
        self, client, mock_firebase_auth, producer_claims
    ):
        """El endpoint debe llamar al servicio con los argumentos correctos."""
        mock_firebase_auth.verify_id_token.return_value = producer_claims

        with patch("routes.products.ProductService") as mock_service_cls:
            mock_service = MagicMock()
            mock_service_cls.return_value = mock_service
            mock_service.delete_image.return_value = None

            client.delete(
                "/api/products/product-abc/images/image-xyz",
                headers={"Authorization": "Bearer valid-producer-token"},
            )

            mock_service.delete_image.assert_called_once_with(
                product_id="product-abc",
                image_id="image-xyz",
                producer_id="producer-uid-123",
            )

    def test_non_owner_returns_403(
        self, client, mock_firebase_auth, other_producer_claims
    ):
        """Productor que no es dueño debe recibir HTTP 403."""
        mock_firebase_auth.verify_id_token.return_value = other_producer_claims

        with patch("routes.products.ProductService") as mock_service_cls:
            from services.product_service import ProductForbiddenError
            mock_service = MagicMock()
            mock_service_cls.return_value = mock_service
            mock_service.delete_image.side_effect = ProductForbiddenError()

            response = client.delete(
                "/api/products/product-abc/images/image-xyz",
                headers={"Authorization": "Bearer other-producer-token"},
            )

        assert response.status_code == 403
        data = response.json()
        assert data["detail"]["error"]["code"] == "FORBIDDEN"

    def test_product_not_found_returns_404(
        self, client, mock_firebase_auth, producer_claims
    ):
        """Producto inexistente debe retornar HTTP 404."""
        mock_firebase_auth.verify_id_token.return_value = producer_claims

        with patch("routes.products.ProductService") as mock_service_cls:
            from services.product_service import ProductNotFoundServiceError
            mock_service = MagicMock()
            mock_service_cls.return_value = mock_service
            mock_service.delete_image.side_effect = ProductNotFoundServiceError("nonexistent-id")

            response = client.delete(
                "/api/products/nonexistent-id/images/image-xyz",
                headers={"Authorization": "Bearer valid-producer-token"},
            )

        assert response.status_code == 404

    def test_image_not_found_returns_404(
        self, client, mock_firebase_auth, producer_claims
    ):
        """Imagen inexistente debe retornar HTTP 404."""
        mock_firebase_auth.verify_id_token.return_value = producer_claims

        with patch("routes.products.ProductService") as mock_service_cls:
            from services.product_service import ProductImageNotFoundError
            mock_service = MagicMock()
            mock_service_cls.return_value = mock_service
            mock_service.delete_image.side_effect = ProductImageNotFoundError("nonexistent-img")

            response = client.delete(
                "/api/products/product-abc/images/nonexistent-img",
                headers={"Authorization": "Bearer valid-producer-token"},
            )

        assert response.status_code == 404
        data = response.json()
        assert data["detail"]["error"]["code"] == "IMAGE_NOT_FOUND"

    def test_missing_token_returns_401(self, client):
        """Solicitud sin token debe retornar HTTP 401."""
        response = client.delete(
            "/api/products/product-abc/images/image-xyz",
        )
        assert response.status_code == 401


# ---------------------------------------------------------------------------
# Tests unitarios – ProductService.add_image
# ---------------------------------------------------------------------------

class TestProductServiceAddImage:
    """Tests unitarios del método ProductService.add_image (Req. 7.1–7.4)."""

    def _make_service(self, mock_repo):
        from services.product_service import ProductService
        return ProductService(repository=mock_repo)

    def _make_product(self, producer_id="producer-uid-123"):
        return {
            "id": "product-abc",
            "producerId": producer_id,
            "name": "Café",
            "status": "active",
        }

    def test_invalid_content_type_raises_validation_error(self):
        """Formato inválido debe lanzar ProductValidationError (Req. 7.2)."""
        from services.product_service import ProductValidationError
        mock_repo = MagicMock()
        mock_repo.get_by_id.return_value = self._make_product()
        mock_repo.count_images.return_value = 0

        service = self._make_service(mock_repo)

        with pytest.raises(ProductValidationError) as exc_info:
            service.add_image(
                product_id="product-abc",
                producer_id="producer-uid-123",
                file_content=b"GIF89a...",
                content_type="image/gif",
                filename="photo.gif",
            )

        assert exc_info.value.code == "VALIDATION_ERROR"
        fields = [f["field"] for f in exc_info.value.fields]
        assert "image" in fields

    def test_invalid_extension_raises_validation_error(self):
        """Extensión inválida (.bmp) debe lanzar ProductValidationError (Req. 7.2)."""
        from services.product_service import ProductValidationError
        mock_repo = MagicMock()
        mock_repo.get_by_id.return_value = self._make_product()
        mock_repo.count_images.return_value = 0

        service = self._make_service(mock_repo)

        with pytest.raises(ProductValidationError):
            service.add_image(
                product_id="product-abc",
                producer_id="producer-uid-123",
                file_content=b"\x42\x4d...",
                content_type="image/bmp",
                filename="photo.bmp",
            )

    def test_oversized_file_raises_validation_error(self):
        """Archivo > 5 MB debe lanzar ProductValidationError (Req. 7.3)."""
        from services.product_service import ProductValidationError
        mock_repo = MagicMock()
        mock_repo.get_by_id.return_value = self._make_product()
        mock_repo.count_images.return_value = 0

        service = self._make_service(mock_repo)

        big_content = b"\xff\xd8\xff\xe0" + b"\x00" * (5 * 1024 * 1024 + 1)

        with pytest.raises(ProductValidationError) as exc_info:
            service.add_image(
                product_id="product-abc",
                producer_id="producer-uid-123",
                file_content=big_content,
                content_type="image/jpeg",
                filename="big.jpg",
            )

        assert exc_info.value.code == "VALIDATION_ERROR"

    def test_image_limit_exceeded_raises_limit_error(self):
        """Superar el límite de 5 imágenes debe lanzar ProductImageLimitError (Req. 7.4)."""
        from services.product_service import ProductImageLimitError
        mock_repo = MagicMock()
        mock_repo.get_by_id.return_value = self._make_product()
        mock_repo.count_images.return_value = 5  # ya tiene 5 imágenes

        service = self._make_service(mock_repo)

        with pytest.raises(ProductImageLimitError):
            service.add_image(
                product_id="product-abc",
                producer_id="producer-uid-123",
                file_content=b"\xff\xd8\xff\xe0" + b"\x00" * 1024,
                content_type="image/jpeg",
                filename="photo.jpg",
            )

    def test_non_owner_raises_forbidden(self):
        """Productor que no es dueño debe lanzar ProductForbiddenError."""
        from services.product_service import ProductForbiddenError
        mock_repo = MagicMock()
        mock_repo.get_by_id.return_value = self._make_product(producer_id="owner-uid")

        service = self._make_service(mock_repo)

        with pytest.raises(ProductForbiddenError):
            service.add_image(
                product_id="product-abc",
                producer_id="different-uid",
                file_content=b"\xff\xd8\xff\xe0" + b"\x00" * 1024,
                content_type="image/jpeg",
                filename="photo.jpg",
            )

    def test_product_not_found_raises_not_found(self):
        """Producto inexistente debe lanzar ProductNotFoundServiceError."""
        from services.product_service import ProductNotFoundServiceError
        mock_repo = MagicMock()
        mock_repo.get_by_id.return_value = None

        service = self._make_service(mock_repo)

        with pytest.raises(ProductNotFoundServiceError):
            service.add_image(
                product_id="nonexistent",
                producer_id="producer-uid-123",
                file_content=b"\xff\xd8\xff\xe0" + b"\x00" * 1024,
                content_type="image/jpeg",
                filename="photo.jpg",
            )

    def test_valid_jpeg_calls_upload_and_repo(self):
        """Imagen válida debe llamar al método de subida y al repositorio."""
        mock_repo = MagicMock()
        mock_repo.get_by_id.return_value = self._make_product()
        mock_repo.count_images.return_value = 2
        mock_repo.add_image.return_value = {
            "id": "new-img-id",
            "url": "https://storage.example.com/img.jpg",
            "storagePath": "products/product-abc/images/new-img-id.jpg",
            "sortOrder": 2,
            "createdAt": datetime.now(timezone.utc),
        }

        from services.product_service import ProductService
        service = ProductService(repository=mock_repo)

        # Mockear el método privado de subida a Storage
        with patch.object(service, "_upload_to_storage") as mock_upload:
            mock_upload.return_value = (
                "products/product-abc/images/new-img-id.jpg",
                "https://storage.example.com/img.jpg",
            )

            result = service.add_image(
                product_id="product-abc",
                producer_id="producer-uid-123",
                file_content=b"\xff\xd8\xff\xe0" + b"\x00" * 1024,
                content_type="image/jpeg",
                filename="photo.jpg",
            )

        mock_upload.assert_called_once()
        mock_repo.add_image.assert_called_once()
        assert result["id"] == "new-img-id"

    def test_max_4_images_allows_fifth(self):
        """Con 4 imágenes existentes, debe permitir agregar la quinta (Req. 7.4)."""
        mock_repo = MagicMock()
        mock_repo.get_by_id.return_value = self._make_product()
        mock_repo.count_images.return_value = 4  # exactamente 4 → permite una más
        mock_repo.add_image.return_value = {
            "id": "fifth-img",
            "url": "https://storage.example.com/fifth.jpg",
            "storagePath": "products/product-abc/images/fifth.jpg",
            "sortOrder": 4,
            "createdAt": datetime.now(timezone.utc),
        }

        from services.product_service import ProductService
        service = ProductService(repository=mock_repo)

        with patch.object(service, "_upload_to_storage") as mock_upload:
            mock_upload.return_value = (
                "products/product-abc/images/fifth.jpg",
                "https://storage.example.com/fifth.jpg",
            )

            result = service.add_image(
                product_id="product-abc",
                producer_id="producer-uid-123",
                file_content=b"\xff\xd8\xff\xe0" + b"\x00" * 1024,
                content_type="image/jpeg",
                filename="fifth.jpg",
            )

        assert result["id"] == "fifth-img"


# ---------------------------------------------------------------------------
# Tests unitarios – ProductService.delete_image
# ---------------------------------------------------------------------------

class TestProductServiceDeleteImage:
    """Tests unitarios del método ProductService.delete_image (Req. 7.5)."""

    def _make_service(self, mock_repo):
        from services.product_service import ProductService
        return ProductService(repository=mock_repo)

    def test_delete_calls_repo_delete(self):
        """Eliminación exitosa debe llamar al repositorio para desvincular la imagen (Req. 7.5)."""
        mock_repo = MagicMock()
        mock_repo.get_by_id.return_value = {
            "id": "product-abc",
            "producerId": "producer-uid-123",
        }
        mock_repo.get_image_by_id.return_value = {
            "id": "image-xyz",
            "url": "https://storage.example.com/img.jpg",
            "storagePath": "products/product-abc/images/image-xyz.jpg",
        }

        service = self._make_service(mock_repo)

        with patch.object(service, "_delete_from_storage") as mock_delete_storage:
            service.delete_image(
                product_id="product-abc",
                image_id="image-xyz",
                producer_id="producer-uid-123",
            )

        mock_repo.delete_image.assert_called_once_with("product-abc", "image-xyz")
        mock_delete_storage.assert_called_once_with(
            "products/product-abc/images/image-xyz.jpg"
        )

    def test_delete_non_owner_raises_forbidden(self):
        """Productor que no es dueño debe lanzar ProductForbiddenError."""
        from services.product_service import ProductForbiddenError
        mock_repo = MagicMock()
        mock_repo.get_by_id.return_value = {
            "id": "product-abc",
            "producerId": "owner-uid",
        }

        service = self._make_service(mock_repo)

        with pytest.raises(ProductForbiddenError):
            service.delete_image(
                product_id="product-abc",
                image_id="image-xyz",
                producer_id="different-uid",
            )

    def test_delete_image_not_found_raises_error(self):
        """Imagen inexistente debe lanzar ProductImageNotFoundError."""
        from services.product_service import ProductImageNotFoundError
        mock_repo = MagicMock()
        mock_repo.get_by_id.return_value = {
            "id": "product-abc",
            "producerId": "producer-uid-123",
        }
        mock_repo.get_image_by_id.return_value = None

        service = self._make_service(mock_repo)

        with pytest.raises(ProductImageNotFoundError):
            service.delete_image(
                product_id="product-abc",
                image_id="nonexistent-img",
                producer_id="producer-uid-123",
            )

    def test_delete_without_storage_path_skips_storage_deletion(self):
        """Si la imagen no tiene storagePath, no debe intentar eliminar de Storage."""
        mock_repo = MagicMock()
        mock_repo.get_by_id.return_value = {
            "id": "product-abc",
            "producerId": "producer-uid-123",
        }
        mock_repo.get_image_by_id.return_value = {
            "id": "image-xyz",
            "url": "https://storage.example.com/img.jpg",
            # Sin storagePath
        }

        service = self._make_service(mock_repo)

        with patch.object(service, "_delete_from_storage") as mock_delete_storage:
            service.delete_image(
                product_id="product-abc",
                image_id="image-xyz",
                producer_id="producer-uid-123",
            )

        mock_delete_storage.assert_not_called()
        mock_repo.delete_image.assert_called_once()
