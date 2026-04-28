# placeholder
"""
test_catalog.py – Tests para los endpoints GET /api/products y GET /api/products/:id.

Cubre:
  - Catálogo con paginación (Tarea 5.1, Req. 9.1, 9.3, 9.4)
  - Búsqueda y filtros (Tarea 5.4, Req. 10.1–10.5)
  - Detalle de producto (Tarea 5.6, Req. 11.1–11.3)
"""

from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from main import app


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def client():
    return TestClient(app, raise_server_exceptions=False)


def _make_catalog_result(items, total=None, page=1, page_size=20):
    if total is None:
        total = len(items)
    has_next = (page - 1) * page_size + len(items) < total
    return {
        "data": {
            "items": items,
            "total": total,
            "page": page,
            "pageSize": page_size,
            "hasNext": has_next,
        }
    }


def _make_active_item(product_id="prod-1", name="Cafe Especial", price=25000.0,
                      producer_name="Finca El Paraiso", main_image_url=None):
    return {
        "id": product_id,
        "name": name,
        "price": price,
        "producerName": producer_name,
        "mainImageUrl": main_image_url,
    }


def _make_product_detail(product_id="prod-1", status="active"):
    return {
        "id": product_id,
        "name": "Cafe Especial",
        "description": "Cafe de altura con notas frutales",
        "price": 25000.0,
        "status": status,
        "producerId": "producer-uid-123",
        "producerName": "Finca El Paraiso",
        "images": [
            {"id": "img-1", "url": "https://example.com/img.jpg", "sortOrder": 0}
        ],
        "producer": {
            "farmName": "Finca El Paraiso",
            "region": "Huila",
            "description": "Productores de cafe de especialidad",
            "contactInfo": "contacto@finca.com",
        },
        "createdAt": datetime(2024, 6, 1, tzinfo=timezone.utc).isoformat(),
        "updatedAt": datetime(2024, 6, 1, tzinfo=timezone.utc).isoformat(),
    }


# ---------------------------------------------------------------------------
# Tests – GET /api/products (Catálogo, Tarea 5.1)
# ---------------------------------------------------------------------------

