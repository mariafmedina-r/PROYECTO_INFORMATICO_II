"""
services/order_service.py – Lógica de negocio de pedidos.

Responsabilidades:
  - Creación de pedidos con snapshot de productos (Req. 13.1, 13.4)
  - Validación: carrito no vacío, dirección válida, empresa de envío seleccionada
  - Vaciado automático del carrito al crear pedido (Req. 13.2)
  - Máquina de estados del pedido (Req. 19.1, 19.4)
  - Verificación de autorización para cambios de estado (Req. 19.3)
  - Notificación al consumidor en cada cambio de estado (Req. 19.2)
  - Panel de ventas del productor (Req. 16.1–16.4)

Requerimientos: 13.1, 13.2, 13.3, 13.4, 13.5, 15.1, 15.2, 16.1, 16.2, 16.3, 16.4,
                19.1, 19.2, 19.3, 19.4
"""

import logging
from datetime import date, datetime, timezone
from datetime import datetime as _datetime_cls  # alias para isinstance, no parcheable
from typing import Optional

from repositories.address_repository import AddressRepository, AddressRepositoryError
from repositories.cart_repository import CartRepository, CartRepositoryError
from repositories.order_repository import OrderRepository, OrderRepositoryError
from repositories.product_repository import ProductRepository, ProductRepositoryError
from repositories.user_repository import UserRepository
from services.notification_service import NotificationService, NotificationServiceError
from services.shipping_service import ShippingService, ShippingServiceUnavailableError

logger = logging.getLogger(__name__)

# Transiciones de estado válidas del pedido (Req. 19.1, 19.4)
VALID_TRANSITIONS: dict[str, list[str]] = {
    "pendiente": ["pagado", "cancelado"],
    "pagado": ["en_preparacion", "cancelado"],
    "en_preparacion": ["enviado"],
    "enviado": ["entregado"],
    "entregado": [],
    "cancelado": [],
}


class OrderServiceError(Exception):
    """Error base del servicio de pedidos."""

    def __init__(self, message: str, code: str = "ORDER_SERVICE_ERROR"):
        self.message = message
        self.code = code
        super().__init__(message)


class OrderCartEmptyError(OrderServiceError):
    """El carrito está vacío (Req. 13.3)."""

    def __init__(self):
        super().__init__(
            message="El carrito no contiene productos. Agrega productos antes de confirmar el pedido.",
            code="CART_EMPTY",
        )


class OrderAddressNotFoundError(OrderServiceError):
    """La dirección de envío no existe o no pertenece al usuario."""

    def __init__(self, address_id: str):
        super().__init__(
            message=f"Dirección con id '{address_id}' no encontrada o no pertenece al usuario.",
            code="ADDRESS_NOT_FOUND",
        )


class OrderShippingOptionNotFoundError(OrderServiceError):
    """La empresa de envío seleccionada no existe."""

    def __init__(self, shipping_company: str):
        super().__init__(
            message=f"Empresa de envío '{shipping_company}' no disponible.",
            code="SHIPPING_OPTION_NOT_FOUND",
        )


class OrderNotFoundError(OrderServiceError):
    """El pedido no existe."""

    def __init__(self, order_id: str):
        super().__init__(
            message=f"Pedido con id '{order_id}' no encontrado.",
            code="ORDER_NOT_FOUND",
        )


class OrderInvalidTransitionError(OrderServiceError):
    """Transición de estado inválida (Req. 19.4)."""

    def __init__(self, current_status: str, new_status: str):
        valid = VALID_TRANSITIONS.get(current_status, [])
        super().__init__(
            message=(
                f"Transición de estado inválida: '{current_status}' → '{new_status}'. "
                f"Transiciones válidas desde '{current_status}': {valid or 'ninguna'}."
            ),
            code="INVALID_STATUS_TRANSITION",
        )


class OrderForbiddenError(OrderServiceError):
    """El productor no tiene productos en el pedido (Req. 19.3)."""

    def __init__(self):
        super().__init__(
            message="No tienes permiso para actualizar el estado de este pedido.",
            code="ORDER_FORBIDDEN",
        )


