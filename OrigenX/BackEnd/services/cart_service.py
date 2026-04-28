"""
services/cart_service.py – Lógica de negocio del carrito de compras.

Responsabilidades:
  - CRUD de ítems del carrito
  - Cálculo de subtotales y total (precio × cantidad)
  - Validación: no agregar productos inactivos (Req. 8.4)
  - Persistencia en Firestore bajo carts/{userId}/items (Req. 12.6)

Requerimientos: 12.1, 12.2, 12.3, 12.4, 12.6, 8.4
"""

import logging
from typing import Optional

from repositories.cart_repository import (
    CartItemNotFoundError,
    CartRepository,
    CartRepositoryError,
)
from repositories.product_repository import ProductRepository, ProductRepositoryError

logger = logging.getLogger(__name__)


class CartServiceError(Exception):
    """Error base del servicio del carrito."""

    def __init__(self, message: str, code: str = "CART_SERVICE_ERROR"):
        self.message = message
        self.code = code
        super().__init__(message)


class CartItemNotFoundServiceError(CartServiceError):
    """El ítem no existe en el carrito."""

    def __init__(self, item_id: str):
        super().__init__(
            message=f"Ítem con id '{item_id}' no encontrado en el carrito.",
            code="CART_ITEM_NOT_FOUND",
        )


class CartProductInactiveError(CartServiceError):
    """El producto está inactivo y no puede agregarse al carrito (Req. 8.4)."""

    def __init__(self, product_id: str):
        super().__init__(
            message=f"El producto '{product_id}' no está disponible actualmente.",
            code="PRODUCT_INACTIVE",
        )


class CartProductNotFoundError(CartServiceError):
    """El producto no existe."""

    def __init__(self, product_id: str):
        super().__init__(
            message=f"Producto con id '{product_id}' no encontrado.",
            code="PRODUCT_NOT_FOUND",
        )


class CartValidationError(CartServiceError):
    """Error de validación de campos del carrito."""

    def __init__(self, message: str, fields: Optional[list] = None):
        super().__init__(message=message, code="VALIDATION_ERROR")
        self.fields = fields or []


def _calculate_subtotal(price: float, quantity: int) -> float:
    """Calcula el subtotal de un ítem: precio × cantidad (Req. 12.2)."""
    return round(price * quantity, 2)


def _calculate_total(items: list[dict]) -> float:
    """Calcula el total del carrito: suma de todos los subtotales (Req. 12.2)."""
    return round(sum(_calculate_subtotal(item["price"], item["quantity"]) for item in items), 2)


def _build_cart_response(user_id: str, cart_doc: dict, items: list[dict]) -> dict:
    """
    Construye la respuesta del carrito con subtotales y total calculados.

    Args:
        user_id: UID del usuario.
        cart_doc: Documento del carrito (contiene updatedAt).
        items: Lista de ítems del carrito desde Firestore.

    Returns:
        Diccionario con la estructura de respuesta del carrito.
    """
    items_response = []
    for item in items:
        price = item.get("price", 0.0)
        quantity = item.get("quantity", 0)
        subtotal = _calculate_subtotal(price, quantity)
        items_response.append({
            "id": item.get("id"),
            "product_id": item.get("productId"),
            "product_name": item.get("productName"),
            "price": price,
            "quantity": quantity,
            "subtotal": subtotal,
            "added_at": item.get("addedAt"),
        })

    total = _calculate_total(items)

    return {
        "user_id": user_id,
        "items": items_response,
        "total": total,
        "updated_at": cart_doc.get("updatedAt"),
    }


