#!/usr/bin/env python3
"""
Create Super Admin Script (Alternative to /super-admin/init endpoint)

This script creates the initial Super Admin user.
Run this ONCE manually before starting the application.

Usage:
    python create_super_admin.py
"""
import sys
import os

# Add the app directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.database import SessionLocal, Base, engine
from app.users.models import User
from app.roles.models import Role
from app.core.security import hash_password

def create_super_admin():
    """Create Super Admin user if it doesn't exist."""
    # Create tables if they don't exist
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # Check if SuperAdmin role exists
        super_admin_role = db.query(Role).filter(Role.name == "SuperAdmin").first()
        
        # Check if Super Admin user already exists
        if super_admin_role:
            existing_super_admin = db.query(User).filter(User.role_id == super_admin_role.id).first()
            if existing_super_admin:
                print("❌ Super Admin already exists!")
                print(f"   Email: {existing_super_admin.email}")
                print("   Run this script only once.")
                return False
        
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
        # Default credentials - CHANGE THESE IN PRODUCTION!
        super_admin_email = "superadmin@crm.com"
        super_admin_password = "SuperAdmin123!"  # Change this!
        
        # Check if email already exists
        existing_user = db.query(User).filter(User.email == super_admin_email).first()
        if existing_user:
            print(f"❌ User with email {super_admin_email} already exists!")
            return False
        
        # Create new Super Admin
        super_admin = User(
            email=super_admin_email,
            name="Super Admin",
            hashed_password=hash_password(super_admin_password),
            role_id=super_admin_role.id
        )
        db.add(super_admin)
        db.commit()
        print("✅ Super Admin created successfully!")
        print(f"\n📧 Email: {super_admin_email}")
        print(f"🔑 Password: {super_admin_password}")
        print("\n⚠️  IMPORTANT: Change the Super Admin password in production!")
        print("\n🚀 You can now start the application with: uvicorn app.main:app --reload")
        return True
    except Exception as e:
        db.rollback()
        print(f"❌ Error creating Super Admin: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    print("=" * 60)
    print("Super Admin Creation Script")
    print("=" * 60)
    print()
    success = create_super_admin()
    sys.exit(0 if success else 1)
