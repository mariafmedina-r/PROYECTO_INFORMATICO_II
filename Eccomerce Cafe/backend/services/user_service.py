from sqlalchemy.orm import Session
try:
    from repository import user_repository
    from schemas.user import UserCreate
except ImportError:
    from backend.repository import user_repository
    from backend.schemas.user import UserCreate

def create_user(db: Session, user: UserCreate):
    existing_user = user_repository.get_user_by_email(db, user.email)
    if existing_user:
        raise ValueError("Email already registered")
    return user_repository.create_user(db=db, user=user)

def get_user_by_email(db: Session, email: str):
    user = user_repository.get_user_by_email(db, email)
    if not user:
        raise ValueError("User not found")
    return user
