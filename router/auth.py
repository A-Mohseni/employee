from fastapi import APIRouter, HTTPException, status, Body, Depends, Response
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


@router.post("/login", response_model=TokenOut)
def login_route(data: LoginRequest = Body(...), response: Response = None):
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


@router.post("/logout")
async def logout(current_user: dict = Depends(get_current_user)):
    try:
        return {"message": "Logout successful"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error during logout: {str(e)}")


@router.post("/register")
def register_route(data: RegisterRequest = Body(...)):
    try:
        return register(data.employee_id, data.password, data.role)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e) or "Internal Server Error")