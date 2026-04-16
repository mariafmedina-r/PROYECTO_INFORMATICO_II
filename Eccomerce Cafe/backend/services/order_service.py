from sqlalchemy.orm import Session
try:
    from models.cart import CartItem
    from models.order import Order, OrderItem
    from models.product import ProductVariant
except ImportError:
    from backend.models.cart import CartItem
    from backend.models.order import Order, OrderItem
    from backend.models.product import ProductVariant

def checkout(db: Session, user_id: int):
    items = db.query(CartItem).filter(CartItem.user_id == user_id).all()
    
    if not items:
        raise ValueError("Cart is empty")

    subtotal = 0.0
    total_iva = 0.0
    
    # 1. Lock stock and Validate
    for item in items:
        variant = db.query(ProductVariant).filter(ProductVariant.id == item.variant_id).first()
        
        if not variant or variant.stock < item.quantity:
            raise ValueError(f"Variant {item.variant_id} is out of stock or insufficient. Transaction Cancelled.")
            
        line_price = variant.price * item.quantity
        line_iva = line_price * (variant.iva_percentage / 100.0)
        
        subtotal += line_price
        total_iva += line_iva

        # Deduct stock (Reservation)
        variant.stock -= item.quantity

    total = subtotal + total_iva

    # 2. Create Order in PENDING
    new_order = Order(
        user_id=user_id,
        status="PENDING",
        total_amount=total
    )
    db.add(new_order)
    db.flush() # get new_order.id before commit to insert items

    # 3. Create OrderItems
    for item in items:
        variant = db.query(ProductVariant).filter(ProductVariant.id == item.variant_id).first()
        order_item = OrderItem(
            order_id=new_order.id,
            variant_id=item.variant_id,
            quantity=item.quantity,
            price_at_purchase=variant.price,
            iva_at_purchase=variant.iva_percentage
        )
        db.add(order_item)

    # 4. Clear Cart
    db.query(CartItem).filter(CartItem.user_id == user_id).delete()

    db.commit()
    db.refresh(new_order)
    return new_order