class CartService:
    """Servicio de gestión del carrito de compras."""

    def __init__(
        self,
        cart_repository: Optional[CartRepository] = None,
        product_repository: Optional[ProductRepository] = None,
    ):
        self._cart_repo = cart_repository or CartRepository()
        self._product_repo = product_repository or ProductRepository()

    # ------------------------------------------------------------------
    # GET /api/cart – Obtener carrito (Req. 12.1, 12.6)
    # ------------------------------------------------------------------

    def get_cart(self, user_id: str) -> dict:
        """
        Retorna el carrito del usuario con subtotales y total calculados.

        Args:
            user_id: UID del consumidor autenticado.

        Returns:
            Diccionario con la estructura del carrito (user_id, items, total, updated_at).
        """
        try:
            cart_doc = self._cart_repo.get_or_create_cart(user_id)
            items = self._cart_repo.get_items(user_id)
        except CartRepositoryError as exc:
            raise CartServiceError(exc.message, exc.code) from exc

        return _build_cart_response(user_id, cart_doc, items)

    # ------------------------------------------------------------------
    # POST /api/cart/items – Agregar ítem (Req. 12.1, 8.4)
    # ------------------------------------------------------------------

    def add_item(self, user_id: str, product_id: str, quantity: int) -> dict:
        """
        Agrega un producto al carrito del usuario.

        Reglas de negocio:
          - El producto debe existir (404 si no).
          - El producto debe estar activo (400 si está inactivo, Req. 8.4).
          - quantity debe ser > 0 (validado por Pydantic en la ruta).
          - Si el producto ya está en el carrito, incrementa la cantidad.
          - Desnormaliza productName y price del producto al momento de agregar.

        Args:
            user_id: UID del consumidor.
            product_id: ID del producto a agregar.
            quantity: Cantidad a agregar (> 0).

        Returns:
            Diccionario con el carrito actualizado.

        Raises:
            CartProductNotFoundError: Si el producto no existe.
            CartProductInactiveError: Si el producto está inactivo.
        """
        # Verificar que el producto existe y está activo
        try:
            product = self._product_repo.get_by_id(product_id)
        except ProductRepositoryError as exc:
            raise CartServiceError(exc.message, exc.code) from exc

        if product is None:
            raise CartProductNotFoundError(product_id)

        if product.get("status") != "active":
            raise CartProductInactiveError(product_id)

        product_name = product.get("name", "")
        price = product.get("price", 0.0)

        # Verificar si el producto ya está en el carrito
        try:
            existing_item = self._cart_repo.get_item_by_product_id(user_id, product_id)
        except CartRepositoryError as exc:
            raise CartServiceError(exc.message, exc.code) from exc

        try:
            if existing_item:
                # Incrementar cantidad
                new_quantity = existing_item["quantity"] + quantity
                self._cart_repo.update_item(
                    user_id, existing_item["id"], {"quantity": new_quantity}
                )
            else:
                # Agregar nuevo ítem
                self._cart_repo.get_or_create_cart(user_id)
                self._cart_repo.add_item(
                    user_id,
                    {
                        "productId": product_id,
                        "productName": product_name,
                        "price": price,
                        "quantity": quantity,
                    },
                )
        except CartRepositoryError as exc:
            raise CartServiceError(exc.message, exc.code) from exc

        return self.get_cart(user_id)

    # ------------------------------------------------------------------
    # PUT /api/cart/items/:itemId – Actualizar cantidad (Req. 12.2)
    # ------------------------------------------------------------------

    def update_item(self, user_id: str, item_id: str, quantity: int) -> dict:
        """
        Actualiza la cantidad de un ítem del carrito.

        Reglas de negocio:
          - El ítem debe existir en el carrito (404 si no).
          - quantity debe ser > 0 (validado por Pydantic en la ruta).
          - Recalcula subtotal y total del carrito.

        Args:
            user_id: UID del consumidor.
            item_id: ID del ítem en el carrito.
            quantity: Nueva cantidad (> 0).

        Returns:
            Diccionario con el carrito actualizado.

        Raises:
            CartItemNotFoundServiceError: Si el ítem no existe.
        """
        try:
            self._cart_repo.update_item(user_id, item_id, {"quantity": quantity})
        except CartItemNotFoundError as exc:
            raise CartItemNotFoundServiceError(item_id) from exc
        except CartRepositoryError as exc:
            raise CartServiceError(exc.message, exc.code) from exc

        return self.get_cart(user_id)

    # ------------------------------------------------------------------
    # DELETE /api/cart/items/:itemId – Eliminar ítem (Req. 12.3)
    # ------------------------------------------------------------------

    def delete_item(self, user_id: str, item_id: str) -> dict:
        """
        Elimina un ítem del carrito y recalcula el total.

        Reglas de negocio:
          - El ítem debe existir en el carrito (404 si no).
          - Recalcula el total del carrito tras la eliminación.

        Args:
            user_id: UID del consumidor.
            item_id: ID del ítem a eliminar.

        Returns:
            Diccionario con el carrito actualizado.

        Raises:
            CartItemNotFoundServiceError: Si el ítem no existe.
        """
        try:
            self._cart_repo.delete_item(user_id, item_id)
        except CartItemNotFoundError as exc:
            raise CartItemNotFoundServiceError(item_id) from exc
        except CartRepositoryError as exc:
            raise CartServiceError(exc.message, exc.code) from exc

        return self.get_cart(user_id)
