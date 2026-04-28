"""
test_sales.py – Tests para el panel de ventas del productor.

Cubre:
  - GET /api/sales → Panel de ventas (Req. 16.1, 16.2, 16.3, 16.4)

Tests de integración (ruta HTTP):
  - Retorna lista de pedidos con ítems del productor (Req. 16.1)
  - Retorna totales del mes en curso y mes anterior (Req. 16.2)
  - Soporta filtro por rango de fechas (Req. 16.3)
  - Solo expone datos del propio productor (Req. 16.4)
  - Requiere autenticación y rol PRODUCER

Tests unitarios del OrderService:
  - get_producer_sales: retorna pedidos y totales correctos
  - get_producer_sales: calcula totales mensuales sobre todos los pedidos
  - get_producer_sales: aplica filtro de fechas solo a la lista de pedidos
"""

from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from main import app


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_NOW = datetime(2024, 6, 15, 12, 0, 0, tzinfo=timezone.utc)   # mes en curso (junio 2024)
_PREV = datetime(2024, 5, 10, 8, 0, 0, tzinfo=timezone.utc)   # mes anterior (mayo 2024)
_OLD = datetime(2024, 4, 1, 10, 0, 0, tzinfo=timezone.utc)    # hace dos meses


def _make_order(
    order_id="order-1",
    consumer_id="consumer-abc",
    status="pagado",
    created_at=None,
    items=None,
    shipping_company="Servientrega",
):
    return {
        "id": order_id,
        "consumerId": consumer_id,
        "addressSnapshot": {
            "street": "Calle 10 # 5-20",
            "city": "Bogotá",
            "department": "Cundinamarca",
            "postalCode": "110111",
        },
        "shippingCompany": shipping_company,
        "shippingCost": 5000.0,
        "total": 80000.0,
        "status": status,
        "transactionId": None,
        "createdAt": created_at or _NOW,
        "updatedAt": created_at or _NOW,
        "items": items or [],
    }


def _make_item(
    item_id="item-1",
    product_id="prod-producer",
    product_name="Café Especial",
    price=25000.0,
    quantity=2,
):
    return {
        "id": item_id,
        "productId": product_id,
        "productNameSnapshot": product_name,
        "priceSnapshot": price,
        "quantity": quantity,
    }


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def client():
    return TestClient(app, raise_server_exceptions=False)


@pytest.fixture
def producer_token_headers(mock_firebase_auth):
    """Simula un token válido de productor."""
    mock_firebase_auth.verify_id_token.return_value = {
        "uid": "producer-456",
        "email": "producer@test.com",
        "role": "PRODUCER",
    }
    return {"Authorization": "Bearer valid-producer-token"}


@pytest.fixture
def consumer_token_headers(mock_firebase_auth):
    """Simula un token válido de consumidor."""
    mock_firebase_auth.verify_id_token.return_value = {
        "uid": "consumer-123",
        "email": "consumer@test.com",
        "role": "CONSUMER",
    }
    return {"Authorization": "Bearer valid-consumer-token"}


# ---------------------------------------------------------------------------
# Tests de integración – GET /api/sales
# ---------------------------------------------------------------------------


