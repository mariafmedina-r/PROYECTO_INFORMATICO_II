from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
try:
    from database import get_db
    from schemas.product import ProductResponse
    from models.product import Product
    from models.product import ProductVariant # Needed for relation loading
except ImportError:
    from backend.database import get_db
    from backend.schemas.product import ProductResponse
    from backend.models.product import Product
    from backend.models.product import ProductVariant

router = APIRouter(prefix="/products", tags=["products"])

@router.get("/", response_model=List[ProductResponse])
def get_all_products(db: Session = Depends(get_db)):
    products = db.query(Product).filter(Product.deleted_at == None).all()
    return products
