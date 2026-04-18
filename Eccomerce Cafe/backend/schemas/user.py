from pydantic import BaseModel, EmailStr
from typing import Optional

class UserBase(BaseModel):
    email: EmailStr
    role: str = "COMPRADOR"
    full_name: Optional[str] = None
    farm_name: Optional[str] = None
    region: Optional[str] = None
    whatsapp: Optional[str] = None
    description: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    is_active: Optional[bool] = None

class UserResponse(UserBase):
    id: int
    is_active: bool

    class Config:
        from_attributes = True
