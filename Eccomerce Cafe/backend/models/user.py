from sqlalchemy import Column, Integer, String, Boolean
try:
    from database import Base
except ImportError:
    from backend.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    role = Column(String, default="COMPRADOR")
    
    # Producer specific fields
    full_name = Column(String, nullable=True)
    farm_name = Column(String, nullable=True)
    region = Column(String, nullable=True)
    whatsapp = Column(String, nullable=True)
    description = Column(String, nullable=True)
