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

@router.get("/{email}", response_model=UserResponse)
def read_user(email: str, db: Session = Depends(get_db)):
    try:
        return user_service.get_user_by_email(db, email)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
