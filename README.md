# Role-Based CRM API

Complete FastAPI authentication + RBAC system with dynamic roles.

## 🚀 Quick Start

### 1. Create Super Admin (Run Once)

```bash
python create_super_admin.py
```

This creates the initial Super Admin:
- Email: `superadmin@crm.com`
- Password: `SuperAdmin123!`

**⚠️ Change the password in production!**

### 2. Start the Application

```bash
uvicorn app.main:app --reload
```

### 3. Access API Documentation

Open your browser: `http://localhost:8000/docs`

## 📁 Project Structure

```
app/
├── roles/              # Role management module
│   ├── models.py       # Role SQLAlchemy model
│   ├── schemas.py      # Role Pydantic schemas
│   ├── services.py     # Role business logic
│   └── router.py       # Role API endpoints
│
├── users/              # User management module
│   ├── models.py       # User SQLAlchemy model
│   ├── schemas.py      # User Pydantic schemas
│   ├── services.py     # User business logic
│   └── router.py       # User API endpoints
│
├── auth/               # Authentication module
│   ├── schemas.py      # Auth Pydantic schemas
│   ├── services.py     # Auth business logic
│   └── router.py       # Auth API endpoints
│
├── dependencies/       # Dependencies
│   ├── auth.py        # get_current_user dependency
│   └── permissions.py # role_required dependency
│
├── core/              # Core utilities
│   ├── database.py    # Database setup
│   ├── security.py    # Password hashing, JWT
│   └── config.py      # Configuration
│
└── main.py            # FastAPI application

create_super_admin.py  # Super Admin creation script
```

## 🔐 Role Hierarchy

### Super Admin
- ✅ Create Admin users
- ✅ Delete Admin users
- ✅ View ALL roles
- ✅ Create ANY new role
- ✅ Assign ANY role
- ✅ Full access everywhere
- ✅ Bypasses all restrictions

### Admin
- ✅ Create Manager, Accounts, Customer users
- ✅ Assign Manager, Accounts, Customer roles
- ✅ Update/Delete Manager, Accounts, Customer users
- ❌ Cannot create Super Admin or Admin
- ❌ Cannot delete Super Admin or Admin
- ❌ Cannot view Super Admin or Admin users

### Manager
- ✅ Can see customer list
- ❌ Limited access

### Accounts
- ✅ Can see billing/finance APIs
- ❌ Limited access

### Customer
- ✅ Only sees their own profile
- ❌ Limited access

## 📡 API Endpoints

### Auth Endpoints (`/auth`)

- `POST /auth/register` - Register new user
- `POST /auth/token` - Login and get token
- `GET /auth/me` - Get current user info
- `GET /auth/roles-options` - Get all roles (for registration form)

### User Endpoints (`/users`)

- `POST /users/create` - Create user (Super Admin/Admin)
- `GET /users/` - Get all users (filtered by role)
- `GET /users/{id}` - Get single user
- `PUT /users/{id}` - Update user (Super Admin/Admin)
- `DELETE /users/{id}` - Delete user (Super Admin/Admin)
- `PUT /users/{id}/assign-role/{role_id}` - Assign role to user

### Role Endpoints (`/roles`)

- `POST /roles/` - Create role (Super Admin/Admin)
- `GET /roles/` - Get all roles (Super Admin)
- `GET /roles/{id}` - Get single role (Super Admin)
- `PUT /roles/{id}` - Update role (Super Admin)
- `DELETE /roles/{id}` - Delete role (Super Admin)

## 🔑 Role Creation Rules

1. **Super Admin** can create:
   - Admin role
   - Any custom role

2. **Admin** can create:
   - Manager role
   - Accounts role
   - Customer role

3. **No one else** can create roles

## 🛡️ Permission System

Use the `role_required` dependency:

```python
from app.dependencies.permissions import role_required

@router.get("/admin-only")
def admin_route(user: User = Depends(role_required(["SuperAdmin", "Admin"]))):
    # Only Super Admin or Admin can access
    pass
```

**Rules:**
- Super Admin bypasses all restrictions
- Checks `user.role.name` against allowed roles
- Returns 403 if role not allowed

## 📝 Usage Examples

### 1. Login as Super Admin

```bash
curl -X POST "http://localhost:8000/auth/token" \
  -H "Content-Type: application/json" \
  -d '{"email": "superadmin@crm.com", "password": "SuperAdmin123!"}'
```

### 2. Create Admin Role (as Super Admin)

```bash
curl -X POST "http://localhost:8000/roles/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "Admin", "description": "Administrator role"}'
```

### 3. Create Admin User (as Super Admin)

```bash
curl -X POST "http://localhost:8000/users/create" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@crm.com", "password": "Admin123!", "name": "Admin User", "role_id": 1}'
```

### 4. Create Manager Role (as Admin)

```bash
curl -X POST "http://localhost:8000/roles/" \
  -H "Authorization: Bearer ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "Manager", "description": "Manager role"}'
```

## ⚠️ Important Notes

1. **No hardcoded roles** - Everything comes from database
2. **Dynamic permissions** - Based on role names in database
3. **Super Admin creation** - Only via `create_super_admin.py` script
4. **Role hierarchy** - Enforced in service layer
5. **Database-driven** - All roles and permissions from DB

## 🔧 Environment Variables

Create a `.env` file:

```env
DATABASE_URL=postgresql://user:password@localhost/dbname
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_SECONDS=86400
```

## 📦 Dependencies

- FastAPI
- SQLAlchemy
- Pydantic
- python-jose (JWT)
- passlib (password hashing)
- psycopg2 (PostgreSQL)

## 🎯 Features

✅ Complete RBAC system
✅ Dynamic role-based permissions
✅ No hardcoded roles
✅ Folder-based modular structure
✅ Super Admin creation script
✅ JWT authentication
✅ Password hashing
✅ Role hierarchy enforcement
✅ Database-driven everything

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

