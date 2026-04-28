"""
test_cart.py – Tests para los endpoints del carrito de compras.

Cubre:
  - GET  /api/cart                  (Req. 12.1, 12.6)
  - POST /api/cart/items            (Req. 12.1, 8.4)
  - PUT  /api/cart/items/:itemId    (Req. 12.2)
  - DELETE /api/cart/items/:itemId  (Req. 12.3)

Tests unitarios del CartService:
  - Cálculo de subtotales y total (Req. 12.2)
  - Bloqueo de productos inactivos (Req. 8.4)
  - Persistencia del carrito (Req. 12.6)
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


def _make_cart(user_id="user-123", items=None, total=0.0):
    return {
        "user_id": user_id,
        "items": items or [],
        "total": total,
        "updated_at": _NOW,
    }


def _make_item(item_id="item-1", product_id="prod-1", product_name="Cafe Especial",
               price=25000.0, quantity=2, subtotal=50000.0):
    return {
        "id": item_id,
        "product_id": product_id,
        "product_name": product_name,
        "price": price,
        "quantity": quantity,
        "subtotal": subtotal,
        "added_at": _NOW,
    }


def _make_product(product_id="prod-1", name="Cafe Especial", price=25000.0, status="active"):
    return {
        "id": product_id,
        "name": name,
        "price": price,
        "status": status,
        "producerId": "producer-1",
        "producerName": "Finca El Paraiso",
        "description": "Cafe de altura",
        "createdAt": _NOW,
        "updatedAt": _NOW,
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
# Tests – GET /api/cart
# ---------------------------------------------------------------------------

class TestGetCart:

    def test_returns_empty_cart_for_new_user(self, client, consumer_token_headers):
        empty_cart = _make_cart()

        with patch("routes.cart.CartService") as mock_cls:
            mock_svc = MagicMock()
            mock_cls.return_value = mock_svc
            mock_svc.get_cart.return_value = empty_cart

            response = client.get("/api/cart", headers=consumer_token_headers)

        assert response.status_code == 200
        body = response.json()
        assert "data" in body
        assert body["data"]["user_id"] == "user-123"
        assert body["data"]["items"] == []
        assert body["data"]["total"] == 0.0

    def test_returns_cart_with_items_and_total(self, client, consumer_token_headers):
        item = _make_item()
        cart = _make_cart(items=[item], total=50000.0)

        with patch("routes.cart.CartService") as mock_cls:
            mock_svc = MagicMock()
            mock_cls.return_value = mock_svc
            mock_svc.get_cart.return_value = cart

            response = client.get("/api/cart", headers=consumer_token_headers)

        assert response.status_code == 200
        data = response.json()["data"]
        assert len(data["items"]) == 1
        assert data["total"] == 50000.0
        assert data["items"][0]["subtotal"] == 50000.0

    def test_requires_authentication(self, client):
        response = client.get("/api/cart")
        assert response.status_code == 401

    def test_requires_consumer_role(self, client, producer_token_headers):
        response = client.get("/api/cart", headers=producer_token_headers)
        assert response.status_code == 403

    def test_service_called_with_user_id(self, client, consumer_token_headers):
        cart = _make_cart()

        with patch("routes.cart.CartService") as mock_cls:
            mock_svc = MagicMock()
            mock_cls.return_value = mock_svc
            mock_svc.get_cart.return_value = cart

            client.get("/api/cart", headers=consumer_token_headers)

        mock_svc.get_cart.assert_called_once_with("user-123")


# ---------------------------------------------------------------------------
# Tests – POST /api/cart/items
# ---------------------------------------------------------------------------

class TestAddCartItem:

    def test_adds_active_product_to_cart(self, client, consumer_token_headers):
        item = _make_item()
        cart = _make_cart(items=[item], total=50000.0)

        with patch("routes.cart.CartService") as mock_cls:
            mock_svc = MagicMock()
            mock_cls.return_value = mock_svc
            mock_svc.add_item.return_value = cart

            response = client.post(
                "/api/cart/items",
                json={"product_id": "prod-1", "quantity": 2},
                headers=consumer_token_headers,
            )

        assert response.status_code == 201
        body = response.json()
        assert "message" in body
        assert "data" in body
        assert len(body["data"]["items"]) == 1

    def test_returns_400_for_inactive_product(self, client, consumer_token_headers):
        from services.cart_service import CartProductInactiveError

        with patch("routes.cart.CartService") as mock_cls:
            mock_svc = MagicMock()
            mock_cls.return_value = mock_svc
            mock_svc.add_item.side_effect = CartProductInactiveError("prod-inactive")

            response = client.post(
                "/api/cart/items",
                json={"product_id": "prod-inactive", "quantity": 1},
                headers=consumer_token_headers,
            )

        assert response.status_code == 400
        error = response.json()["detail"]["error"]
        assert error["code"] == "PRODUCT_INACTIVE"

    def test_returns_404_for_nonexistent_product(self, client, consumer_token_headers):
        from services.cart_service import CartProductNotFoundError

        with patch("routes.cart.CartService") as mock_cls:
            mock_svc = MagicMock()
            mock_cls.return_value = mock_svc
            mock_svc.add_item.side_effect = CartProductNotFoundError("nonexistent")

            response = client.post(
                "/api/cart/items",
                json={"product_id": "nonexistent", "quantity": 1},
                headers=consumer_token_headers,
            )

        assert response.status_code == 404
        error = response.json()["detail"]["error"]
        assert error["code"] == "PRODUCT_NOT_FOUND"

    def test_returns_422_for_zero_quantity(self, client, consumer_token_headers):
        response = client.post(
            "/api/cart/items",
            json={"product_id": "prod-1", "quantity": 0},
            headers=consumer_token_headers,
        )
        assert response.status_code == 422

    def test_returns_422_for_negative_quantity(self, client, consumer_token_headers):
        response = client.post(
            "/api/cart/items",
            json={"product_id": "prod-1", "quantity": -1},
            headers=consumer_token_headers,
        )
        assert response.status_code == 422

    def test_requires_authentication(self, client):
        response = client.post(
            "/api/cart/items",
            json={"product_id": "prod-1", "quantity": 1},
        )
        assert response.status_code == 401

    def test_requires_consumer_role(self, client, producer_token_headers):
        response = client.post(
            "/api/cart/items",
            json={"product_id": "prod-1", "quantity": 1},
            headers=producer_token_headers,
        )
        assert response.status_code == 403

    def test_service_called_with_correct_params(self, client, consumer_token_headers):
        cart = _make_cart()

        with patch("routes.cart.CartService") as mock_cls:
            mock_svc = MagicMock()
            mock_cls.return_value = mock_svc
            mock_svc.add_item.return_value = cart

            client.post(
                "/api/cart/items",
                json={"product_id": "prod-1", "quantity": 3},
                headers=consumer_token_headers,
            )

        mock_svc.add_item.assert_called_once_with(
            user_id="user-123",
            product_id="prod-1",
            quantity=3,
        )


# ---------------------------------------------------------------------------
# Tests – PUT /api/cart/items/:itemId
# ---------------------------------------------------------------------------

class TestUpdateCartItem:

    def test_updates_quantity_and_recalculates_total(self, client, consumer_token_headers):
        item = _make_item(quantity=5, subtotal=125000.0)
        cart = _make_cart(items=[item], total=125000.0)

        with patch("routes.cart.CartService") as mock_cls:
            mock_svc = MagicMock()
            mock_cls.return_value = mock_svc
            mock_svc.update_item.return_value = cart

            response = client.put(
                "/api/cart/items/item-1",
                json={"quantity": 5},
                headers=consumer_token_headers,
            )

        assert response.status_code == 200
        body = response.json()
        assert body["data"]["total"] == 125000.0
        assert body["data"]["items"][0]["quantity"] == 5

    def test_returns_404_for_nonexistent_item(self, client, consumer_token_headers):
        from services.cart_service import CartItemNotFoundServiceError

        with patch("routes.cart.CartService") as mock_cls:
            mock_svc = MagicMock()
            mock_cls.return_value = mock_svc
            mock_svc.update_item.side_effect = CartItemNotFoundServiceError("nonexistent-item")

            response = client.put(
                "/api/cart/items/nonexistent-item",
                json={"quantity": 2},
                headers=consumer_token_headers,
            )

        assert response.status_code == 404
        error = response.json()["detail"]["error"]
        assert error["code"] == "CART_ITEM_NOT_FOUND"

    def test_returns_422_for_zero_quantity(self, client, consumer_token_headers):
        response = client.put(
            "/api/cart/items/item-1",
            json={"quantity": 0},
            headers=consumer_token_headers,
        )
        assert response.status_code == 422

    def test_requires_authentication(self, client):
        response = client.put("/api/cart/items/item-1", json={"quantity": 2})
        assert response.status_code == 401

    def test_requires_consumer_role(self, client, producer_token_headers):
        response = client.put(
            "/api/cart/items/item-1",
            json={"quantity": 2},
            headers=producer_token_headers,
        )
        assert response.status_code == 403

    def test_service_called_with_correct_params(self, client, consumer_token_headers):
        cart = _make_cart()

        with patch("routes.cart.CartService") as mock_cls:
            mock_svc = MagicMock()
            mock_cls.return_value = mock_svc
            mock_svc.update_item.return_value = cart

            client.put(
                "/api/cart/items/item-1",
                json={"quantity": 4},
                headers=consumer_token_headers,
            )

        mock_svc.update_item.assert_called_once_with(
            user_id="user-123",
            item_id="item-1",
            quantity=4,
        )


# ---------------------------------------------------------------------------
# Tests – DELETE /api/cart/items/:itemId
# ---------------------------------------------------------------------------

class TestDeleteCartItem:

    def test_removes_item_and_recalculates_total(self, client, consumer_token_headers):
        cart = _make_cart(items=[], total=0.0)

        with patch("routes.cart.CartService") as mock_cls:
            mock_svc = MagicMock()
            mock_cls.return_value = mock_svc
            mock_svc.delete_item.return_value = cart

            response = client.delete(
                "/api/cart/items/item-1",
                headers=consumer_token_headers,
            )

        assert response.status_code == 200
        body = response.json()
        assert "message" in body
        assert body["data"]["items"] == []
        assert body["data"]["total"] == 0.0

    def test_returns_404_for_nonexistent_item(self, client, consumer_token_headers):
        from services.cart_service import CartItemNotFoundServiceError

        with patch("routes.cart.CartService") as mock_cls:
            mock_svc = MagicMock()
            mock_cls.return_value = mock_svc
            mock_svc.delete_item.side_effect = CartItemNotFoundServiceError("nonexistent-item")

            response = client.delete(
                "/api/cart/items/nonexistent-item",
                headers=consumer_token_headers,
            )

        assert response.status_code == 404
        error = response.json()["detail"]["error"]
        assert error["code"] == "CART_ITEM_NOT_FOUND"

    def test_requires_authentication(self, client):
        response = client.delete("/api/cart/items/item-1")
        assert response.status_code == 401

    def test_requires_consumer_role(self, client, producer_token_headers):
        response = client.delete(
            "/api/cart/items/item-1",
            headers=producer_token_headers,
        )
        assert response.status_code == 403

    def test_service_called_with_correct_params(self, client, consumer_token_headers):
        cart = _make_cart()

        with patch("routes.cart.CartService") as mock_cls:
            mock_svc = MagicMock()
            mock_cls.return_value = mock_svc
            mock_svc.delete_item.return_value = cart

            client.delete("/api/cart/items/item-1", headers=consumer_token_headers)

        mock_svc.delete_item.assert_called_once_with(
            user_id="user-123",
            item_id="item-1",
        )


# ---------------------------------------------------------------------------
# Tests unitarios – CartService (lógica de negocio)
# ---------------------------------------------------------------------------

class TestCartServiceGetCart:

    def _make_service(self, mock_cart_repo, mock_product_repo=None):
        from services.cart_service import CartService
        return CartService(
            cart_repository=mock_cart_repo,
            product_repository=mock_product_repo or MagicMock(),
        )

    def test_returns_empty_cart(self):
        mock_repo = MagicMock()
        mock_repo.get_or_create_cart.return_value = {"userId": "user-1", "updatedAt": _NOW}
        mock_repo.get_items.return_value = []

        service = self._make_service(mock_repo)
        result = service.get_cart("user-1")

        assert result["user_id"] == "user-1"
        assert result["items"] == []
        assert result["total"] == 0.0

    def test_calculates_subtotals_and_total(self):
        mock_repo = MagicMock()
        mock_repo.get_or_create_cart.return_value = {"userId": "user-1", "updatedAt": _NOW}
        mock_repo.get_items.return_value = [
            {"id": "i1", "productId": "p1", "productName": "Cafe A", "price": 10000.0, "quantity": 2, "addedAt": _NOW},
            {"id": "i2", "productId": "p2", "productName": "Cafe B", "price": 5000.0, "quantity": 3, "addedAt": _NOW},
        ]

        service = self._make_service(mock_repo)
        result = service.get_cart("user-1")

        # subtotal i1 = 10000 * 2 = 20000
        # subtotal i2 = 5000 * 3 = 15000
        # total = 35000
        assert result["items"][0]["subtotal"] == 20000.0
        assert result["items"][1]["subtotal"] == 15000.0
        assert result["total"] == 35000.0


class TestCartServiceAddItem:

    def _make_service(self, mock_cart_repo, mock_product_repo):
        from services.cart_service import CartService
        return CartService(
            cart_repository=mock_cart_repo,
            product_repository=mock_product_repo,
        )

    def test_adds_active_product_successfully(self):
        mock_product_repo = MagicMock()
        mock_product_repo.get_by_id.return_value = _make_product()

        mock_cart_repo = MagicMock()
        mock_cart_repo.get_item_by_product_id.return_value = None
        mock_cart_repo.get_or_create_cart.return_value = {"userId": "user-1", "updatedAt": _NOW}
        mock_cart_repo.get_items.return_value = [
            {"id": "i1", "productId": "prod-1", "productName": "Cafe Especial",
             "price": 25000.0, "quantity": 1, "addedAt": _NOW}
        ]

        service = self._make_service(mock_cart_repo, mock_product_repo)
        result = service.add_item("user-1", "prod-1", 1)

        mock_cart_repo.add_item.assert_called_once()
        assert result["total"] == 25000.0

    def test_raises_error_for_inactive_product(self):
        from services.cart_service import CartProductInactiveError

        mock_product_repo = MagicMock()
        mock_product_repo.get_by_id.return_value = _make_product(status="inactive")

        mock_cart_repo = MagicMock()
        service = self._make_service(mock_cart_repo, mock_product_repo)

        with pytest.raises(CartProductInactiveError):
            service.add_item("user-1", "prod-inactive", 1)

    def test_raises_error_for_nonexistent_product(self):
        from services.cart_service import CartProductNotFoundError

        mock_product_repo = MagicMock()
        mock_product_repo.get_by_id.return_value = None

        mock_cart_repo = MagicMock()
        service = self._make_service(mock_cart_repo, mock_product_repo)

        with pytest.raises(CartProductNotFoundError):
            service.add_item("user-1", "nonexistent", 1)

    def test_increments_quantity_if_product_already_in_cart(self):
        mock_product_repo = MagicMock()
        mock_product_repo.get_by_id.return_value = _make_product()

        existing_item = {
            "id": "item-1", "productId": "prod-1", "productName": "Cafe Especial",
            "price": 25000.0, "quantity": 2, "addedAt": _NOW
        }
        mock_cart_repo = MagicMock()
        mock_cart_repo.get_item_by_product_id.return_value = existing_item
        mock_cart_repo.get_or_create_cart.return_value = {"userId": "user-1", "updatedAt": _NOW}
        mock_cart_repo.get_items.return_value = [
            {**existing_item, "quantity": 5}  # after update
        ]

        service = self._make_service(mock_cart_repo, mock_product_repo)
        service.add_item("user-1", "prod-1", 3)

        # Should call update_item with new quantity = 2 + 3 = 5
        mock_cart_repo.update_item.assert_called_once_with("user-1", "item-1", {"quantity": 5})
        mock_cart_repo.add_item.assert_not_called()

    def test_denormalizes_product_name_and_price(self):
        mock_product_repo = MagicMock()
        mock_product_repo.get_by_id.return_value = _make_product(
            name="Cafe Premium", price=30000.0
        )

        mock_cart_repo = MagicMock()
        mock_cart_repo.get_item_by_product_id.return_value = None
        mock_cart_repo.get_or_create_cart.return_value = {"userId": "user-1", "updatedAt": _NOW}
        mock_cart_repo.get_items.return_value = []

        service = self._make_service(mock_cart_repo, mock_product_repo)
        service.add_item("user-1", "prod-1", 1)

        call_args = mock_cart_repo.add_item.call_args
        item_fields = call_args[0][1]  # second positional arg
        assert item_fields["productName"] == "Cafe Premium"
        assert item_fields["price"] == 30000.0


class TestCartServiceUpdateItem:

    def _make_service(self, mock_cart_repo):
        from services.cart_service import CartService
        return CartService(
            cart_repository=mock_cart_repo,
            product_repository=MagicMock(),
        )

    def test_updates_quantity_successfully(self):
        mock_repo = MagicMock()
        mock_repo.get_or_create_cart.return_value = {"userId": "user-1", "updatedAt": _NOW}
        mock_repo.get_items.return_value = [
            {"id": "i1", "productId": "p1", "productName": "Cafe", "price": 10000.0, "quantity": 5, "addedAt": _NOW}
        ]

        service = self._make_service(mock_repo)
        result = service.update_item("user-1", "i1", 5)

        mock_repo.update_item.assert_called_once_with("user-1", "i1", {"quantity": 5})
        assert result["total"] == 50000.0

    def test_raises_error_for_nonexistent_item(self):
        from repositories.cart_repository import CartItemNotFoundError
        from services.cart_service import CartItemNotFoundServiceError

        mock_repo = MagicMock()
        mock_repo.update_item.side_effect = CartItemNotFoundError("nonexistent")

        service = self._make_service(mock_repo)

        with pytest.raises(CartItemNotFoundServiceError):
            service.update_item("user-1", "nonexistent", 2)


class TestCartServiceDeleteItem:

    def _make_service(self, mock_cart_repo):
        from services.cart_service import CartService
        return CartService(
            cart_repository=mock_cart_repo,
            product_repository=MagicMock(),
        )

    def test_deletes_item_and_returns_updated_cart(self):
        mock_repo = MagicMock()
        mock_repo.get_or_create_cart.return_value = {"userId": "user-1", "updatedAt": _NOW}
        mock_repo.get_items.return_value = []  # empty after deletion

        service = self._make_service(mock_repo)
        result = service.delete_item("user-1", "i1")

        mock_repo.delete_item.assert_called_once_with("user-1", "i1")
        assert result["items"] == []
        assert result["total"] == 0.0

    def test_raises_error_for_nonexistent_item(self):
        from repositories.cart_repository import CartItemNotFoundError
        from services.cart_service import CartItemNotFoundServiceError

        mock_repo = MagicMock()
        mock_repo.delete_item.side_effect = CartItemNotFoundError("nonexistent")

        service = self._make_service(mock_repo)

        with pytest.raises(CartItemNotFoundServiceError):
            service.delete_item("user-1", "nonexistent")


# ---------------------------------------------------------------------------
# Tests – Cálculo de subtotales y total (Propiedad 18)
# ---------------------------------------------------------------------------

class TestCartCalculations:
    """
    Verifica la invariante de cálculo del carrito:
    subtotal = precio × cantidad, total = suma de subtotales.
    Valida: Requerimientos 12.1, 12.2, 12.3
    """

    def _make_service(self, items):
        from services.cart_service import CartService
        mock_cart_repo = MagicMock()
        mock_cart_repo.get_or_create_cart.return_value = {"userId": "user-1", "updatedAt": _NOW}
        mock_cart_repo.get_items.return_value = items
        return CartService(
            cart_repository=mock_cart_repo,
            product_repository=MagicMock(),
        )

    def test_single_item_subtotal_equals_price_times_quantity(self):
        items = [
            {"id": "i1", "productId": "p1", "productName": "Cafe", "price": 12500.0, "quantity": 4, "addedAt": _NOW}
        ]
        service = self._make_service(items)
        result = service.get_cart("user-1")

        assert result["items"][0]["subtotal"] == 50000.0
        assert result["total"] == 50000.0

    def test_total_equals_sum_of_subtotals(self):
        items = [
            {"id": "i1", "productId": "p1", "productName": "A", "price": 10000.0, "quantity": 1, "addedAt": _NOW},
            {"id": "i2", "productId": "p2", "productName": "B", "price": 20000.0, "quantity": 2, "addedAt": _NOW},
            {"id": "i3", "productId": "p3", "productName": "C", "price": 5000.0, "quantity": 3, "addedAt": _NOW},
        ]
        service = self._make_service(items)
        result = service.get_cart("user-1")

        expected_subtotals = [10000.0, 40000.0, 15000.0]
        for i, expected in enumerate(expected_subtotals):
            assert result["items"][i]["subtotal"] == expected

        assert result["total"] == sum(expected_subtotals)

    def test_empty_cart_total_is_zero(self):
        service = self._make_service([])
        result = service.get_cart("user-1")

        assert result["total"] == 0.0
        assert result["items"] == []

    def test_subtotal_precision(self):
        """Verifica que el cálculo maneja decimales correctamente."""
        items = [
            {"id": "i1", "productId": "p1", "productName": "Cafe", "price": 3333.33, "quantity": 3, "addedAt": _NOW}
        ]
        service = self._make_service(items)
        result = service.get_cart("user-1")

        # 3333.33 * 3 = 9999.99
        assert result["items"][0]["subtotal"] == 9999.99
        assert result["total"] == 9999.99