class TestCatalogEndpoint:

    def test_returns_only_active_products(self, client, mock_firebase_auth):
        item = _make_active_item()
        service_result = _make_catalog_result([item])

        with patch("routes.products.ProductService") as mock_cls:
            mock_svc = MagicMock()
            mock_cls.return_value = mock_svc
            mock_svc.get_catalog.return_value = service_result

            response = client.get("/api/products")

        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "items" in data["data"]
        assert len(data["data"]["items"]) == 1
        assert data["data"]["items"][0]["id"] == "prod-1"

    def test_public_endpoint_no_auth_required(self, client):
        service_result = _make_catalog_result([])
        service_result["message"] = "No se encontraron productos con los criterios seleccionados."

        with patch("routes.products.ProductService") as mock_cls:
            mock_svc = MagicMock()
            mock_cls.return_value = mock_svc
            mock_svc.get_catalog.return_value = service_result

            response = client.get("/api/products")

        assert response.status_code == 200

    def test_empty_catalog_returns_empty_list(self, client):
        service_result = {
            "data": {
                "items": [],
                "total": 0,
                "page": 1,
                "pageSize": 20,
                "hasNext": False,
            },
            "message": "No se encontraron productos con los criterios seleccionados.",
        }

        with patch("routes.products.ProductService") as mock_cls:
            mock_svc = MagicMock()
            mock_cls.return_value = mock_svc
            mock_svc.get_catalog.return_value = service_result

            response = client.get("/api/products")

        assert response.status_code == 200
        body = response.json()
        assert body["data"]["items"] == []
        assert body["data"]["total"] == 0
        assert "message" in body

    def test_response_includes_required_fields(self, client):
        item = _make_active_item(main_image_url="https://example.com/img.jpg")
        service_result = _make_catalog_result([item])

        with patch("routes.products.ProductService") as mock_cls:
            mock_svc = MagicMock()
            mock_cls.return_value = mock_svc
            mock_svc.get_catalog.return_value = service_result

            response = client.get("/api/products")

        assert response.status_code == 200
        item_data = response.json()["data"]["items"][0]
        assert "id" in item_data
        assert "name" in item_data
        assert "price" in item_data
        assert "producerName" in item_data
        assert "mainImageUrl" in item_data

    def test_pagination_params_passed_to_service(self, client):
        service_result = _make_catalog_result([], page=2, page_size=10)

        with patch("routes.products.ProductService") as mock_cls:
            mock_svc = MagicMock()
            mock_cls.return_value = mock_svc
            mock_svc.get_catalog.return_value = service_result

            response = client.get("/api/products?page=2&pageSize=10")

        assert response.status_code == 200
        mock_svc.get_catalog.assert_called_once_with(
            page=2,
            page_size=10,
            q=None,
            min_price=None,
            max_price=None,
            region=None,
        )

    def test_pagination_response_shape(self, client):
        items = [_make_active_item(product_id=f"prod-{i}") for i in range(5)]
        service_result = {
            "data": {
                "items": items,
                "total": 25,
                "page": 1,
                "pageSize": 5,
                "hasNext": True,
            }
        }

        with patch("routes.products.ProductService") as mock_cls:
            mock_svc = MagicMock()
            mock_cls.return_value = mock_svc
            mock_svc.get_catalog.return_value = service_result

            response = client.get("/api/products?pageSize=5")

        assert response.status_code == 200
        body = response.json()["data"]
        assert body["total"] == 25
        assert body["page"] == 1
        assert body["pageSize"] == 5
        assert body["hasNext"] is True

    def test_page_size_max_20(self, client):
        response = client.get("/api/products?pageSize=21")
        assert response.status_code == 422

    def test_page_min_1(self, client):
        response = client.get("/api/products?page=0")
        assert response.status_code == 422

    def test_main_image_url_null_when_no_images(self, client):
        item = _make_active_item(main_image_url=None)
        service_result = _make_catalog_result([item])

        with patch("routes.products.ProductService") as mock_cls:
            mock_svc = MagicMock()
            mock_cls.return_value = mock_svc
            mock_svc.get_catalog.return_value = service_result

            response = client.get("/api/products")

        assert response.status_code == 200
        assert response.json()["data"]["items"][0]["mainImageUrl"] is None


# ---------------------------------------------------------------------------
# Tests – GET /api/products (Búsqueda y filtros, Tarea 5.4)
# ---------------------------------------------------------------------------

