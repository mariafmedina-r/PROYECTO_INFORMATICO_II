from sqlalchemy.orm import Session
try:
    from models.cart import CartItem
    from models.product import ProductVariant
except ImportError:
    from backend.models.cart import CartItem
    from backend.models.product import ProductVariant

def add_to_cart(db: Session, user_id: int, variant_id: int, quantity: int):
    variant = db.query(ProductVariant).filter(ProductVariant.id == variant_id).first()
    if not variant:
        raise ValueError("Product variant not found")
    
    if variant.stock < quantity:
        raise ValueError(f"Not enough stock. Available: {variant.stock}")

    item = db.query(CartItem).filter(CartItem.user_id == user_id, CartItem.variant_id == variant_id).first()
    if item:
        new_quantity = item.quantity + quantity
        if new_quantity > variant.stock:
            raise ValueError(f"Cannot add more item. Max stock reached: {variant.stock}")
        item.quantity = new_quantity
    else:
        item = CartItem(user_id=user_id, variant_id=variant_id, quantity=quantity)
        db.add(item)

    db.commit()
    db.refresh(item)
    return item

def get_cart_summary(db: Session, user_id: int):
    items = db.query(CartItem).filter(CartItem.user_id == user_id).all()
    subtotal = 0.0
    total_iva = 0.0
    
    for item in items:
        # Load variant explicitely to calculate
        variant = item.variant
        line_price = variant.price * item.quantity
        line_iva = line_price * (variant.iva_percentage / 100.0)
        
        subtotal += line_price
        total_iva += line_iva
        
    return {
        "items": items,
        "subtotal": subtotal,
        "total_iva": total_iva,
        "total": subtotal + total_iva
    }

def clear_cart(db: Session, user_id: int):
    db.query(CartItem).filter(CartItem.user_id == user_id).delete()
    db.commit()
