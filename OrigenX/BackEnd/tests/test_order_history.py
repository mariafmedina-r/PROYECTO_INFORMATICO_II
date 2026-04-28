"""
test_order_history.py – Tests para el historial de pedidos del consumidor.

Cubre:
  - GET  /api/orders        → Historial de pedidos (Req. 15.1)
  - GET  /api/orders/:id    → Detalle de pedido (Req. 15.2, 15.3)

Tests unitarios del OrderService:
  - get_consumer_orders: retorna pedidos ordenados por createdAt desc (Req. 15.1)
  - get_order_detail: retorna detalle completo con ítems (Req. 15.2)
  - get_order_detail: verifica que el pedido pertenece al consumidor
  - Historial permanente: pedidos no se eliminan (Req. 15.3)
"""

from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from main import app


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_NOW = datetime(2024, 6, 1, 12, 0, 0, tzinfo=timezone.utc)
_EARLIER = datetime(2024, 5, 15, 8, 0, 0, tzinfo=timezone.utc)
_EARLIEST = datetime(2024, 4, 1, 10, 0, 0, tzinfo=timezone.utc)


def _make_order(
    order_id="order-1",
    consumer_id="user-123",
    total=75000.0,
    status="pendiente",
    created_at=None,
    items=None,
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
        "shippingCompany": "Servientrega",
        "shippingCost": 5000.0,
        "total": total,
        "status": status,
        "transactionId": None,
        "createdAt": created_at or _NOW,
        "updatedAt": created_at or _NOW,
        "items": items or [],
    }


