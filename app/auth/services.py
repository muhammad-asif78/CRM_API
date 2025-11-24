# app/auth/services.py
from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException
from app.users.models import User
from app.roles.models import Role
from app.core.security import hash_password, verify_password, create_access_token
from app.auth.schemas import RegisterRequest, LoginRequest

class AuthService:
    def __init__(self, db: Session):
        self.db = db

    def register(self, register_data: RegisterRequest) -> dict:
        """Register a new user."""
        existing_user = self.db.query(User).filter(User.email == register_data.email).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")

        # Validate role_id if provided
        role = None
        if register_data.role_id:
            role = self.db.query(Role).filter(Role.id == register_data.role_id).first()
            if not role:
                raise HTTPException(status_code=400, detail=f"Role with id {register_data.role_id} not found")
        else:
            raise HTTPException(status_code=400, detail="role_id is required")

        user = User(
            email=register_data.email,
            name=register_data.name or register_data.email.split("@")[0],
            hashed_password=hash_password(register_data.password),
            role_id=register_data.role_id
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)

        return {
            "message": "User registered successfully",
            "user": {
                "id": user.id,
                "email": user.email,
                "name": user.name,
                "role_id": user.role_id
            }
        }

    def login(self, login_data: LoginRequest) -> dict:
        """Login and get access token."""
        user = self.db.query(User).options(joinedload(User.role)).filter(User.email == login_data.email).first()
        if not user:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        if not verify_password(login_data.password, user.hashed_password):
            raise HTTPException(status_code=401, detail="Invalid credentials")

        token_data = {
            "id": user.id,
            "email": user.email,
            "role": user.role.name if user.role else None,
        }
        token = create_access_token(token_data)
        return {"access_token": token, "token_type": "bearer"}

    def get_roles_options(self) -> list:
        """Get all available roles from database."""
        roles = self.db.query(Role).all()
        return [
            {
                "id": role.id,
                "name": role.name,
                "description": role.description
            }
            for role in roles
        ]
