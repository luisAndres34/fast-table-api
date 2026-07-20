from pydantic import BaseModel, EmailStr
from datetime import datetime
import uuid

from app.models.enums import UserRole

class UserBase(BaseModel):
    name: str
    email: EmailStr
    role: UserRole = UserRole.client
    is_active: bool = True

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    name: str | None = None
    email: EmailStr | None = None
    password: str | None = None
    is_active: bool | None = None

class UserPublic(UserBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