def _make_item(
    item_id="item-1",
    product_id="prod-1",
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
def consumer_token_headers(mock_firebase_auth):
    """Simula un token válido de consumidor."""
    mock_firebase_auth.verify_id_token.return_value = {
        "uid": "user-123",
        "email": "consumer@test.com",
        "role": "CONSUMER",
    }
    return {"Authorization": "Bearer valid-consumer-token"}


@pytest.fixture
def producer_token_headers(mock_firebase_auth):
    """Simula un token válido de productor."""
    mock_firebase_auth.verify_id_token.return_value = {
        "uid": "producer-456",
        "email": "producer@test.com",
        "role": "PRODUCER",
    }
    return {"Authorization": "Bearer valid-producer-token"}


# ---------------------------------------------------------------------------
# Tests – GET /api/orders (Req. 15.1)
# ---------------------------------------------------------------------------


class TestGetOrderHistory:
    """Tests para el historial de pedidos del consumidor (Req. 15.1)."""

    def test_returns_empty_list_when_no_orders(self, client, consumer_token_headers):
        """Consumidor sin pedidos recibe lista vacía."""
        with patch("routes.orders.OrderService") as mock_cls:
            mock_svc = MagicMock()
            mock_cls.return_value = mock_svc
            mock_svc.get_consumer_orders.return_value = []

            response = client.get("/api/orders", headers=consumer_token_headers)

        assert response.status_code == 200
        body = response.json()
        assert "data" in body
        assert body["data"] == []

    def test_returns_orders_with_required_fields(self, client, consumer_token_headers):
        """Cada pedido incluye id, total, status y createdAt (Req. 15.1)."""
        order = _make_order()

        with patch("routes.orders.OrderService") as mock_cls:
            mock_svc = MagicMock()
            mock_cls.return_value = mock_svc
            mock_svc.get_consumer_orders.return_value = [order]

            response = client.get("/api/orders", headers=consumer_token_headers)

        assert response.status_code == 200
        data = response.json()["data"]
        assert len(data) == 1
        order_data = data[0]
        assert order_data["id"] == "order-1"
        assert order_data["total"] == 75000.0
        assert order_data["status"] == "pendiente"
        assert "createdAt" in order_data

    def test_returns_multiple_orders(self, client, consumer_token_headers):
        """Retorna múltiples pedidos correctamente."""
        orders = [
            _make_order("order-3", total=90000.0, created_at=_NOW),
            _make_order("order-2", total=50000.0, created_at=_EARLIER),
            _make_order("order-1", total=30000.0, created_at=_EARLIEST),
        ]

        with patch("routes.orders.OrderService") as mock_cls:
            mock_svc = MagicMock()
            mock_cls.return_value = mock_svc
            mock_svc.get_consumer_orders.return_value = orders

            response = client.get("/api/orders", headers=consumer_token_headers)

        assert response.status_code == 200
        data = response.json()["data"]
        assert len(data) == 3
        # El servicio ya retorna ordenados por createdAt desc; verificar el orden
        assert data[0]["id"] == "order-3"
        assert data[1]["id"] == "order-2"
        assert data[2]["id"] == "order-1"

    def test_service_called_with_consumer_id(self, client, consumer_token_headers):
        """El servicio recibe el UID del consumidor autenticado."""
        with patch("routes.orders.OrderService") as mock_cls:
            mock_svc = MagicMock()
            mock_cls.return_value = mock_svc
            mock_svc.get_consumer_orders.return_value = []

            client.get("/api/orders", headers=consumer_token_headers)

        mock_svc.get_consumer_orders.assert_called_once_with("user-123")

    def test_requires_authentication(self, client):
        """Sin token retorna 401."""
        response = client.get("/api/orders")
        assert response.status_code == 401

    def test_requires_consumer_role(self, client, producer_token_headers):
        """Rol PRODUCER no puede acceder al historial de consumidor."""
        response = client.get("/api/orders", headers=producer_token_headers)
        assert response.status_code == 403

    def test_returns_500_on_service_error(self, client, consumer_token_headers):
        """Error interno del servicio retorna 500."""
        from services.order_service import OrderServiceError

        with patch("routes.orders.OrderService") as mock_cls:
            mock_svc = MagicMock()
            mock_cls.return_value = mock_svc
            mock_svc.get_consumer_orders.side_effect = OrderServiceError(
                "Error de Firestore", "FIRESTORE_READ_ERROR"
            )

            response = client.get("/api/orders", headers=consumer_token_headers)

        assert response.status_code == 500
        error = response.json()["detail"]["error"]
        assert error["code"] == "FIRESTORE_READ_ERROR"

    def test_orders_include_shipping_company(self, client, consumer_token_headers):
        """Los pedidos incluyen la empresa de envío."""
        order = _make_order()

        with patch("routes.orders.OrderService") as mock_cls:
            mock_svc = MagicMock()
            mock_cls.return_value = mock_svc
            mock_svc.get_consumer_orders.return_value = [order]

            response = client.get("/api/orders", headers=consumer_token_headers)

        data = response.json()["data"]
        assert data[0]["shippingCompany"] == "Servientrega"


# ---------------------------------------------------------------------------
# Tests – GET /api/orders/:id (Req. 15.2)
# ---------------------------------------------------------------------------


class TestGetOrderDetail:
    """Tests para el detalle de pedido del consumidor (Req. 15.2)."""

    def test_returns_full_order_detail(self, client, consumer_token_headers):
        """Retorna el pedido completo con todos los campos (Req. 15.2)."""
        items = [_make_item(), _make_item("item-2", "prod-2", "Café Orgánico", 30000.0, 1)]
        order = _make_order(items=items)

        with patch("routes.orders.OrderService") as mock_cls:
            mock_svc = MagicMock()
            mock_cls.return_value = mock_svc
            mock_svc.get_order_detail.return_value = order

            response = client.get("/api/orders/order-1", headers=consumer_token_headers)

        assert response.status_code == 200
        data = response.json()["data"]
        assert data["id"] == "order-1"
        assert data["total"] == 75000.0
        assert data["status"] == "pendiente"
        assert data["shippingCompany"] == "Servientrega"
        assert "addressSnapshot" in data
        assert len(data["items"]) == 2

    def test_detail_includes_items_with_quantities_and_prices(self, client, consumer_token_headers):
        """Los ítems incluyen productNameSnapshot, priceSnapshot y quantity (Req. 15.2)."""
        item = _make_item(price=25000.0, quantity=3)
        order = _make_order(items=[item])

        with patch("routes.orders.OrderService") as mock_cls:
            mock_svc = MagicMock()
            mock_cls.return_value = mock_svc
            mock_svc.get_order_detail.return_value = order

            response = client.get("/api/orders/order-1", headers=consumer_token_headers)

        data = response.json()["data"]
        item_data = data["items"][0]
        assert item_data["productNameSnapshot"] == "Café Especial"
        assert item_data["priceSnapshot"] == 25000.0
        assert item_data["quantity"] == 3

    def test_detail_includes_address_snapshot(self, client, consumer_token_headers):
        """El detalle incluye la dirección de envío (Req. 15.2)."""
        order = _make_order()

        with patch("routes.orders.OrderService") as mock_cls:
            mock_svc = MagicMock()
            mock_cls.return_value = mock_svc
            mock_svc.get_order_detail.return_value = order

            response = client.get("/api/orders/order-1", headers=consumer_token_headers)

        data = response.json()["data"]
        addr = data["addressSnapshot"]
        assert addr["street"] == "Calle 10 # 5-20"
        assert addr["city"] == "Bogotá"
        assert addr["department"] == "Cundinamarca"

    def test_returns_404_for_nonexistent_order(self, client, consumer_token_headers):
        """Pedido inexistente retorna 404."""
        from services.order_service import OrderNotFoundError

        with patch("routes.orders.OrderService") as mock_cls:
            mock_svc = MagicMock()
            mock_cls.return_value = mock_svc
            mock_svc.get_order_detail.side_effect = OrderNotFoundError("nonexistent-order")

            response = client.get("/api/orders/nonexistent-order", headers=consumer_token_headers)

        assert response.status_code == 404
        error = response.json()["detail"]["error"]
        assert error["code"] == "ORDER_NOT_FOUND"

    def test_returns_404_for_order_belonging_to_other_consumer(self, client, consumer_token_headers):
        """Pedido de otro consumidor retorna 404 (no revela existencia)."""
        from services.order_service import OrderNotFoundError

        with patch("routes.orders.OrderService") as mock_cls:
            mock_svc = MagicMock()
            mock_cls.return_value = mock_svc
            mock_svc.get_order_detail.side_effect = OrderNotFoundError("other-order")

            response = client.get("/api/orders/other-order", headers=consumer_token_headers)

        assert response.status_code == 404

    def test_service_called_with_correct_params(self, client, consumer_token_headers):
        """El servicio recibe order_id y consumer_id correctos."""
        order = _make_order()

        with patch("routes.orders.OrderService") as mock_cls:
            mock_svc = MagicMock()
            mock_cls.return_value = mock_svc
            mock_svc.get_order_detail.return_value = order

            client.get("/api/orders/order-1", headers=consumer_token_headers)

        mock_svc.get_order_detail.assert_called_once_with(
            order_id="order-1",
            consumer_id="user-123",
        )

    def test_requires_authentication(self, client):
        """Sin token retorna 401."""
        response = client.get("/api/orders/order-1")
        assert response.status_code == 401

    def test_requires_consumer_role(self, client, producer_token_headers):
        """Rol PRODUCER no puede acceder al detalle de pedido del consumidor."""
        response = client.get("/api/orders/order-1", headers=producer_token_headers)
        assert response.status_code == 403

    def test_returns_500_on_service_error(self, client, consumer_token_headers):
        """Error interno del servicio retorna 500."""
        from services.order_service import OrderServiceError

        with patch("routes.orders.OrderService") as mock_cls:
            mock_svc = MagicMock()
            mock_cls.return_value = mock_svc
            mock_svc.get_order_detail.side_effect = OrderServiceError(
                "Error de Firestore", "FIRESTORE_READ_ERROR"
            )

            response = client.get("/api/orders/order-1", headers=consumer_token_headers)

        assert response.status_code == 500

    def test_timestamps_serialized_as_iso_strings(self, client, consumer_token_headers):
        """Los timestamps se serializan como strings ISO 8601."""
        order = _make_order()

        with patch("routes.orders.OrderService") as mock_cls:
            mock_svc = MagicMock()
            mock_cls.return_value = mock_svc
            mock_svc.get_order_detail.return_value = order

            response = client.get("/api/orders/order-1", headers=consumer_token_headers)

        data = response.json()["data"]
        # createdAt debe ser un string ISO, no un objeto datetime
        assert isinstance(data["createdAt"], str)
        assert "2024-06-01" in data["createdAt"]


# ---------------------------------------------------------------------------
# Tests unitarios – OrderService (lógica de negocio)
# ---------------------------------------------------------------------------


class TestOrderServiceGetConsumerOrders:
    """Tests unitarios del método get_consumer_orders (Req. 15.1)."""

    def _make_service(self, mock_order_repo):
        from services.order_service import OrderService

        return OrderService(order_repository=mock_order_repo)

    def test_returns_orders_from_repository(self):
        """Retorna los pedidos que devuelve el repositorio."""
        orders = [_make_order("o1"), _make_order("o2")]
        mock_repo = MagicMock()
        mock_repo.get_orders_by_consumer.return_value = orders

        service = self._make_service(mock_repo)
        result = service.get_consumer_orders("user-123")

        assert result == orders
        mock_repo.get_orders_by_consumer.assert_called_once_with("user-123")

    def test_returns_empty_list_when_no_orders(self):
        """Retorna lista vacía si el consumidor no tiene pedidos."""
        mock_repo = MagicMock()
        mock_repo.get_orders_by_consumer.return_value = []

        service = self._make_service(mock_repo)
        result = service.get_consumer_orders("user-no-orders")

        assert result == []

    def test_raises_order_service_error_on_repository_failure(self):
        """Propaga errores del repositorio como OrderServiceError."""
        from repositories.order_repository import OrderRepositoryError
        from services.order_service import OrderServiceError

        mock_repo = MagicMock()
        mock_repo.get_orders_by_consumer.side_effect = OrderRepositoryError(
            "Firestore error", "FIRESTORE_READ_ERROR"
        )

        service = self._make_service(mock_repo)

        with pytest.raises(OrderServiceError) as exc_info:
            service.get_consumer_orders("user-123")

        assert exc_info.value.code == "FIRESTORE_READ_ERROR"

    def test_orders_ordered_by_created_at_descending(self):
        """
        El repositorio retorna pedidos ordenados por createdAt desc (Req. 15.1).
        El servicio no reordena; confía en el repositorio.
        """
        orders = [
            _make_order("o3", created_at=_NOW),
            _make_order("o2", created_at=_EARLIER),
            _make_order("o1", created_at=_EARLIEST),
        ]
        mock_repo = MagicMock()
        mock_repo.get_orders_by_consumer.return_value = orders

        service = self._make_service(mock_repo)
        result = service.get_consumer_orders("user-123")

        # Verificar que el orden se preserva (más reciente primero)
        assert result[0]["id"] == "o3"
        assert result[1]["id"] == "o2"
        assert result[2]["id"] == "o1"


class TestOrderServiceGetOrderDetail:
    """Tests unitarios del método get_order_detail (Req. 15.2, 15.3)."""

    def _make_service(self, mock_order_repo):
        from services.order_service import OrderService

        return OrderService(order_repository=mock_order_repo)

    def test_returns_order_with_items(self):
        """Retorna el pedido completo con ítems."""
        items = [_make_item()]
        order = _make_order(items=items)
        mock_repo = MagicMock()
        mock_repo.get_by_id.return_value = order

        service = self._make_service(mock_repo)
        result = service.get_order_detail("order-1", "user-123")

        assert result["id"] == "order-1"
        assert len(result["items"]) == 1
        mock_repo.get_by_id.assert_called_once_with("order-1")

    def test_raises_not_found_for_nonexistent_order(self):
        """Lanza OrderNotFoundError si el pedido no existe."""
        from services.order_service import OrderNotFoundError

        mock_repo = MagicMock()
        mock_repo.get_by_id.return_value = None

        service = self._make_service(mock_repo)

        with pytest.raises(OrderNotFoundError):
            service.get_order_detail("nonexistent", "user-123")

    def test_raises_not_found_when_order_belongs_to_other_consumer(self):
        """Lanza OrderNotFoundError si el pedido pertenece a otro consumidor."""
        from services.order_service import OrderNotFoundError

        order = _make_order(consumer_id="other-user")
        mock_repo = MagicMock()
        mock_repo.get_by_id.return_value = order

        service = self._make_service(mock_repo)

        with pytest.raises(OrderNotFoundError):
            service.get_order_detail("order-1", "user-123")

    def test_raises_order_service_error_on_repository_failure(self):
        """Propaga errores del repositorio como OrderServiceError."""
        from repositories.order_repository import OrderRepositoryError
        from services.order_service import OrderServiceError

        mock_repo = MagicMock()
        mock_repo.get_by_id.side_effect = OrderRepositoryError(
            "Firestore error", "FIRESTORE_READ_ERROR"
        )

        service = self._make_service(mock_repo)

        with pytest.raises(OrderServiceError):
            service.get_order_detail("order-1", "user-123")

    def test_order_detail_includes_address_snapshot(self):
        """El detalle incluye el snapshot de dirección (Req. 15.2)."""
        order = _make_order()
        mock_repo = MagicMock()
        mock_repo.get_by_id.return_value = order

        service = self._make_service(mock_repo)
        result = service.get_order_detail("order-1", "user-123")

        assert "addressSnapshot" in result
        assert result["addressSnapshot"]["city"] == "Bogotá"

    def test_order_detail_includes_shipping_company(self):
        """El detalle incluye la empresa de envío (Req. 15.2)."""
        order = _make_order()
        mock_repo = MagicMock()
        mock_repo.get_by_id.return_value = order

        service = self._make_service(mock_repo)
        result = service.get_order_detail("order-1", "user-123")

        assert result["shippingCompany"] == "Servientrega"

    def test_order_detail_includes_status(self):
        """El detalle incluye el estado del pedido (Req. 15.2)."""
        order = _make_order(status="enviado")
        mock_repo = MagicMock()
        mock_repo.get_by_id.return_value = order

        service = self._make_service(mock_repo)
        result = service.get_order_detail("order-1", "user-123")

        assert result["status"] == "enviado"

    def test_history_preserved_permanently(self):
        """
        El historial se preserva permanentemente (Req. 15.3).
        Los pedidos completados o cancelados siguen siendo accesibles.
        """
        for final_status in ["entregado", "cancelado"]:
            order = _make_order(status=final_status)
            mock_repo = MagicMock()
            mock_repo.get_by_id.return_value = order

            service = self._make_service(mock_repo)
            result = service.get_order_detail("order-1", "user-123")

            assert result["status"] == final_status