class TestCatalogFilters:

    def test_q_param_passed_to_service(self, client):
        service_result = _make_catalog_result([_make_active_item()])

        with patch("routes.products.ProductService") as mock_cls:
            mock_svc = MagicMock()
            mock_cls.return_value = mock_svc
            mock_svc.get_catalog.return_value = service_result

            response = client.get("/api/products?q=especial")

        assert response.status_code == 200
        mock_svc.get_catalog.assert_called_once_with(
            page=1,
            page_size=20,
            q="especial",
            min_price=None,
            max_price=None,
            region=None,
        )

    def test_min_price_param_passed_to_service(self, client):
        service_result = _make_catalog_result([_make_active_item()])

        with patch("routes.products.ProductService") as mock_cls:
            mock_svc = MagicMock()
            mock_cls.return_value = mock_svc
            mock_svc.get_catalog.return_value = service_result

            response = client.get("/api/products?minPrice=10000")

        assert response.status_code == 200
        mock_svc.get_catalog.assert_called_once_with(
            page=1,
            page_size=20,
            q=None,
            min_price=10000.0,
            max_price=None,
            region=None,
        )

    def test_max_price_param_passed_to_service(self, client):
        service_result = _make_catalog_result([_make_active_item()])

        with patch("routes.products.ProductService") as mock_cls:
            mock_svc = MagicMock()
            mock_cls.return_value = mock_svc
            mock_svc.get_catalog.return_value = service_result

            response = client.get("/api/products?maxPrice=50000")

        assert response.status_code == 200
        mock_svc.get_catalog.assert_called_once_with(
            page=1,
            page_size=20,
            q=None,
            min_price=None,
            max_price=50000.0,
            region=None,
        )

    def test_region_param_passed_to_service(self, client):
        service_result = _make_catalog_result([_make_active_item()])

        with patch("routes.products.ProductService") as mock_cls:
            mock_svc = MagicMock()
            mock_cls.return_value = mock_svc
            mock_svc.get_catalog.return_value = service_result

            response = client.get("/api/products?region=Huila")

        assert response.status_code == 200
        mock_svc.get_catalog.assert_called_once_with(
            page=1,
            page_size=20,
            q=None,
            min_price=None,
            max_price=None,
            region="Huila",
        )

    def test_combined_filters_passed_to_service(self, client):
        service_result = _make_catalog_result([_make_active_item()])

        with patch("routes.products.ProductService") as mock_cls:
            mock_svc = MagicMock()
            mock_cls.return_value = mock_svc
            mock_svc.get_catalog.return_value = service_result

            response = client.get(
                "/api/products?q=cafe&minPrice=5000&maxPrice=30000&region=Huila"
            )

        assert response.status_code == 200
        mock_svc.get_catalog.assert_called_once_with(
            page=1,
            page_size=20,
            q="cafe",
            min_price=5000.0,
            max_price=30000.0,
            region="Huila",
        )

    def test_no_results_returns_message(self, client):
        service_result = {
            "data": {
                "items": [],
                "total": 0,
                "page": 1,
                "pageSize": 20,
                "hasNext": False,
            },
            "message": "No se encontraron productos con los criterios seleccionados.",
        }

        with patch("routes.products.ProductService") as mock_cls:
            mock_svc = MagicMock()
            mock_cls.return_value = mock_svc
            mock_svc.get_catalog.return_value = service_result

            response = client.get("/api/products?q=inexistente")

        assert response.status_code == 200
        body = response.json()
        assert body["data"]["items"] == []
        assert body["message"] == "No se encontraron productos con los criterios seleccionados."

    def test_negative_min_price_returns_422(self, client):
        response = client.get("/api/products?minPrice=-1")
        assert response.status_code == 422

    def test_negative_max_price_returns_422(self, client):
        response = client.get("/api/products?maxPrice=-1")
        assert response.status_code == 422


# ---------------------------------------------------------------------------
# Tests – GET /api/products/:id (Detalle, Tarea 5.6)
# ---------------------------------------------------------------------------

