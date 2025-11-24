# app/auth/router.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from app.core.database import get_db
from app.auth.schemas import RegisterRequest, LoginRequest, TokenResponse
from app.auth.services import AuthService
from app.users.models import User
from app.dependencies.auth import get_current_user

router = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)

# Login
@router.post("/token", response_model=TokenResponse)
def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    """Login and get access token."""
    service = AuthService(db)
    return service.login(login_data)

# Get current user
@router.get("/me")
def get_me(current_user: User = Depends(get_current_user)):
    """Get current authenticated user information."""
    return {
        "id": current_user.id,
        "name": current_user.name,
        "email": current_user.email,
        "role": {
            "id": current_user.role.id,
            "name": current_user.role.name,
            "description": current_user.role.description
        } if current_user.role else None,
        "role_id": current_user.role_id
    }

# Get roles options
@router.get("/roles-options")
def get_roles_options(db: Session = Depends(get_db)):
    """
    Get all available roles from database.
    No authentication required - used for registration form.
    """
    service = AuthService(db)
    return service.get_roles_options()
