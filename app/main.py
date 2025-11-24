# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import routers
from app.auth.router import router as auth_router
from app.users.router import router as user_router
from app.roles.router import router as role_router
from app.super_admin.router import router as super_admin_router

# Import database
from app.core.database import Base, engine

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Role-Based CRM API",
    description="Complete FastAPI authentication + RBAC system with dynamic roles",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Include routers
app.include_router(super_admin_router)  # Must be first - no auth required
app.include_router(auth_router)
app.include_router(user_router)
app.include_router(role_router)

@app.get("/")
def root():
    return {
        "message": "Role-Based CRM API is running!",
        "docs": "/docs",
        "setup": "POST /super-admin/init to create Super Admin (no auth required)"
    }
