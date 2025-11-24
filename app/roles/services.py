# app/roles/services.py
from sqlalchemy.orm import Session
from fastapi import HTTPException
from typing import List
from app.roles.models import Role
from app.roles.schemas import RoleCreate, RoleUpdate

class RoleService:
    def __init__(self, db: Session):
        self.db = db

    def get_all_roles(self) -> List[Role]:
        return self.db.query(Role).all()

    def get_role(self, role_id: int) -> Role:
        role = self.db.query(Role).filter(Role.id == role_id).first()
        if not role:
            raise HTTPException(status_code=404, detail="Role not found")
        return role

    def get_role_by_name(self, name: str) -> Role:
        return self.db.query(Role).filter(Role.name == name).first()

    def create_role(self, role_in: RoleCreate) -> Role:
        existing = self.db.query(Role).filter(Role.name == role_in.name).first()
        if existing:
            raise HTTPException(status_code=400, detail="Role already exists")
        
        role = Role(
            name=role_in.name,
            description=role_in.description
        )
        self.db.add(role)
        self.db.commit()
        self.db.refresh(role)
        return role

    def update_role(self, role_id: int, role_in: RoleUpdate) -> Role:
        role = self.get_role(role_id)
        
        # Check if name is being changed and if new name already exists
        if role_in.name != role.name:
            existing = self.db.query(Role).filter(Role.name == role_in.name).first()
            if existing:
                raise HTTPException(status_code=400, detail="Role name already exists")
        
        role.name = role_in.name
        role.description = role_in.description
        self.db.commit()
        self.db.refresh(role)
        return role

    def delete_role(self, role_id: int):
        role = self.get_role(role_id)
        self.db.delete(role)
        self.db.commit()

