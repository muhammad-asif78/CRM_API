# app/users/services.py
from sqlalchemy.orm import Session
from fastapi import HTTPException
from typing import List, Optional
from app.users.models import User
from app.roles.models import Role
from app.users.schemas import UserCreate, UserUpdate
from app.core.security import hash_password

class UserService:
    def __init__(self, db: Session):
        self.db = db

    def get_all_users(self) -> List[User]:
        return self.db.query(User).all()

    def get_user(self, user_id: int) -> User:
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user

    def get_user_by_email(self, email: str) -> Optional[User]:
        return self.db.query(User).filter(User.email == email).first()

    def create_user(self, user_in: UserCreate, created_by: User) -> User:
        existing = self.db.query(User).filter(User.email == user_in.email).first()
        if existing:
            raise HTTPException(status_code=400, detail="Email already exists")
        
        # Validate role_id
        role = self.db.query(Role).filter(Role.id == user_in.role_id).first()
        if not role:
            raise HTTPException(status_code=400, detail=f"Role with id {user_in.role_id} not found")
        
        # Check permissions based on role being assigned
        if role.name == "SuperAdmin":
            raise HTTPException(
                status_code=403,
                detail="Cannot create SuperAdmin user. Use /super-admin/init endpoint."
            )
        elif role.name == "Admin":
            if created_by.role.name != "SuperAdmin":
                raise HTTPException(
                    status_code=403,
                    detail="Only SuperAdmin can create Admin users"
                )
        elif role.name in ["Manager", "Accounts", "Customer"]:
            if created_by.role.name not in ["SuperAdmin", "Admin"]:
                raise HTTPException(
                    status_code=403,
                    detail="Only Admin or SuperAdmin can create Manager, Accounts, or Customer users"
                )
        
        user = User(
            email=user_in.email,
            name=user_in.name or user_in.email.split("@")[0],
            hashed_password=hash_password(user_in.password),
            role_id=user_in.role_id
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def update_user(self, user_id: int, user_in: UserUpdate, updated_by: User) -> User:
        user = self.get_user(user_id)
        
        # Check if trying to update SuperAdmin or Admin
        if user.role.name == "SuperAdmin":
            if updated_by.role.name != "SuperAdmin":
                raise HTTPException(
                    status_code=403,
                    detail="Cannot modify SuperAdmin user"
                )
        elif user.role.name == "Admin":
            if updated_by.role.name != "SuperAdmin":
                raise HTTPException(
                    status_code=403,
                    detail="Only SuperAdmin can modify Admin users"
                )
        
        if user_in.name is not None:
            user.name = user_in.name
        if user_in.email is not None:
            existing = self.db.query(User).filter(User.email == user_in.email, User.id != user_id).first()
            if existing:
                raise HTTPException(status_code=400, detail="Email already exists")
            user.email = user_in.email
        if user_in.password:
            user.hashed_password = hash_password(user_in.password)
        if user_in.role_id is not None:
            # Validate role assignment permissions
            if user_in.role_id:
                role = self.db.query(Role).filter(Role.id == user_in.role_id).first()
                if not role:
                    raise HTTPException(status_code=400, detail=f"Role with id {user_in.role_id} not found")
                
                # Check permissions
                if role.name == "SuperAdmin":
                    raise HTTPException(
                        status_code=403,
                        detail="Cannot assign SuperAdmin role"
                    )
                elif role.name == "Admin":
                    if updated_by.role.name != "SuperAdmin":
                        raise HTTPException(
                            status_code=403,
                            detail="Only SuperAdmin can assign Admin role"
                        )
                elif role.name in ["Manager", "Accounts", "Customer"]:
                    if updated_by.role.name not in ["SuperAdmin", "Admin"]:
                        raise HTTPException(
                            status_code=403,
                            detail="Only Admin or SuperAdmin can assign Manager, Accounts, or Customer roles"
                        )
            user.role_id = user_in.role_id
        
        self.db.commit()
        self.db.refresh(user)
        return user

    def delete_user(self, user_id: int, deleted_by: User):
        user = self.get_user(user_id)
        
        # Check permissions
        if user.role.name == "SuperAdmin":
            raise HTTPException(
                status_code=403,
                detail="Cannot delete SuperAdmin user"
            )
        elif user.role.name == "Admin":
            if deleted_by.role.name != "SuperAdmin":
                raise HTTPException(
                    status_code=403,
                    detail="Only SuperAdmin can delete Admin users"
                )
        
        self.db.delete(user)
        self.db.commit()

    def assign_role(self, user_id: int, role_id: int, assigned_by: User):
        user = self.get_user(user_id)
        role = self.db.query(Role).filter(Role.id == role_id).first()
        if not role:
            raise HTTPException(status_code=404, detail="Role not found")
        
        # Check permissions
        if role.name == "SuperAdmin":
            raise HTTPException(
                status_code=403,
                detail="Cannot assign SuperAdmin role"
            )
        elif role.name == "Admin":
            if assigned_by.role.name != "SuperAdmin":
                raise HTTPException(
                    status_code=403,
                    detail="Only SuperAdmin can assign Admin role"
                )
        elif role.name in ["Manager", "Accounts", "Customer"]:
            if assigned_by.role.name not in ["SuperAdmin", "Admin"]:
                raise HTTPException(
                    status_code=403,
                    detail="Only Admin or SuperAdmin can assign Manager, Accounts, or Customer roles"
                )
        
        user.role_id = role_id
        self.db.commit()
        self.db.refresh(user)
        return user