class OrderService:
    """Servicio de gestión de pedidos."""

    def __init__(
        self,
        order_repository: Optional[OrderRepository] = None,
        cart_repository: Optional[CartRepository] = None,
        address_repository: Optional[AddressRepository] = None,
        product_repository: Optional[ProductRepository] = None,
        shipping_service: Optional[ShippingService] = None,
        notification_service: Optional[NotificationService] = None,
    ):
        self._order_repo = order_repository or OrderRepository()
        self._cart_repo = cart_repository or CartRepository()
        self._address_repo = address_repository or AddressRepository()
        self._product_repo = product_repository or ProductRepository()
        self._user_repo = UserRepository()
        self._shipping_svc = shipping_service or ShippingService()
        self._notification_svc = notification_service or NotificationService()

    # ------------------------------------------------------------------
    # POST /api/orders – Crear pedido (Req. 13.1 – 13.5)
    # ------------------------------------------------------------------

    def create_order(
        self,
        consumer_id: str,
        address_id: str,
        shipping_company_id: str,
    ) -> dict:
        """
        Crea un pedido a partir del carrito del consumidor.

        Reglas de negocio:
          - El carrito no puede estar vacío (Req. 13.3).
          - La dirección debe existir y pertenecer al consumidor.
          - La empresa de envío debe estar disponible.
          - Registra snapshot de productos (nombre, precio, cantidad) (Req. 13.4).
          - Crea el pedido con estado 'pendiente' y registra createdAt (Req. 13.1).
          - Vacía el carrito automáticamente tras crear el pedido (Req. 13.2).

        Args:
            consumer_id: UID del consumidor autenticado.
            address_id: ID de la dirección de envío seleccionada.
            shipping_company_id: ID de la empresa de envío seleccionada.

        Returns:
            Diccionario con los datos del pedido creado (incluye items).

        Raises:
            OrderCartEmptyError: Si el carrito está vacío.
            OrderAddressNotFoundError: Si la dirección no existe o no pertenece al usuario.
            OrderShippingOptionNotFoundError: Si la empresa de envío no existe.
            OrderServiceError: Para otros errores internos.
        """
        # 1. Obtener ítems del carrito
        try:
            cart_items = self._cart_repo.get_items(consumer_id)
        except CartRepositoryError as exc:
            raise OrderServiceError(exc.message, exc.code) from exc

        if not cart_items:
            raise OrderCartEmptyError()

        # 2. Validar dirección de envío
        try:
            address = self._address_repo.get_by_id(address_id, user_id=consumer_id)
        except AddressRepositoryError as exc:
            raise OrderServiceError(exc.message, exc.code) from exc

        if address is None:
            raise OrderAddressNotFoundError(address_id)

        # 3. Validar empresa de envío y obtener costo
        try:
            shipping_option = self._shipping_svc.get_option_by_id(shipping_company_id)
        except ShippingServiceUnavailableError as exc:
            raise OrderServiceError(exc.message, exc.code) from exc

        if shipping_option is None:
            raise OrderShippingOptionNotFoundError(shipping_company_id)

        shipping_cost = shipping_option["cost"]
        shipping_name = shipping_option["name"]

        # 4. Construir snapshot de productos (Req. 13.4)
        items_snapshot = []
        subtotal = 0.0
        for item in cart_items:
            price = float(item.get("price", 0.0))
            quantity = int(item.get("quantity", 0))
            subtotal += round(price * quantity, 2)
            items_snapshot.append({
                "productId": item.get("productId"),
                "productNameSnapshot": item.get("productName"),
                "priceSnapshot": price,
                "quantity": quantity,
            })

        total = round(subtotal + shipping_cost, 2)

        # 5. Construir snapshot de dirección
        address_snapshot = {
            "street": address.get("street"),
            "city": address.get("city"),
            "department": address.get("department"),
            "postalCode": address.get("postalCode"),
        }

        # 6. Crear documento del pedido en Firestore
        now = datetime.now(timezone.utc)
        order_data = {
            "consumerId": consumer_id,
            "addressSnapshot": address_snapshot,
            "shippingCompany": shipping_name,
            "shippingCost": shipping_cost,
            "total": total,
            "status": "pendiente",
            "transactionId": None,
            "createdAt": now,
            "updatedAt": now,
        }

        try:
            order = self._order_repo.create_order(order_data)
            order_id = order["id"]
        except OrderRepositoryError as exc:
            raise OrderServiceError(exc.message, exc.code) from exc

        # 7. Crear ítems del pedido en la subcolección
        try:
            self._order_repo.create_order_items(order_id, items_snapshot)
        except OrderRepositoryError as exc:
            raise OrderServiceError(exc.message, exc.code) from exc

        # 8. Vaciar el carrito automáticamente (Req. 13.2)
        try:
            self._cart_repo.clear_items(consumer_id)
        except CartRepositoryError as exc:
            # No fallar el pedido si el vaciado del carrito falla; solo registrar el error
            logger.error(
                "Error al vaciar carrito del consumidor '%s' tras crear pedido '%s': %s",
                consumer_id, order_id, exc,
            )

        # 9. Decrementar stock de cada producto (Req. 13.5)
        for item in items_snapshot:
            product_id = item.get("productId")
            qty = int(item.get("quantity", 0))
            if not product_id or qty <= 0:
                continue
            try:
                product = self._product_repo.get_by_id(product_id)
                if product:
                    current_stock = int(product.get("stock", 0))
                    new_stock = max(0, current_stock - qty)
                    self._product_repo.update(product_id, {"stock": new_stock})
            except Exception as exc:
                # No fallar el pedido si la actualización de stock falla; solo registrar
                logger.error(
                    "Error al decrementar stock del producto '%s' tras crear pedido '%s': %s",
                    product_id, order_id, exc,
                )

        # 10. Retornar pedido con ítems
        order["items"] = items_snapshot
        return order

    # ------------------------------------------------------------------
    # PATCH /api/orders/:id/status – Actualizar estado (Req. 19.1, 19.3, 19.4)
    # ------------------------------------------------------------------

    def update_order_status(
        self,
        order_id: str,
        new_status: str,
        requester_id: str,
        requester_role: str,
    ) -> dict:
        """
        Actualiza el estado de un pedido siguiendo la máquina de estados.

        Reglas de negocio:
          - Solo PRODUCER (con productos en el pedido) o ADMIN pueden actualizar (Req. 19.3).
          - Solo se permiten transiciones válidas (Req. 19.4).
          - Registra timestamp de cada cambio de estado (Req. 19.1).
          - Notifica al consumidor del cambio de estado (Req. 19.2).

        Args:
            order_id: ID del pedido a actualizar.
            new_status: Nuevo estado deseado.
            requester_id: UID del usuario que realiza la solicitud.
            requester_role: Rol del usuario ('PRODUCER' o 'ADMIN').

        Returns:
            Diccionario con los datos del pedido actualizado.

        Raises:
            OrderNotFoundError: Si el pedido no existe.
            OrderForbiddenError: Si el productor no tiene productos en el pedido.
            OrderInvalidTransitionError: Si la transición de estado no es válida.
            OrderServiceError: Para otros errores internos.
        """
        # 1. Obtener el pedido
        try:
            order = self._order_repo.get_by_id(order_id)
        except OrderRepositoryError as exc:
            raise OrderServiceError(exc.message, exc.code) from exc

        if order is None:
            raise OrderNotFoundError(order_id)

        current_status = order.get("status")

        # 2. Verificar autorización del productor (Req. 19.3)
        if requester_role == "PRODUCER":
            items = order.get("items", [])
            # Verificar que al menos un ítem del pedido pertenece al productor
            producer_has_products = self._producer_has_products_in_order(
                requester_id, items
            )
            if not producer_has_products:
                raise OrderForbiddenError()

        # 3. Validar transición de estado (Req. 19.4)
        valid_next_states = VALID_TRANSITIONS.get(current_status, [])
        if new_status not in valid_next_states:
            raise OrderInvalidTransitionError(current_status, new_status)

        # 4. Actualizar estado y registrar timestamp (Req. 19.1)
        now = datetime.now(timezone.utc)
        try:
            updated_order = self._order_repo.update_order(
                order_id,
                {
                    "status": new_status,
                    "updatedAt": now,
                },
            )
        except OrderRepositoryError as exc:
            raise OrderServiceError(exc.message, exc.code) from exc

        # 5. Notificar al consumidor (Req. 19.2)
        consumer_id = order.get("consumerId")
        if consumer_id:
            try:
                self._notification_svc.notify_order_status_change(
                    user_id=consumer_id,
                    order_id=order_id,
                    new_status=new_status,
                )
            except NotificationServiceError as exc:
                # No fallar la actualización si la notificación falla; solo registrar
                logger.error(
                    "Error al notificar cambio de estado del pedido '%s': %s",
                    order_id, exc,
                )

        return updated_order

    def _producer_has_products_in_order(
        self, producer_id: str, items: list[dict]
    ) -> bool:
        """
        Verifica si el productor tiene al menos un producto en los ítems del pedido.

        Consulta Firestore para verificar la propiedad de cada producto referenciado.

        Args:
            producer_id: UID del productor.
            items: Lista de ítems del pedido (con productId).

        Returns:
            True si el productor tiene al menos un producto en el pedido.
        """
        for item in items:
            product_id = item.get("productId")
            if not product_id:
                continue
            try:
                product = self._product_repo.get_by_id(product_id)
                if product and product.get("producerId") == producer_id:
                    return True
            except ProductRepositoryError:
                continue
        return False

    # ------------------------------------------------------------------
    # GET /api/orders – Historial del consumidor (Req. 15.1)
    # ------------------------------------------------------------------

    def get_consumer_orders(self, consumer_id: str) -> list[dict]:
        """
        Retorna todos los pedidos del consumidor con el primer ítem y su imagen.
        """
        try:
            orders = self._order_repo.get_orders_by_consumer(consumer_id)
        except OrderRepositoryError as exc:
            raise OrderServiceError(exc.message, exc.code) from exc

        # Enriquecer cada pedido con el primer ítem + imagen principal
        for order in orders:
            order_id = order.get("id")
            if not order_id:
                continue
            try:
                # Obtener ítems de la subcolección
                items_ref = (
                    self._order_repo._db.collection("orders")
                    .document(order_id)
                    .collection("items")
                    .limit(3)
                )
                item_docs = list(items_ref.stream())
                items_preview = []
                for doc in item_docs:
                    item = doc.to_dict()
                    item["id"] = doc.id
                    # Obtener imagen principal
                    product_id = item.get("productId")
                    main_image_url = None
                    if product_id:
                        try:
                            first_image = self._product_repo.get_first_image(product_id)
                            if first_image:
                                main_image_url = first_image.get("url")
                        except Exception:
                            pass
                    item["mainImageUrl"] = main_image_url
                    items_preview.append(item)
                order["itemsPreview"] = items_preview
            except Exception:
                order["itemsPreview"] = []

        return orders

    # ------------------------------------------------------------------
    # GET /api/orders/:id – Detalle de pedido (Req. 15.2)
    # ------------------------------------------------------------------

    def get_order_detail(self, order_id: str, consumer_id: str) -> dict:
        """
        Retorna el detalle completo de un pedido, verificando que pertenece al consumidor.
        Enriquece los ítems con la imagen principal del producto.
        """
        try:
            order = self._order_repo.get_by_id(order_id)
        except OrderRepositoryError as exc:
            raise OrderServiceError(exc.message, exc.code) from exc

        if order is None or order.get("consumerId") != consumer_id:
            raise OrderNotFoundError(order_id)

        # Enriquecer ítems con imagen principal del producto
        enriched_items = []
        for item in order.get("items", []):
            product_id = item.get("productId")
            main_image_url = None
            if product_id:
                try:
                    first_image = self._product_repo.get_first_image(product_id)
                    if first_image:
                        main_image_url = first_image.get("url")
                except ProductRepositoryError:
                    pass
            enriched_items.append({**item, "mainImageUrl": main_image_url})

        # Calcular fecha estimada de entrega basada en la empresa de envío
        shipping_company_id = None
        estimated_delivery = None
        try:
            options = self._shipping_svc.get_options()
            shipping_name = order.get("shippingCompany", "")
            for opt in options:
                if opt["name"] == shipping_name:
                    shipping_company_id = opt["id"]
                    created_at = order.get("createdAt")
                    if created_at and isinstance(created_at, datetime):
                        from datetime import timedelta
                        estimated_delivery = (
                            created_at + timedelta(days=opt["estimated_days"])
                        ).isoformat()
                    break
        except Exception:
            pass

        order["items"] = enriched_items
        order["estimatedDelivery"] = estimated_delivery
        return order

    # ------------------------------------------------------------------
    # GET /api/sales – Panel de ventas del productor (Req. 16.1–16.4)
    # ------------------------------------------------------------------

    def get_producer_sales(
        self,
        producer_id: str,
        from_date: Optional[date] = None,
        to_date: Optional[date] = None,
    ) -> dict:
        """
        Retorna el panel de ventas del productor autenticado.

        Reglas de negocio:
          - Solo expone pedidos y productos del propio productor (Req. 16.4).
          - Cada pedido incluye fecha, productos vendidos, cantidades, precios y estado (Req. 16.1).
          - Calcula el total acumulado del mes en curso y del mes anterior (Req. 16.2).
          - Soporta filtro por rango de fechas en la lista de pedidos (Req. 16.3).
          - Los totales mensuales se calculan sobre TODOS los pedidos, sin filtro de fechas.

        Args:
            producer_id: UID del productor autenticado.
            from_date: Fecha de inicio del filtro de la lista (inclusive, YYYY-MM-DD).
            to_date: Fecha de fin del filtro de la lista (inclusive, YYYY-MM-DD).

        Returns:
            Diccionario con:
              - orders: lista de pedidos filtrados (solo ítems del productor)
              - current_month_total: total acumulado del mes en curso
              - previous_month_total: total acumulado del mes anterior

        Raises:
            OrderServiceError: Para errores internos.
        """
        now = datetime.now(timezone.utc)
        current_year = now.year
        current_month = now.month

        # Calcular año/mes del mes anterior
        if current_month == 1:
            prev_year = current_year - 1
            prev_month = 12
        else:
            prev_year = current_year
            prev_month = current_month - 1

        # Obtener pedidos filtrados por fecha para la lista (Req. 16.3)
        try:
            filtered_orders = self._order_repo.get_orders_by_producer(
                producer_id, from_date=from_date, to_date=to_date
            )
        except OrderRepositoryError as exc:
            raise OrderServiceError(exc.message, exc.code) from exc

        # Obtener TODOS los pedidos del productor para calcular totales mensuales (Req. 16.2)
        # Solo necesitamos recalcular si hay filtros activos
        if from_date is not None or to_date is not None:
            try:
                all_orders = self._order_repo.get_orders_by_producer(producer_id)
            except OrderRepositoryError as exc:
                raise OrderServiceError(exc.message, exc.code) from exc
        else:
            all_orders = filtered_orders

        # Enriquecer pedidos filtrados con información del cliente (nombre, email)
        consumer_cache: dict[str, dict] = {}
        for order in filtered_orders:
            consumer_id = order.get("consumerId")
            if not consumer_id:
                order["consumerInfo"] = None
                continue
            if consumer_id not in consumer_cache:
                try:
                    user = self._user_repo.get_by_id(consumer_id)
                    consumer_cache[consumer_id] = {
                        "name": user.get("name") if user else None,
                        "email": user.get("email") if user else None,
                    }
                except Exception:
                    consumer_cache[consumer_id] = {"name": None, "email": None}
            order["consumerInfo"] = consumer_cache[consumer_id]

        # Calcular totales mensuales (Req. 16.2)
        current_month_total = 0.0
        previous_month_total = 0.0

        for order in all_orders:
            created_at = order.get("createdAt")
            if created_at is None:
                continue

            # Normalizar a datetime con timezone si es necesario
            if isinstance(created_at, _datetime_cls):
                order_dt = created_at if created_at.tzinfo else created_at.replace(tzinfo=timezone.utc)
            else:
                continue

            order_year = order_dt.year
            order_month = order_dt.month

            # Calcular subtotal de los ítems del productor en este pedido
            items = order.get("items", [])
            subtotal = sum(
                float(item.get("priceSnapshot", 0.0)) * int(item.get("quantity", 0))
                for item in items
            )

            if order_year == current_year and order_month == current_month:
                current_month_total += subtotal
            elif order_year == prev_year and order_month == prev_month:
                previous_month_total += subtotal

        return {
            "orders": filtered_orders,
            "current_month_total": round(current_month_total, 2),
            "previous_month_total": round(previous_month_total, 2),
        }