class TestProductDetailEndpoint:

    def test_returns_full_product_data(self, client):
        detail = _make_product_detail()
        service_result = {"data": detail}

        with patch("routes.products.ProductService") as mock_cls:
            mock_svc = MagicMock()
            mock_cls.return_value = mock_svc
            mock_svc.get_product_detail.return_value = service_result

            response = client.get("/api/products/prod-1")

        assert response.status_code == 200
        data = response.json()["data"]
        assert data["id"] == "prod-1"
        assert data["name"] == "Cafe Especial"
        assert data["description"] == "Cafe de altura con notas frutales"
        assert data["price"] == 25000.0
        assert data["status"] == "active"
        assert data["producerId"] == "producer-uid-123"
        assert data["producerName"] == "Finca El Paraiso"

    def test_returns_images_list(self, client):
        detail = _make_product_detail()
        service_result = {"data": detail}

        with patch("routes.products.ProductService") as mock_cls:
            mock_svc = MagicMock()
            mock_cls.return_value = mock_svc
            mock_svc.get_product_detail.return_value = service_result

            response = client.get("/api/products/prod-1")

        assert response.status_code == 200
        images = response.json()["data"]["images"]
        assert isinstance(images, list)
        assert len(images) == 1
        assert images[0]["url"] == "https://example.com/img.jpg"

    def test_returns_producer_info(self, client):
        detail = _make_product_detail()
        service_result = {"data": detail}

        with patch("routes.products.ProductService") as mock_cls:
            mock_svc = MagicMock()
            mock_cls.return_value = mock_svc
            mock_svc.get_product_detail.return_value = service_result

            response = client.get("/api/products/prod-1")

        assert response.status_code == 200
        producer = response.json()["data"]["producer"]
        assert producer["farmName"] == "Finca El Paraiso"
        assert producer["region"] == "Huila"

    def test_inactive_product_returns_200_with_message(self, client):
        detail = _make_product_detail(status="inactive")
        service_result = {
            "data": detail,
            "message": "Este producto no está disponible actualmente.",
        }

        with patch("routes.products.ProductService") as mock_cls:
            mock_svc = MagicMock()
            mock_cls.return_value = mock_svc
            mock_svc.get_product_detail.return_value = service_result

            response = client.get("/api/products/prod-1")

        assert response.status_code == 200
        body = response.json()
        assert body["data"]["status"] == "inactive"
        assert body["message"] == "Este producto no está disponible actualmente."

    def test_nonexistent_product_returns_404(self, client):
        from services.product_service import ProductNotFoundServiceError

        with patch("routes.products.ProductService") as mock_cls:
            mock_svc = MagicMock()
            mock_cls.return_value = mock_svc
            mock_svc.get_product_detail.side_effect = ProductNotFoundServiceError("nonexistent-id")

            response = client.get("/api/products/nonexistent-id")

        assert response.status_code == 404

    def test_public_endpoint_no_auth_required(self, client):
        detail = _make_product_detail()
        service_result = {"data": detail}

        with patch("routes.products.ProductService") as mock_cls:
            mock_svc = MagicMock()
            mock_cls.return_value = mock_svc
            mock_svc.get_product_detail.return_value = service_result

            response = client.get("/api/products/prod-1")

        assert response.status_code == 200

    def test_service_called_with_correct_product_id(self, client):
        detail = _make_product_detail(product_id="specific-id")
        service_result = {"data": detail}

        with patch("routes.products.ProductService") as mock_cls:
            mock_svc = MagicMock()
            mock_cls.return_value = mock_svc
            mock_svc.get_product_detail.return_value = service_result

            client.get("/api/products/specific-id")

        mock_svc.get_product_detail.assert_called_once_with("specific-id")


# ---------------------------------------------------------------------------
# Tests unitarios – ProductService.get_catalog
# ---------------------------------------------------------------------------

