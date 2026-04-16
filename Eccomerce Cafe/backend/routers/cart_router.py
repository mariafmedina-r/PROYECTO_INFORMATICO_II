from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
try:
    from database import get_db
    from schemas.cart import CartItemCreate, CartSummary
    from services import cart_service
except ImportError:
    from backend.database import get_db
    from backend.schemas.cart import CartItemCreate, CartSummary
    from backend.services import cart_service

router = APIRouter(prefix="/cart", tags=["cart"])
TEST_USER_ID = 1 # Assuming user ID 1 is the test user we created

@router.post("/items")
def add_item_to_cart(item: CartItemCreate, user_id: int = TEST_USER_ID, db: Session = Depends(get_db)):
    try:
        cart_service.add_to_cart(db, user_id, item.variant_id, item.quantity)
        return {"message": "Item added successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {e}")

@router.get("/", response_model=CartSummary)
def get_cart(user_id: int = TEST_USER_ID, db: Session = Depends(get_db)):
    try:
        return cart_service.get_cart_summary(db, user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {e}")

@router.delete("/")
def clear_cart(user_id: int = TEST_USER_ID, db: Session = Depends(get_db)):
    cart_service.clear_cart(db, user_id)
    return {"message": "Cart cleared"}
