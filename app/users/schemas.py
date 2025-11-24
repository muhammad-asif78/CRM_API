# app/users/schemas.py
from pydantic import BaseModel
from typing import Optional
from app.roles.schemas import RoleOut

class UserBase(BaseModel):
    email: str
    name: Optional[str] = None

class UserCreate(UserBase):
    password: str
    role_id: int  # Required - must assign a role

class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None
    role_id: Optional[int] = None

class UserOut(UserBase):
    id: int
    role_id: int
    role: Optional[RoleOut] = None

    class Config:
        from_attributes = True
