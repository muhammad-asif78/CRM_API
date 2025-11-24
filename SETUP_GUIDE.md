# FastAPI RBAC System - Setup Guide

## 🚀 Quick Start

### Step 1: Create Super Admin

**Option A: Using API Endpoint (Recommended)**
```bash
curl -X POST "http://localhost:8000/super-admin/init" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "superadmin@crm.com",
    "name": "Super Admin",
    "password": "SuperAdmin123!"
  }'
```

**Option B: Using Script**
```bash
python create_super_admin.py
```

**Important:** 
- ✅ NO AUTHENTICATION REQUIRED
- ✅ Can only be called ONCE
- ✅ Creates SuperAdmin role and user

### Step 2: Start the Application

```bash
uvicorn app.main:app --reload
```

### Step 3: Login as Super Admin

```bash
curl -X POST "http://localhost:8000/auth/token" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "superadmin@crm.com",
    "password": "SuperAdmin123!"
  }'
```

### Step 4: Create Admin Role

```bash
curl -X POST "http://localhost:8000/roles/" \
  -H "Authorization: Bearer YOUR_SUPERADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Admin",
    "description": "Administrator role"
  }'
```

### Step 5: Create Admin User

```bash
curl -X POST "http://localhost:8000/users/create" \
  -H "Authorization: Bearer YOUR_SUPERADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@crm.com",
    "name": "Admin User",
    "password": "Admin123!",
    "role_id": 2
  }'
```

## 📁 Project Structure

```
app/
├── core/               # Core utilities
│   ├── database.py    # Database setup
│   └── security.py    # Password hashing, JWT
│
├── super_admin/       # Super Admin initialization
│   └── router.py     # POST /super-admin/init (NO AUTH)
│
├── auth/              # Authentication
│   ├── router.py     # POST /auth/token, GET /auth/me, GET /auth/roles-options
│   ├── services.py   # Auth business logic
│   └── schemas.py    # Auth schemas
│
├── users/             # User management
│   ├── models.py     # User SQLAlchemy model
│   ├── schemas.py    # User Pydantic schemas
│   ├── services.py   # User business logic
│   └── router.py     # User CRUD endpoints
│
├── roles/             # Role management
│   ├── models.py     # Role SQLAlchemy model
│   ├── schemas.py    # Role Pydantic schemas
│   ├── services.py   # Role business logic
│   └── router.py     # Role CRUD endpoints
│
├── dependencies/      # Dependencies
│   ├── auth.py       # get_current_user
│   └── permissions.py # role_required dependency
│
└── main.py           # FastAPI application
```

## 🔐 Role Hierarchy

### SuperAdmin
- ✅ Create Admin role
- ✅ Create Admin users
- ✅ Delete Admin users
- ✅ Assign Admin role
- ✅ View ALL roles
- ✅ Create ANY role
- ✅ Full access everywhere
- ✅ Bypasses all permission checks

### Admin
- ✅ Create Manager, Accounts, Customer roles
- ✅ Create Manager, Accounts, Customer users
- ✅ Assign Manager, Accounts, Customer roles
- ✅ Update/Delete Manager, Accounts, Customer users
- ❌ Cannot create SuperAdmin or Admin
- ❌ Cannot delete SuperAdmin or Admin
- ❌ Cannot view SuperAdmin or Admin users

### Manager / Accounts / Customer
- ✅ Can only update their own data
- ❌ Limited access

## 📡 API Endpoints

### Super Admin Init (NO AUTH)
- `POST /super-admin/init` - Create Super Admin (one-time, no auth)

### Auth Endpoints
- `POST /auth/token` - Login and get token
- `GET /auth/me` - Get current user info
- `GET /auth/roles-options` - Get all roles from DB

### User Endpoints (Protected)
- `POST /users/create` - Create user (SuperAdmin/Admin)
- `GET /users/` - Get all users (filtered by role)
- `GET /users/{id}` - Get single user
- `PUT /users/{id}` - Update user
- `DELETE /users/{id}` - Delete user
- `PUT /users/{id}/assign-role/{role_id}` - Assign role

### Role Endpoints (Protected)
- `POST /roles/` - Create role (SuperAdmin/Admin)
- `GET /roles/` - Get all roles (SuperAdmin only)
- `GET /roles/{id}` - Get single role (SuperAdmin only)
- `PUT /roles/{id}` - Update role (SuperAdmin only)
- `DELETE /roles/{id}` - Delete role (SuperAdmin only)

## 🛡️ Permission System

Use the `role_required` dependency:

```python
from app.dependencies.permissions import role_required

@router.get("/admin-only")
def admin_route(user: User = Depends(role_required(["SuperAdmin", "Admin"]))):
    # Only SuperAdmin or Admin can access
    pass
```

**Rules:**
- SuperAdmin bypasses all restrictions (checks `role.name == "SuperAdmin"`)
- Checks `user.role.name` against allowed roles
- Returns 403 if role not allowed

## 🔑 Role Creation Rules

1. **SuperAdmin** can create:
   - Admin role
   - Any custom role

2. **Admin** can create:
   - Manager role
   - Accounts role
   - Customer role

3. **SuperAdmin role** is created automatically via `/super-admin/init`
4. **No one** can create SuperAdmin role manually

## ⚠️ Important Notes

1. ✅ **No hardcoded roles** - Everything comes from database
2. ✅ **SuperAdmin is a role** - Stored in roles table, not a boolean flag
3. ✅ **Dynamic permissions** - Based on role names in database
4. ✅ **One-time Super Admin creation** - Via `/super-admin/init` (no auth)
5. ✅ **Role-based checks** - All checks use `role.name == "SuperAdmin"`

## 🎯 Working Flow

1. ✅ Call `POST /super-admin/init` → Creates SuperAdmin role and user
2. ✅ SuperAdmin login `POST /auth/token`
3. ✅ SuperAdmin creates "Admin" role `POST /roles/`
4. ✅ SuperAdmin creates Admin user `POST /users/create`
5. ✅ Admin login `POST /auth/token`
6. ✅ Admin creates Manager/Accounts/Customer roles `POST /roles/`
7. ✅ Only authorized roles can access restricted endpoints

## 🔧 Environment Variables

Create a `.env` file:

```env
DATABASE_URL=postgresql://user:password@localhost/dbname
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_SECONDS=86400
```

