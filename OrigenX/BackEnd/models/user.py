"""
models/user.py – Modelos Pydantic para usuarios y autenticación.
"""

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class UserRole(str, Enum):
    """Roles disponibles en el sistema (Req. 3.1)."""
    CONSUMER = "CONSUMER"
    PRODUCER = "PRODUCER"
    ADMIN = "ADMIN"


class UserBase(BaseModel):
    """Campos base de un usuario."""
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr


class UserCreate(UserBase):
    """Esquema de request para registro de usuario (Req. 1.1)."""
    password: str = Field(..., min_length=8, description="Mínimo 8 caracteres")
    role: UserRole = UserRole.CONSUMER


class UserResponse(UserBase):
    """Esquema de response para datos de usuario."""
    id: str
    role: UserRole
    created_at: datetime

    model_config = {"from_attributes": True}


class LoginRequest(BaseModel):
    """Esquema de request para login (Req. 2.1)."""
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    """Esquema de response para login exitoso."""
    token: str
    user: UserResponse


class ForgotPasswordRequest(BaseModel):
    """Esquema de request para recuperación de contraseña (Req. 2.4)."""
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    """Esquema de request para restablecimiento de contraseña."""
    token: str
    new_password: str = Field(..., min_length=8)
