from sqlalchemy.orm import Session
try:
    from models.user import User
    from schemas.user import UserCreate
except ImportError:
    from backend.models.user import User
    from backend.schemas.user import UserCreate

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def get_user_by_id(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()

def create_user(db: Session, user: UserCreate):
    # If it's a producer, it starts inactive
    is_active = True
    if user.role == "PRODUCTOR":
        is_active = False
        
    fake_hashed_password = user.password + "_hashed"
    db_user = User(
        email=user.email, 
        hashed_password=fake_hashed_password, 
        role=user.role,
        is_active=is_active,
        full_name=user.full_name,
        farm_name=user.farm_name,
        region=user.region,
        whatsapp=user.whatsapp,
        description=user.description
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user_status(db: Session, user_id: int, status: bool):
    user = get_user_by_id(db, user_id)
    if user:
        user.is_active = status
        db.commit()
        db.refresh(user)
    return user

def get_pending_producers(db: Session):
    return db.query(User).filter(User.role == "PRODUCTOR", User.is_active == False).all()

def get_all_users(db: Session):
    return db.query(User).all()

def init_test_user(db: Session):
    test_user = get_user_by_email(db, "test@example.com")
    if not test_user:
        create_user(db, UserCreate(email="test@example.com", password="testpassword123", role="ADMIN"))
