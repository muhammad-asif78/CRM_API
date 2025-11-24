# app/dependencies/permissions.py
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.dependencies.auth import get_current_user
from app.core.database import get_db
from app.users.models import User
from typing import List

def role_required(allowed_roles: List[str]):
    """
    Dependency to restrict access based on role names.
    
    Usage:
        @router.get("/admin-route")
        def route(user: User = Depends(role_required(["SuperAdmin", "Admin"]))):
            ...
    
    Rules:
    - SuperAdmin bypasses all restrictions (checks role.name == "SuperAdmin")
    - Checks if user's role.name is in allowed_roles
    """
    def role_checker(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
    ):
        # Check if user has a role
        if not current_user.role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User has no role assigned"
            )
        
        # SuperAdmin bypasses all restrictions
        if current_user.role.name == "SuperAdmin":
            return current_user
        
        # Check if user's role is in allowed roles
        role_name = current_user.role.name
        if role_name not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{role_name}' is not allowed. Required roles: {allowed_roles}"
            )
        
        return current_user

    return role_checker