class TestGetSalesEndpoint:
    """Tests de integración para GET /api/sales (Req. 16.1–16.4)."""

    def test_requires_authentication(self, client):
        """Sin token retorna 401."""
        response = client.get("/api/sales")
        assert response.status_code == 401

    def test_requires_producer_role(self, client, consumer_token_headers):
        """Rol CONSUMER no puede acceder al panel de ventas."""
        response = client.get("/api/sales", headers=consumer_token_headers)
        assert response.status_code == 403

    def test_returns_empty_orders_when_no_sales(self, client, producer_token_headers):
        """Productor sin ventas recibe lista vacía y totales en cero."""
        with patch("routes.sales.OrderService") as mock_cls:
            mock_svc = MagicMock()
            mock_cls.return_value = mock_svc
            mock_svc.get_producer_sales.return_value = {
                "orders": [],
                "current_month_total": 0.0,
                "previous_month_total": 0.0,
            }

            response = client.get("/api/sales", headers=producer_token_headers)

        assert response.status_code == 200
        body = response.json()
        assert "data" in body
        data = body["data"]
        assert data["orders"] == []
        assert data["current_month_total"] == 0.0
        assert data["previous_month_total"] == 0.0

    def test_returns_orders_with_required_fields(self, client, producer_token_headers):
        """Cada pedido incluye id, createdAt, status, shippingCompany e items (Req. 16.1)."""
        items = [_make_item()]
        order = _make_order(items=items)

        with patch("routes.sales.OrderService") as mock_cls:
            mock_svc = MagicMock()
            mock_cls.return_value = mock_svc
            mock_svc.get_producer_sales.return_value = {
                "orders": [order],
                "current_month_total": 50000.0,
                "previous_month_total": 0.0,
            }

            response = client.get("/api/sales", headers=producer_token_headers)

        assert response.status_code == 200
        data = response.json()["data"]
        assert len(data["orders"]) == 1
        o = data["orders"][0]
        assert o["id"] == "order-1"
        assert "createdAt" in o
        assert o["status"] == "pagado"
        assert o["shippingCompany"] == "Servientrega"
        assert len(o["items"]) == 1

    def test_items_include_product_name_price_quantity(self, client, producer_token_headers):
        """Los ítems incluyen productNameSnapshot, priceSnapshot y quantity (Req. 16.1)."""
        item = _make_item(price=30000.0, quantity=3)
        order = _make_order(items=[item])

        with patch("routes.sales.OrderService") as mock_cls:
            mock_svc = MagicMock()
            mock_cls.return_value = mock_svc
            mock_svc.get_producer_sales.return_value = {
                "orders": [order],
                "current_month_total": 90000.0,
                "previous_month_total": 0.0,
            }

            response = client.get("/api/sales", headers=producer_token_headers)

        item_data = response.json()["data"]["orders"][0]["items"][0]
        assert item_data["productNameSnapshot"] == "Café Especial"
        assert item_data["priceSnapshot"] == 30000.0
        assert item_data["quantity"] == 3

    def test_returns_monthly_totals(self, client, producer_token_headers):
        """Retorna current_month_total y previous_month_total (Req. 16.2)."""
        with patch("routes.sales.OrderService") as mock_cls:
            mock_svc = MagicMock()
            mock_cls.return_value = mock_svc
            mock_svc.get_producer_sales.return_value = {
                "orders": [],
                "current_month_total": 150000.0,
                "previous_month_total": 75000.0,
            }

            response = client.get("/api/sales", headers=producer_token_headers)

        data = response.json()["data"]
        assert data["current_month_total"] == 150000.0
        assert data["previous_month_total"] == 75000.0

    def test_passes_date_filters_to_service(self, client, producer_token_headers):
        """Los query params from_date y to_date se pasan al servicio (Req. 16.3)."""
        with patch("routes.sales.OrderService") as mock_cls:
            mock_svc = MagicMock()
            mock_cls.return_value = mock_svc
            mock_svc.get_producer_sales.return_value = {
                "orders": [],
                "current_month_total": 0.0,
                "previous_month_total": 0.0,
            }

            client.get(
                "/api/sales?from_date=2024-06-01&to_date=2024-06-30",
                headers=producer_token_headers,
            )

        from datetime import date
        mock_svc.get_producer_sales.assert_called_once_with(
            producer_id="producer-456",
            from_date=date(2024, 6, 1),
            to_date=date(2024, 6, 30),
        )

    def test_service_called_with_producer_id(self, client, producer_token_headers):
        """El servicio recibe el UID del productor autenticado (Req. 16.4)."""
        with patch("routes.sales.OrderService") as mock_cls:
            mock_svc = MagicMock()
            mock_cls.return_value = mock_svc
            mock_svc.get_producer_sales.return_value = {
                "orders": [],
                "current_month_total": 0.0,
                "previous_month_total": 0.0,
            }

            client.get("/api/sales", headers=producer_token_headers)

        mock_svc.get_producer_sales.assert_called_once_with(
            producer_id="producer-456",
            from_date=None,
            to_date=None,
        )

    def test_returns_500_on_service_error(self, client, producer_token_headers):
        """Error interno del servicio retorna 500."""
        from services.order_service import OrderServiceError

        with patch("routes.sales.OrderService") as mock_cls:
            mock_svc = MagicMock()
            mock_cls.return_value = mock_svc
            mock_svc.get_producer_sales.side_effect = OrderServiceError(
                "Error de Firestore", "FIRESTORE_READ_ERROR"
            )

            response = client.get("/api/sales", headers=producer_token_headers)

        assert response.status_code == 500
        error = response.json()["detail"]["error"]
        assert error["code"] == "FIRESTORE_READ_ERROR"

    def test_timestamps_serialized_as_iso_strings(self, client, producer_token_headers):
        """Los timestamps se serializan como strings ISO 8601."""
        order = _make_order(created_at=_NOW)

        with patch("routes.sales.OrderService") as mock_cls:
            mock_svc = MagicMock()
            mock_cls.return_value = mock_svc
            mock_svc.get_producer_sales.return_value = {
                "orders": [order],
                "current_month_total": 0.0,
                "previous_month_total": 0.0,
            }

            response = client.get("/api/sales", headers=producer_token_headers)

        o = response.json()["data"]["orders"][0]
        assert isinstance(o["createdAt"], str)
        assert "2024-06-15" in o["createdAt"]

    def test_no_date_filters_returns_all_orders(self, client, producer_token_headers):
        """Sin filtros de fecha se retornan todos los pedidos."""
        orders = [
            _make_order("o1", created_at=_NOW, items=[_make_item()]),
            _make_order("o2", created_at=_PREV, items=[_make_item("item-2")]),
        ]

        with patch("routes.sales.OrderService") as mock_cls:
            mock_svc = MagicMock()
            mock_cls.return_value = mock_svc
            mock_svc.get_producer_sales.return_value = {
                "orders": orders,
                "current_month_total": 50000.0,
                "previous_month_total": 50000.0,
            }

            response = client.get("/api/sales", headers=producer_token_headers)

        data = response.json()["data"]
        assert len(data["orders"]) == 2


