from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
try:
    from database import get_db
    from schemas.order import OrderResponse
    from services import order_service
except ImportError:
    from backend.database import get_db
    from backend.schemas.order import OrderResponse
    from backend.services import order_service

router = APIRouter(prefix="/orders", tags=["orders"])
TEST_USER_ID = 1

@router.post("/checkout", response_model=OrderResponse)
def checkout_cart(user_id: int = TEST_USER_ID, db: Session = Depends(get_db)):
    try:
        new_order = order_service.checkout(db, user_id)
        return new_order
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Checkout error: {str(e)}")
