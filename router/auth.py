from fastapi import APIRouter, HTTPException, status, Body, Depends, Response, Query
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from utils.error_handler import exception_handler
from utils.db import get_db
from utils.password_hash import verify_password
from services.auth import get_current_user, require_roles
from services.token import deactivate_token
from models.auth import LoginRequest, AdminCreate, AdminOut
from services.auth import login, create_admin, admin_login

router = APIRouter(prefix="/auth", tags=["auth"])


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    user_id: str


# =============================================================================
# 🔐 LOGIN ENDPOINTS
# =============================================================================

@router.post("/login", response_model=TokenOut)
def login_employee(data: LoginRequest = Body(...), response: Response = None):
    """
    Login for employees (non-admin users)
    """
    try:
        login_data = login(data.employee_id, data.password)
        token = login_data["token"]
        user_id = login_data["user_id"]
        role = login_data["role"]
        
        try:
            from services.token import create_token
            create_token(user_id, token, expires_in_minutes=30)
        except Exception as e:
            print(f"Warning: Could not store token in database: {e}")

        if response is not None:
            try:
                response.set_cookie(
                    key="access_token",
                    value=f"Bearer {token}",
                    httponly=True,
                    secure=False,
                    samesite="lax",
                    max_age=60*30
                )
                response.headers["Authorization"] = f"Bearer {token}"
            except Exception:
                pass

        return TokenOut(access_token=token, role=role, user_id=user_id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e) or "Internal Server Error")


@router.post("/admin/login", response_model=TokenOut)
def login_admin(data: LoginRequest = Body(...), response: Response = None):
    """
    Login for admins
    """
    try:
        login_data = admin_login(data.employee_id, data.password)
        token = login_data["token"]
        user_id = login_data["user_id"]
        role = login_data["role"]
        
        try:
            from services.token import create_token
            create_token(user_id, token, expires_in_minutes=30)
        except Exception as e:
            print(f"Warning: Could not store token in database: {e}")

        if response is not None:
            try:
                response.set_cookie(
                    key="access_token",
                    value=f"Bearer {token}",
                    httponly=True,
                    secure=False,
                    samesite="lax",
                    max_age=60*30
                )
                response.headers["Authorization"] = f"Bearer {token}"
            except Exception:
                pass

        return TokenOut(access_token=token, role=role, user_id=user_id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e) or "Internal Server Error")


# =============================================================================
# 🚪 LOGOUT ENDPOINT
# =============================================================================

@router.post("/logout")
async def logout(current_user: dict = Depends(get_current_user)):
    """
    Logout from system
    """
    try:
        return {"message": "Logout successful"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error during logout: {str(e)}")


# =============================================================================
# 👑 ADMIN MANAGEMENT ENDPOINTS
# =============================================================================


@router.post("/admin/create", response_model=AdminOut)
def create_new_admin(
    data: AdminCreate = Body(...),
    current_user: dict = Depends(require_roles("admin1"))
):
 
    try:
        result = create_admin(
            employee_id=data.employee_id,
            password=data.password,
            full_name=data.full_name,
            phone=data.phone,
            email=data.email,
            role=data.role,
            is_super_admin=data.is_super_admin
        )
        
        # Get the created admin data
        db = get_db()
        admins = db["admins"]
        admin = admins.find_one({"employee_id": data.employee_id})
        
        if admin:
            return AdminOut(
                id=str(admin["_id"]),
                employee_id=admin["employee_id"],
                full_name=admin["full_name"],
                role=admin["role"],
                status=admin["status"],
                phone=admin["phone"],
                email=admin["email"],
                is_super_admin=admin["is_super_admin"],
                created_at=admin["created_at"],
                updated_at=admin["updated_at"]
            )
        else:
            return {"message": "Admin created successfully"}
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e) or "Internal Server Error")


@router.get("/admin/list")
def list_admins(current_user: dict = Depends(require_roles("admin1", "admin2"))):
    
    
    try:
        db = get_db()
        admins = db["admins"]
        
        admin_list = []
        for admin in admins.find({}):
            admin_list.append(AdminOut(
                id=str(admin["_id"]),
                employee_id=admin["employee_id"],
                full_name=admin["full_name"],
                role=admin["role"],
                status=admin["status"],
                phone=admin["phone"],
                email=admin["email"],
                is_super_admin=admin["is_super_admin"],
                created_at=admin["created_at"],
                updated_at=admin["updated_at"]
            ))
        
        return admin_list
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e) or "Internal Server Error")


# =============================================================================
# 👥 USER MANAGEMENT ENDPOINTS (for admins)
# =============================================================================

@router.post("/user/create")
def create_user_by_admin(
    user_data: dict = Body(...),
    current_user: dict = Depends(require_roles("admin1", "admin2"))
):
   
    try:
        from services.user import create_user
        from models.user import employee_create
        
        # Convert dict to employee_create model
        user = employee_create(
            employee_id=user_data["employee_id"],
            full_name=user_data["full_name"],
            role=user_data["role"],
            phone=user_data.get("phone", ""),
            email=user_data.get("email", ""),
            password=user_data.get("password", "default123"),
            status=user_data.get("status", "active")
        )
        
        result = create_user(user, current_user, return_token=True)
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e) or "Internal Server Error")


@router.get("/user/list")
def list_users(current_user: dict = Depends(require_roles("admin1", "admin2"))):
    """
    List all users
    Only admins can view user list
    """
    try:
        from services.user import get_all_users
        return get_all_users(current_user)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e) or "Internal Server Error")