class TestProductServiceGetCatalog:

    def _make_service(self, mock_repo):
        from services.product_service import ProductService
        return ProductService(repository=mock_repo)

    def _make_product(self, product_id, name, price, producer_name="Finca", status="active",
                      description="Descripcion"):
        return {
            "id": product_id,
            "name": name,
            "description": description,
            "price": price,
            "producerName": producer_name,
            "producerId": "producer-1",
            "status": status,
            "createdAt": datetime(2024, 6, 1, tzinfo=timezone.utc),
            "updatedAt": datetime(2024, 6, 1, tzinfo=timezone.utc),
        }

    def test_returns_only_active_products(self):
        mock_repo = MagicMock()
        active = self._make_product("p1", "Cafe Activo", 20000)
        mock_repo.list_active.return_value = ([active], 1)
        mock_repo.get_first_image.return_value = None

        service = self._make_service(mock_repo)
        result = service.get_catalog()

        assert result["data"]["total"] == 1
        assert result["data"]["items"][0]["id"] == "p1"

    def test_q_filter_by_name_case_insensitive(self):
        mock_repo = MagicMock()
        products = [
            self._make_product("p1", "Cafe Especial", 20000),
            self._make_product("p2", "Te Verde", 5000),
        ]
        mock_repo.list_active.return_value = (products, 2)
        mock_repo.get_first_image.return_value = None

        service = self._make_service(mock_repo)
        result = service.get_catalog(q="CAFE")

        assert result["data"]["total"] == 1
        assert result["data"]["items"][0]["id"] == "p1"

    def test_q_filter_by_description(self):
        mock_repo = MagicMock()
        products = [
            self._make_product("p1", "Producto A", 20000, description="Cafe de altura"),
            self._make_product("p2", "Producto B", 5000, description="Te organico"),
        ]
        mock_repo.list_active.return_value = (products, 2)
        mock_repo.get_first_image.return_value = None

        service = self._make_service(mock_repo)
        result = service.get_catalog(q="altura")

        assert result["data"]["total"] == 1
        assert result["data"]["items"][0]["id"] == "p1"

    def test_min_price_filter(self):
        mock_repo = MagicMock()
        products = [
            self._make_product("p1", "Caro", 50000),
            self._make_product("p2", "Barato", 5000),
        ]
        mock_repo.list_active.return_value = (products, 2)
        mock_repo.get_first_image.return_value = None

        service = self._make_service(mock_repo)
        result = service.get_catalog(min_price=20000)

        assert result["data"]["total"] == 1
        assert result["data"]["items"][0]["id"] == "p1"

    def test_max_price_filter(self):
        mock_repo = MagicMock()
        products = [
            self._make_product("p1", "Caro", 50000),
            self._make_product("p2", "Barato", 5000),
        ]
        mock_repo.list_active.return_value = (products, 2)
        mock_repo.get_first_image.return_value = None

        service = self._make_service(mock_repo)
        result = service.get_catalog(max_price=10000)

        assert result["data"]["total"] == 1
        assert result["data"]["items"][0]["id"] == "p2"

    def test_region_filter(self):
        mock_repo = MagicMock()
        # Two products from different producers in different regions
        p1 = self._make_product("p1", "Cafe Huila", 20000)
        p1["producerId"] = "producer-huila"
        p2 = self._make_product("p2", "Cafe Narino", 20000)
        p2["producerId"] = "producer-narino"
        products = [p1, p2]
        mock_repo.list_active.return_value = (products, 2)
        mock_repo.get_first_image.return_value = None
        mock_repo.get_producer_profile.side_effect = lambda pid: {
            "producer-huila": {"region": "Huila"},
            "producer-narino": {"region": "Narino"},
        }.get(pid)

        service = self._make_service(mock_repo)
        result = service.get_catalog(region="Huila")

        assert result["data"]["total"] == 1
        assert result["data"]["items"][0]["id"] == "p1"

    def test_combined_filters(self):
        mock_repo = MagicMock()
        products = [
            self._make_product("p1", "Cafe Especial", 25000, description="Cafe de altura"),
            self._make_product("p2", "Cafe Barato", 5000, description="Cafe comun"),
            self._make_product("p3", "Te Verde", 25000, description="Te organico"),
        ]
        mock_repo.list_active.return_value = (products, 3)
        mock_repo.get_first_image.return_value = None

        service = self._make_service(mock_repo)
        result = service.get_catalog(q="cafe", min_price=10000)

        assert result["data"]["total"] == 1
        assert result["data"]["items"][0]["id"] == "p1"

    def test_no_results_returns_message(self):
        mock_repo = MagicMock()
        mock_repo.list_active.return_value = ([], 0)

        service = self._make_service(mock_repo)
        result = service.get_catalog(q="inexistente")

        assert result["data"]["total"] == 0
        assert result["data"]["items"] == []
        assert "message" in result
        assert result["message"] == "No se encontraron productos con los criterios seleccionados."

    def test_pagination_returns_correct_page(self):
        mock_repo = MagicMock()
        products = [self._make_product(f"p{i}", f"Cafe {i}", 10000 + i) for i in range(25)]
        mock_repo.list_active.return_value = (products, 25)
        mock_repo.get_first_image.return_value = None

        service = self._make_service(mock_repo)
        result = service.get_catalog(page=2, page_size=10)

        assert result["data"]["page"] == 2
        assert result["data"]["pageSize"] == 10
        assert len(result["data"]["items"]) == 10
        assert result["data"]["hasNext"] is True

    def test_main_image_url_from_first_image(self):
        mock_repo = MagicMock()
        product = self._make_product("p1", "Cafe", 20000)
        mock_repo.list_active.return_value = ([product], 1)
        mock_repo.get_first_image.return_value = {"id": "img-1", "url": "https://example.com/img.jpg", "sortOrder": 0}

        service = self._make_service(mock_repo)
        result = service.get_catalog()

        assert result["data"]["items"][0]["mainImageUrl"] == "https://example.com/img.jpg"

    def test_main_image_url_null_when_no_images(self):
        mock_repo = MagicMock()
        product = self._make_product("p1", "Cafe", 20000)
        mock_repo.list_active.return_value = ([product], 1)
        mock_repo.get_first_image.return_value = None

        service = self._make_service(mock_repo)
        result = service.get_catalog()

        assert result["data"]["items"][0]["mainImageUrl"] is None


