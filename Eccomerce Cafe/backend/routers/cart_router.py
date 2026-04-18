from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
try:
    from database import get_db
    from schemas.cart import CartItemCreate, CartSummary
    from services import cart_service
    from middleware.auth_middleware import get_current_user
except ImportError:
    from backend.database import get_db
    from backend.schemas.cart import CartItemCreate, CartSummary
    from backend.services import cart_service
    from backend.middleware.auth_middleware import get_current_user

router = APIRouter(prefix="/cart", tags=["cart"])

@router.post("/items")
def add_item_to_cart(item: CartItemCreate, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    user_id = 1 # We still need a way to map Firebase UID to local DB User ID
    # In a full implementation, we would find or create the user in our DB based on Firebase UID
    # user_id = find_or_create_user(db, current_user['uid'])

    try:
        cart_service.add_to_cart(db, user_id, item.variant_id, item.quantity)
        return {"message": "Item added successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {e}")

@router.get("/", response_model=CartSummary)
def get_cart(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    user_id = 1 # Placeholder for mapping
    try:
        return cart_service.get_cart_summary(db, user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {e}")

@router.delete("/")
def clear_cart(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    user_id = 1 # Placeholder for mapping
    cart_service.clear_cart(db, user_id)
    return {"message": "Cart cleared"}

