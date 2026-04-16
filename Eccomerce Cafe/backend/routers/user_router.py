from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
try:
    from database import get_db
    from schemas.user import UserCreate, UserResponse
    from services import user_service
except ImportError:
    from backend.database import get_db
    from backend.schemas.user import UserCreate, UserResponse
    from backend.services import user_service

router = APIRouter(
    prefix="/users",
    tags=["users"],
)

@router.post("/", response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    try:
        return user_service.create_user(db=db, user=user)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # Fallback for unexpected errors 
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@router.get("/{email}", response_model=UserResponse)
def read_user(email: str, db: Session = Depends(get_db)):
    try:
        return user_service.get_user_by_email(db, email)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
