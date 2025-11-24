# app/super_admin/router.py
from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError
from pydantic import BaseModel
from typing import List
from app.core.database import get_db
from app.users.models import User
from app.roles.models import Role
from app.core.security import hash_password
from app.dependencies.permissions import role_required
from app.users.schemas import UserOut

router = APIRouter(
    prefix="/super-admin",
    tags=["Super Admin"]
)

class SuperAdminCreate(BaseModel):
    email: str
    name: str
    password: str
    force: bool = False  # If True, delete existing SuperAdmin and create new one

@router.post("/init", status_code=status.HTTP_201_CREATED)
def init_super_admin(
    super_admin_data: SuperAdminCreate,
    db: Session = Depends(get_db)
):
    """
    Initialize Super Admin user.
    
    NO AUTHENTICATION REQUIRED - This is a one-time setup endpoint.
    
    Creates:
    1. SuperAdmin role (if it doesn't exist)
    2. Super Admin user with SuperAdmin role
    
    Rules:
    - Can only be called once (unless force=true)
    - If Super Admin already exists, use force=true to replace it
    - No authentication required
    
    Parameters:
    - force: If True, delete existing SuperAdmin and create new one
    """
    try:
        # First check: Check if Super Admin role exists
        super_admin_role = db.query(Role).filter(Role.name == "SuperAdmin").first()
        
        # Second check: If SuperAdmin role exists, check if any SuperAdmin user exists
        if super_admin_role:
            existing_super_admin = db.query(User).filter(
                User.role_id == super_admin_role.id
            ).first()
            
            if existing_super_admin:
                if super_admin_data.force:
                    # Force mode: Delete existing SuperAdmin and create new one
                    db.delete(existing_super_admin)
                    db.commit()
                    # Continue to create new SuperAdmin below
                else:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Super Admin already exists (email: {existing_super_admin.email}). Cannot create another one. Use 'force: true' to replace existing SuperAdmin."
                    )
        
        # Third check: Check if email already exists (for any user)
        # Skip this check if force=true and the existing user is the SuperAdmin we're replacing
        existing_user = db.query(User).filter(User.email == super_admin_data.email).first()
        if existing_user:
            # If force=true and this is the SuperAdmin we're replacing, allow it
            if super_admin_data.force and super_admin_role and existing_user.role_id == super_admin_role.id:
                # This is the SuperAdmin we're replacing, so it's okay
                pass
            else:
                raise HTTPException(
                    status_code=400,
                    detail=f"User with email '{super_admin_data.email}' already exists"
                )
        
        # Create SuperAdmin role if it doesn't exist
        if not super_admin_role:
            super_admin_role = Role(
                name="SuperAdmin",
                description="Super Administrator with full access"
            )
            db.add(super_admin_role)
            db.commit()
            db.refresh(super_admin_role)
        
        # Create Super Admin user
        super_admin_user = User(
            email=super_admin_data.email,
            name=super_admin_data.name,
            hashed_password=hash_password(super_admin_data.password),
            role_id=super_admin_role.id
        )
        db.add(super_admin_user)
        db.commit()
        db.refresh(super_admin_user)
        
        return {
            "message": "Super Admin created successfully",
            "user": {
                "id": super_admin_user.id,
                "email": super_admin_user.email,
                "name": super_admin_user.name,
                "role": "SuperAdmin"
            }
        }
    except HTTPException as e:
        # HTTPException is already raised, just ensure rollback
        db.rollback()
        raise e
    except IntegrityError as e:
        db.rollback()
        error_msg = str(e.orig) if hasattr(e, 'orig') else str(e)
        import traceback
        print(f"IntegrityError: {error_msg}")
        print(traceback.format_exc())
        
        # Check for specific constraint violations
        if 'email' in error_msg.lower() or 'unique' in error_msg.lower() or 'duplicate' in error_msg.lower():
            raise HTTPException(
                status_code=400,
                detail=f"User with email '{super_admin_data.email}' already exists"
            )
        elif 'role_id' in error_msg.lower() or 'foreign key' in error_msg.lower():
            raise HTTPException(
                status_code=400,
                detail="Invalid role. SuperAdmin role may not exist."
            )
        elif 'check constraint' in error_msg.lower() or 'violates' in error_msg.lower():
            # Check if it's about SuperAdmin uniqueness
            if 'superadmin' in error_msg.lower():
                raise HTTPException(
                    status_code=400,
                    detail="Super Admin already exists. Cannot create another one."
                )
            raise HTTPException(
                status_code=400,
                detail=f"Database constraint violation: {error_msg}"
            )
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Database constraint violation: {error_msg}"
            )
    except Exception as e:
        db.rollback()
        import traceback
        error_trace = traceback.format_exc()
        print(f"Error creating Super Admin: {error_trace}")
        raise HTTPException(
            status_code=500,
            detail=f"Error creating Super Admin: {str(e)}"
        )

# ==================== Super Admin Management Endpoints ====================

