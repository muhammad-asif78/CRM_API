# app/roles/router.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.roles.models import Role
from app.roles.schemas import RoleCreate, RoleUpdate, RoleOut
from app.roles.services import RoleService
from app.users.models import User
from app.dependencies.permissions import role_required

router = APIRouter(
    prefix="/roles",
    tags=["Roles"]
)

# Get all roles
@router.get("/", response_model=List[RoleOut])
def get_roles(
    db: Session = Depends(get_db),
    current_user: User = Depends(role_required(["SuperAdmin"]))
):
    """Get all roles. SuperAdmin only."""
    service = RoleService(db)
    return service.get_all_roles()

# Get single role
@router.get("/{role_id}", response_model=RoleOut)
def get_role(
    role_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(role_required(["SuperAdmin"]))
):
    """Get a single role by ID. SuperAdmin only."""
    service = RoleService(db)
    return service.get_role(role_id)

# Create role
@router.post("/", response_model=RoleOut, status_code=status.HTTP_201_CREATED)
def create_role(
    role_in: RoleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(role_required(["SuperAdmin", "Admin"]))
):
    """
    Create a new role.
    
    Rules:
    - SuperAdmin can create Admin role
    - Admin can create Manager, Accounts, Customer roles
    - No one else can create roles
    """
    service = RoleService(db)
    
    # Check role creation rules
    if role_in.name == "SuperAdmin":
        raise HTTPException(
            status_code=403,
            detail="Cannot create SuperAdmin role. It is created automatically."
        )
    elif role_in.name == "Admin":
        # Only SuperAdmin can create Admin role
        if current_user.role.name != "SuperAdmin":
            raise HTTPException(
                status_code=403,
                detail="Only SuperAdmin can create Admin role"
            )
    elif role_in.name in ["Manager", "Accounts", "Customer"]:
        # Admin can create these roles
        if current_user.role.name not in ["SuperAdmin", "Admin"]:
            raise HTTPException(
                status_code=403,
                detail="Only Admin or SuperAdmin can create Manager, Accounts, or Customer roles"
            )
    else:
        # For any other role, only SuperAdmin can create
        if current_user.role.name != "SuperAdmin":
            raise HTTPException(
                status_code=403,
                detail="Only SuperAdmin can create custom roles"
            )
    
    return service.create_role(role_in)

# Update role
@router.put("/{role_id}", response_model=RoleOut)
def update_role(
    role_id: int,
    role_in: RoleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(role_required(["SuperAdmin"]))
):
    """Update a role. SuperAdmin only."""
    service = RoleService(db)
    
    # Get existing role to check name
    existing_role = service.get_role(role_id)
    
    # Prevent updating SuperAdmin role
    if existing_role.name == "SuperAdmin":
        raise HTTPException(
            status_code=403,
            detail="Cannot update SuperAdmin role"
        )
    
    # Check if trying to change to Admin role
    if role_in.name == "Admin" and existing_role.name != "Admin":
        if current_user.role.name != "SuperAdmin":
            raise HTTPException(
                status_code=403,
                detail="Only SuperAdmin can update role to Admin"
            )
    
    return service.update_role(role_id, role_in)

# Delete role
@router.delete("/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_role(
    role_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(role_required(["SuperAdmin"]))
):
    """Delete a role. SuperAdmin only."""
    service = RoleService(db)
    
    # Get role to check if it's SuperAdmin or Admin
    role = service.get_role(role_id)
    if role.name == "SuperAdmin":
        raise HTTPException(
            status_code=403,
            detail="Cannot delete SuperAdmin role"
        )
    elif role.name == "Admin":
        if current_user.role.name != "SuperAdmin":
            raise HTTPException(
                status_code=403,
                detail="Only SuperAdmin can delete Admin role"
            )
    
    service.delete_role(role_id)
    return None
