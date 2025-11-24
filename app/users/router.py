# app/users/router.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from typing import List

from app.core.database import get_db
from app.users.models import User
from app.users.schemas import UserCreate, UserUpdate, UserOut
from app.users.services import UserService
from app.dependencies.permissions import role_required
from app.dependencies.auth import get_current_user

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

# Create user
@router.post("/create", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def create_user(
    user_in: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(role_required(["SuperAdmin", "Admin"]))
):
    """
    Create a new user.
    
    Rules:
    - SuperAdmin can create Admin users
    - Admin can create Manager, Accounts, Customer users
    """
    service = UserService(db)
    user = service.create_user(user_in, current_user)
    # Reload with role relationship
    user = db.query(User).options(joinedload(User.role)).filter(User.id == user.id).first()
    return user

# Get all users
@router.get("/", response_model=List[UserOut])
def get_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(role_required(["SuperAdmin", "Admin"]))
):
    """
    Get all users.
    
    Rules:
    - SuperAdmin sees all users
    - Admin sees Manager, Accounts, Customer users (not SuperAdmin or Admin)
    """
    service = UserService(db)
    users = service.get_all_users()
    
    # Filter based on role
    if current_user.role.name == "SuperAdmin":
        # SuperAdmin sees all
        pass
    elif current_user.role.name == "Admin":
        # Admin sees non-SuperAdmin, non-Admin users
        users = [u for u in users if u.role and u.role.name not in ["SuperAdmin", "Admin"]]
    else:
        # Others see only themselves
        users = [u for u in users if u.id == current_user.id]
    
    # Load role relationships
    user_ids = [u.id for u in users]
    users_with_roles = db.query(User).options(joinedload(User.role)).filter(User.id.in_(user_ids)).all()
    return users_with_roles

# Get single user
@router.get("/{user_id}", response_model=UserOut)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get a single user by ID.
    
    Rules:
    - Users can only see their own profile unless they have permission
    """
    user = db.query(User).options(joinedload(User.role)).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check permissions
    if user_id != current_user.id:
        if not (current_user.role and current_user.role.name in ["SuperAdmin", "Admin"]):
            raise HTTPException(
                status_code=403,
                detail="You can only view your own profile"
            )
        # Admin can't see SuperAdmin or Admin users
        if current_user.role.name == "Admin":
            if user.role and user.role.name in ["SuperAdmin", "Admin"]:
                raise HTTPException(
                    status_code=403,
                    detail="Admin cannot view SuperAdmin or Admin users"
                )
    
    return user

# Update user
@router.put("/{user_id}", response_model=UserOut)
def update_user(
    user_id: int,
    user_in: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update a user.
    
    Rules:
    - SuperAdmin can update Admin users
    - Admin can update Manager, Accounts, Customer users
    - Others can only update their own data
    """
    user = db.query(User).options(joinedload(User.role)).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if user can update
    if user_id != current_user.id:
        # Not updating self - need permission
        if not (current_user.role and current_user.role.name in ["SuperAdmin", "Admin"]):
            raise HTTPException(
                status_code=403,
                detail="You can only update your own profile"
            )
    
    service = UserService(db)
    user = service.update_user(user_id, user_in, current_user)
    # Reload with role relationship
    user = db.query(User).options(joinedload(User.role)).filter(User.id == user.id).first()
    return user

# Delete user
@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(role_required(["SuperAdmin", "Admin"]))
):
    """
    Delete a user.
    
    Rules:
    - SuperAdmin can delete Admin users
    - Admin can delete Manager, Accounts, Customer users
    """
    service = UserService(db)
    service.delete_user(user_id, current_user)
    return None

# Assign role to user
@router.put("/{user_id}/assign-role/{role_id}", response_model=UserOut)
def assign_role(
    user_id: int,
    role_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(role_required(["SuperAdmin", "Admin"]))
):
    """
    Assign a role to a user.
    
    Rules:
    - SuperAdmin can assign Admin role
    - Admin can assign Manager, Accounts, Customer roles
    """
    service = UserService(db)
    user = service.assign_role(user_id, role_id, current_user)
    # Reload with role relationship
    user = db.query(User).options(joinedload(User.role)).filter(User.id == user.id).first()
    return user