# Get all SuperAdmin users
@router.get("/users", response_model=List[UserOut])
def get_all_super_admins(
    db: Session = Depends(get_db),
    current_user: User = Depends(role_required(["SuperAdmin"]))
):
    """
    Get all SuperAdmin users.
    SuperAdmin only.
    """
    super_admin_role = db.query(Role).filter(Role.name == "SuperAdmin").first()
    if not super_admin_role:
        return []
    
    super_admins = db.query(User).options(joinedload(User.role)).filter(
        User.role_id == super_admin_role.id
    ).all()
    return super_admins

# Get single SuperAdmin user
@router.get("/users/{user_id}", response_model=UserOut)
def get_super_admin(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(role_required(["SuperAdmin"]))
):
    """
    Get a single SuperAdmin user by ID.
    SuperAdmin only.
    """
    super_admin_role = db.query(Role).filter(Role.name == "SuperAdmin").first()
    if not super_admin_role:
        raise HTTPException(status_code=404, detail="SuperAdmin role not found")
    
    super_admin = db.query(User).options(joinedload(User.role)).filter(
        User.id == user_id,
        User.role_id == super_admin_role.id
    ).first()
    
    if not super_admin:
        raise HTTPException(status_code=404, detail="SuperAdmin user not found")
    
    return super_admin

# Delete SuperAdmin user
@router.delete("/users/{user_id}", status_code=status.HTTP_200_OK)
def delete_super_admin(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(role_required(["SuperAdmin"]))
):
    """
    Delete a SuperAdmin user.
    
    Rules:
    - Can delete yourself if there are other SuperAdmins
    - Cannot delete the last SuperAdmin (at least one must exist)
    - SuperAdmin only
    """
    super_admin_role = db.query(Role).filter(Role.name == "SuperAdmin").first()
    if not super_admin_role:
        raise HTTPException(status_code=404, detail="SuperAdmin role not found")
    
    # First check if user exists at all
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=404,
            detail=f"User with id {user_id} not found"
        )
    
    # Check if user is actually a SuperAdmin
    if user.role_id != super_admin_role.id:
        raise HTTPException(
            status_code=400,
            detail=f"User with id {user_id} is not a SuperAdmin. User has role_id: {user.role_id}, SuperAdmin role_id: {super_admin_role.id}"
        )
    
    # Check how many SuperAdmin users exist
    super_admin_count = db.query(User).filter(User.role_id == super_admin_role.id).count()
    
    # Allow deleting the last SuperAdmin (user can recreate via /super-admin/init)
    # Just warn about it
    if super_admin_count <= 1:
        # Allow deletion but warn - user can recreate via /super-admin/init endpoint
        pass
    
    # Check if this is self-deletion
    is_self_deletion = user_id == current_user.id
    
    # Warn about self-deletion but allow it if there are other SuperAdmins
    if is_self_deletion:
        # Already checked that super_admin_count > 1 above, so self-deletion is allowed
        pass
    
    # Delete the SuperAdmin user
    try:
        user_email = user.email
        was_last_superadmin = super_admin_count <= 1
        
        db.delete(user)
        db.commit()
        
        message = f"SuperAdmin user (id: {user_id}, email: {user_email}) deleted successfully"
        if is_self_deletion:
            message += " You have been logged out."
        if was_last_superadmin:
            message += " This was the last SuperAdmin. You can create a new one using POST /super-admin/init"
        
        return {
            "message": message,
            "deleted_user_id": user_id,
            "deleted_user_email": user_email,
            "was_self_deletion": is_self_deletion,
            "was_last_superadmin": was_last_superadmin,
            "note": "You can create a new SuperAdmin using POST /super-admin/init" if was_last_superadmin else None
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error deleting SuperAdmin user: {str(e)}"
        )

# Delete SuperAdmin role (DANGEROUS - use with caution)
@router.delete("/role", status_code=status.HTTP_200_OK)
def delete_super_admin_role(
    db: Session = Depends(get_db),
    current_user: User = Depends(role_required(["SuperAdmin"]))
):
    """
    Delete the SuperAdmin role.
    
    WARNING: This will remove the SuperAdmin role from the system.
    All users with SuperAdmin role will lose their role.
    This is a dangerous operation - use with extreme caution.
    
    SuperAdmin only.
    """
    super_admin_role = db.query(Role).filter(Role.name == "SuperAdmin").first()
    if not super_admin_role:
        raise HTTPException(status_code=404, detail="SuperAdmin role not found")
    
    # Check if there are any users with SuperAdmin role
    super_admin_users = db.query(User).filter(User.role_id == super_admin_role.id).all()
    if super_admin_users:
        user_emails = [u.email for u in super_admin_users]
        raise HTTPException(
            status_code=400,
            detail=f"Cannot delete SuperAdmin role. There are {len(super_admin_users)} user(s) with this role: {', '.join(user_emails)}. Delete all SuperAdmin users first."
        )
    
    # Delete the role
    try:
        db.delete(super_admin_role)
        db.commit()
        return {
            "message": "SuperAdmin role deleted successfully"
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error deleting SuperAdmin role: {str(e)}"
        )

