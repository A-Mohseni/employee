from fastapi import APIRouter, HTTPException, status, Body, Depends
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from utils.error_handler import exception_handler
from utils.db import get_db
from utils.password_hash import verify_password
from services.auth import get_current_user
from services.token import deactivate_token
from models.auth import LoginRequest, RegisterRequest
from services.auth import login, register

router = APIRouter(prefix="/auth", tags=["auth"])


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    user_id: str


@exception_handler
@router.post("/login", response_model=TokenOut)
def login_route(data: LoginRequest = Body(...)):
    # Delegate authentication to service
    login_data = login(data.employee_id, data.password)
    token = login_data["token"]
    user_id = login_data["user_id"]
    role = login_data["role"]

    # Store token in database for revocation support
    try:
        from services.token import create_token
        create_token(user_id, token, expires_in_minutes=30)
    except Exception as e:
        print(f"Warning: Could not store token in database: {e}")

    return TokenOut(access_token=token, role=role, user_id=user_id)


@exception_handler
@router.post("/logout")
async def logout(current_user: dict = Depends(get_current_user)):
    try:
        return {"message": "Logout successful"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error during logout: {str(e)}"
        )


@exception_handler
@router.post("/register")
def register_route(data: RegisterRequest = Body(...)):
    return register(data.employee_id, data.password, data.role)