# ---------------------------------------------------------------------------
# Tests unitarios – OrderService.get_producer_sales
# ---------------------------------------------------------------------------


class TestOrderServiceGetProducerSales:
    """Tests unitarios del método get_producer_sales (Req. 16.1–16.4)."""

    def _make_service(self, mock_order_repo):
        from services.order_service import OrderService

        return OrderService(order_repository=mock_order_repo)

    def test_returns_orders_and_totals(self):
        """Retorna pedidos y totales correctos."""
        items = [_make_item(price=25000.0, quantity=2)]  # subtotal = 50000
        order = _make_order(items=items, created_at=_NOW)

        mock_repo = MagicMock()
        mock_repo.get_orders_by_producer.return_value = [order]

        with patch("services.order_service.datetime") as mock_dt:
            mock_dt.now.return_value = _NOW
            service = self._make_service(mock_repo)
            result = service.get_producer_sales("producer-456")

        assert len(result["orders"]) == 1
        assert result["orders"][0]["id"] == "order-1"
        assert result["current_month_total"] == 50000.0
        assert result["previous_month_total"] == 0.0

    def test_calculates_previous_month_total(self):
        """Calcula el total del mes anterior correctamente (Req. 16.2)."""
        item_curr = _make_item("item-1", price=30000.0, quantity=1)  # junio
        item_prev = _make_item("item-2", price=20000.0, quantity=2)  # mayo → 40000

        order_curr = _make_order("o1", items=[item_curr], created_at=_NOW)
        order_prev = _make_order("o2", items=[item_prev], created_at=_PREV)

        mock_repo = MagicMock()
        mock_repo.get_orders_by_producer.return_value = [order_curr, order_prev]

        with patch("services.order_service.datetime") as mock_dt:
            mock_dt.now.return_value = _NOW
            service = self._make_service(mock_repo)
            result = service.get_producer_sales("producer-456")

        assert result["current_month_total"] == 30000.0
        assert result["previous_month_total"] == 40000.0

    def test_old_orders_not_counted_in_monthly_totals(self):
        """Pedidos de hace más de un mes no se cuentan en los totales mensuales."""
        item_old = _make_item(price=100000.0, quantity=1)
        order_old = _make_order("o-old", items=[item_old], created_at=_OLD)

        mock_repo = MagicMock()
        mock_repo.get_orders_by_producer.return_value = [order_old]

        with patch("services.order_service.datetime") as mock_dt:
            mock_dt.now.return_value = _NOW
            service = self._make_service(mock_repo)
            result = service.get_producer_sales("producer-456")

        assert result["current_month_total"] == 0.0
        assert result["previous_month_total"] == 0.0

    def test_date_filter_applied_to_orders_list_only(self):
        """
        El filtro de fechas afecta solo la lista de pedidos, no los totales mensuales (Req. 16.3).
        """
        from datetime import date

        item_curr = _make_item("item-1", price=30000.0, quantity=1)
        item_prev = _make_item("item-2", price=20000.0, quantity=2)

        order_curr = _make_order("o1", items=[item_curr], created_at=_NOW)
        order_prev = _make_order("o2", items=[item_prev], created_at=_PREV)

        mock_repo = MagicMock()
        # Primera llamada (con filtro) → solo pedido del mes en curso
        # Segunda llamada (sin filtro) → todos los pedidos
        mock_repo.get_orders_by_producer.side_effect = [
            [order_curr],
            [order_curr, order_prev],
        ]

        with patch("services.order_service.datetime") as mock_dt:
            mock_dt.now.return_value = _NOW
            service = self._make_service(mock_repo)
            result = service.get_producer_sales(
                "producer-456",
                from_date=date(2024, 6, 1),
                to_date=date(2024, 6, 30),
            )

        # La lista solo tiene el pedido filtrado
        assert len(result["orders"]) == 1
        assert result["orders"][0]["id"] == "o1"

        # Los totales se calculan sobre todos los pedidos
        assert result["current_month_total"] == 30000.0
        assert result["previous_month_total"] == 40000.0

    def test_returns_empty_when_no_producer_orders(self):
        """Retorna lista vacía y totales en cero si el productor no tiene ventas."""
        mock_repo = MagicMock()
        mock_repo.get_orders_by_producer.return_value = []

        with patch("services.order_service.datetime") as mock_dt:
            mock_dt.now.return_value = _NOW
            service = self._make_service(mock_repo)
            result = service.get_producer_sales("producer-no-sales")

        assert result["orders"] == []
        assert result["current_month_total"] == 0.0
        assert result["previous_month_total"] == 0.0

    def test_raises_order_service_error_on_repository_failure(self):
        """Propaga errores del repositorio como OrderServiceError."""
        from repositories.order_repository import OrderRepositoryError
        from services.order_service import OrderServiceError

        mock_repo = MagicMock()
        mock_repo.get_orders_by_producer.side_effect = OrderRepositoryError(
            "Firestore error", "FIRESTORE_READ_ERROR"
        )

        service = self._make_service(mock_repo)

        with pytest.raises(OrderServiceError) as exc_info:
            service.get_producer_sales("producer-456")

        assert exc_info.value.code == "FIRESTORE_READ_ERROR"

    def test_multiple_items_per_order_summed_correctly(self):
        """Múltiples ítems del productor en un pedido se suman correctamente."""
        items = [
            _make_item("item-1", price=10000.0, quantity=2),   # 20000
            _make_item("item-2", price=15000.0, quantity=3),   # 45000
        ]
        order = _make_order(items=items, created_at=_NOW)

        mock_repo = MagicMock()
        mock_repo.get_orders_by_producer.return_value = [order]

        with patch("services.order_service.datetime") as mock_dt:
            mock_dt.now.return_value = _NOW
            service = self._make_service(mock_repo)
            result = service.get_producer_sales("producer-456")

        assert result["current_month_total"] == 65000.0

    def test_january_previous_month_is_december_of_prior_year(self):
        """En enero, el mes anterior es diciembre del año anterior."""
        january = datetime(2024, 1, 15, 12, 0, 0, tzinfo=timezone.utc)
        december_prev = datetime(2023, 12, 10, 8, 0, 0, tzinfo=timezone.utc)

        item_jan = _make_item("item-1", price=50000.0, quantity=1)
        item_dec = _make_item("item-2", price=30000.0, quantity=1)

        order_jan = _make_order("o-jan", items=[item_jan], created_at=january)
        order_dec = _make_order("o-dec", items=[item_dec], created_at=december_prev)

        mock_repo = MagicMock()
        mock_repo.get_orders_by_producer.return_value = [order_jan, order_dec]

        with patch("services.order_service.datetime") as mock_dt:
            mock_dt.now.return_value = january
            service = self._make_service(mock_repo)
            result = service.get_producer_sales("producer-456")

        assert result["current_month_total"] == 50000.0
        assert result["previous_month_total"] == 30000.0