# ---------------------------------------------------------------------------
# Tests unitarios – ProductService.get_product_detail
# ---------------------------------------------------------------------------

class TestProductServiceGetProductDetail:

    def _make_service(self, mock_repo):
        from services.product_service import ProductService
        return ProductService(repository=mock_repo)

    def test_returns_full_product_data(self):
        mock_repo = MagicMock()
        now = datetime(2024, 6, 1, tzinfo=timezone.utc)
        mock_repo.get_by_id.return_value = {
            "id": "prod-1",
            "name": "Cafe Especial",
            "description": "Descripcion",
            "price": 25000.0,
            "status": "active",
            "producerId": "producer-1",
            "producerName": "Finca",
            "createdAt": now,
            "updatedAt": now,
        }
        mock_repo.get_images.return_value = [
            {"id": "img-1", "url": "https://example.com/img.jpg", "sortOrder": 0}
        ]
        mock_repo.get_producer_profile.return_value = {
            "farmName": "Finca El Paraiso",
            "region": "Huila",
            "description": "Productores",
            "contactInfo": "contacto@finca.com",
        }

        from services.product_service import ProductService
        service = ProductService(repository=mock_repo)
        result = service.get_product_detail("prod-1")

        assert result["data"]["id"] == "prod-1"
        assert result["data"]["name"] == "Cafe Especial"
        assert len(result["data"]["images"]) == 1
        assert result["data"]["producer"]["farmName"] == "Finca El Paraiso"

    def test_inactive_product_includes_message(self):
        mock_repo = MagicMock()
        now = datetime(2024, 6, 1, tzinfo=timezone.utc)
        mock_repo.get_by_id.return_value = {
            "id": "prod-1",
            "name": "Cafe",
            "description": "Desc",
            "price": 10000.0,
            "status": "inactive",
            "producerId": "producer-1",
            "producerName": "Finca",
            "createdAt": now,
            "updatedAt": now,
        }
        mock_repo.get_images.return_value = []
        mock_repo.get_producer_profile.return_value = None

        from services.product_service import ProductService
        service = ProductService(repository=mock_repo)
        result = service.get_product_detail("prod-1")

        assert result["data"]["status"] == "inactive"
        assert "message" in result
        assert result["message"] == "Este producto no está disponible actualmente."

    def test_active_product_has_no_message(self):
        mock_repo = MagicMock()
        now = datetime(2024, 6, 1, tzinfo=timezone.utc)
        mock_repo.get_by_id.return_value = {
            "id": "prod-1",
            "name": "Cafe",
            "description": "Desc",
            "price": 10000.0,
            "status": "active",
            "producerId": "producer-1",
            "producerName": "Finca",
            "createdAt": now,
            "updatedAt": now,
        }
        mock_repo.get_images.return_value = []
        mock_repo.get_producer_profile.return_value = None

        from services.product_service import ProductService
        service = ProductService(repository=mock_repo)
        result = service.get_product_detail("prod-1")

        assert "message" not in result

    def test_nonexistent_product_raises_not_found(self):
        from services.product_service import ProductNotFoundServiceError, ProductService

        mock_repo = MagicMock()
        mock_repo.get_by_id.return_value = None

        service = ProductService(repository=mock_repo)

        with pytest.raises(ProductNotFoundServiceError):
            service.get_product_detail("nonexistent-id")
