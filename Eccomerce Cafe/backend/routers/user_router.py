from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
try:
    from database import get_db
    from schemas.user import UserCreate, UserResponse, UserUpdate
    from services import user_service
    from repository import user_repository
except ImportError:
    from backend.database import get_db
    from backend.schemas.user import UserCreate, UserResponse, UserUpdate
    from backend.services import user_service
    from backend.repository import user_repository

router = APIRouter(
    prefix="/users",
    tags=["users"],
)

@router.post("/", response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    print(f"DEBUG: Attempting to create user: {user.email}")
    try:
        new_user = user_service.create_user(db=db, user=user)
        print(f"DEBUG: User {new_user.email} created in DB.")
        return new_user
    except ValueError as e:
        print(f"DEBUG: Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(f"DEBUG: Fatal error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/pending-producers", response_model=List[UserResponse])
def get_pending_producers(db: Session = Depends(get_db)):
    return user_repository.get_pending_producers(db)

@router.get("/all", response_model=List[UserResponse])
def get_all_users(db: Session = Depends(get_db)):
    return user_repository.get_all_users(db)

@router.patch("/{user_id}/approve", response_model=UserResponse)
def approve_producer(user_id: int, db: Session = Depends(get_db)):
    user = user_repository.update_user_status(db, user_id, True)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# =====================================================================
# FIREBASE & FIRESTORE IDENTITY MIDDLEWARE
# =====================================================================
# Estos endpoints delegan el poder de Firestore/Auth al backend. 
# Esto evita tener que escribir Reglas de Seguridad complejas 
# en Firebase que usualmente causan errores de "Insufficient Permissions" en produccion.

@router.get("/admin/firebase-users")
def get_firebase_users():
    """Retorna TODOS los usuarios del eCommerce (Merge entre Firebase Auth + Firestore)."""
    try:
        return user_service.get_all_firebase_users()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/profile")
def save_profile(uid: str, data: dict):
    """Guarda/actualiza el perfil base tras el registro inicial en el Frontend."""
    try:
        return user_service.save_user_profile(uid, data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/profile/{uid}")
def get_firebase_profile(uid: str):
    """Obtiene un perfil de Firebase sorteando reglas de Firestore usando Backend SDK."""
    try:
        return user_service.get_user_profile_fs(uid)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/upgrade-to-producer")
def upgrade_to_producer(uid: str, data: dict):
    """Cambia el rol de un COMPRADOR a PRODUCTOR y activa la cuenta para acceso inmediato."""
    try:
        return user_service.upgrade_user_to_producer(uid, data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/admin/products-fs")
def create_product_bypassing_rules(data: dict):
    try:
        return user_service.create_product_fs(data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/admin/products-fs")
def get_all_products_fs():
    try:
        return user_service.get_all_products_fs()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/admin/products-fs/{product_id}")
def delete_product_bypassing_rules(product_id: str):
    try:
        return user_service.delete_product_fs(product_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.patch("/admin/products-fs/{product_id}")
def update_product_bypassing_rules(product_id: str, data: dict):
    try:
        return user_service.update_product_fs(product_id, data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{email}", response_model=UserResponse)
def read_user(email: str, db: Session = Depends(get_db)):
    try:
        return user_service.get_user_by_email(db, email)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
