# app/roles/schemas.py
from pydantic import BaseModel
from typing import Optional

class RoleBase(BaseModel):
    name: str
    description: Optional[str] = None

class RoleCreate(RoleBase):
    pass

class RoleUpdate(RoleBase):
    pass

class RoleOut(RoleBase):
    id: int

    class Config:
        from_attributes = True

