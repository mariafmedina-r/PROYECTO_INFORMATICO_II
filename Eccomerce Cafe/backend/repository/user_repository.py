from sqlalchemy.orm import Session
try:
    from models.user import User
    from schemas.user import UserCreate
except ImportError:
    from backend.models.user import User
    from backend.schemas.user import UserCreate

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def create_user(db: Session, user: UserCreate):
    # Fake hashing for now, as we're preparing a temporary SQLite setup
    # You will later replace this with Firebase Auth or actual password hashing (e.g. Passlib/Bcrypt)
    fake_hashed_password = user.password + "_hashed"
    db_user = User(email=user.email, hashed_password=fake_hashed_password, role=user.role)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def init_test_user(db: Session):
    test_user = get_user_by_email(db, "test@example.com")
    if not test_user:
        create_user(db, UserCreate(email="test@example.com", password="testpassword123", role="Admin"))
