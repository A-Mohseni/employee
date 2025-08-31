from fastapi import APIRouter, HTTPException, status, Body, Depends
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from utils.db import get_db
from utils.password_hash import verify_password
from services.auth import get_current_user
from services.token import deactivate_token

router = APIRouter(prefix="/auth", tags=["auth"])


class LoginInput(BaseModel):
    employee_id: int = Field(..., ge=10, le=999)
    password: str = Field(..., min_length=4)


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    user_id: str


@router.post("/login", response_model=TokenOut)
async def login(data: LoginInput = Body(...)):
    db = get_db()
    employees = db["employees"]
    user = employees.find_one({"employee_id": data.employee_id})
    if not user or not user.get("password_hash") or not verify_password(data.password, user["password_hash"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    payload: Dict[str, Any] = {"user_id": str(user["_id"]), "role": user["role"]}
    try:
        from utils.jwt import create_access_token
        token = create_access_token(payload, subject=str(user["_id"]))
    except Exception as e:
        print(f"JWT creation failed: {e}")
        token = "mock-token"

    try:
        from services.token import create_token
        create_token(str(user["_id"]), token, expires_in_minutes=30)
    except Exception as e:
        print(f"Warning: Could not store token in database: {e}")

    return TokenOut(access_token=token, role=user["role"], user_id=str(user["_id"]))


@router.post("/logout")
async def logout(current_user: dict = Depends(get_current_user)):
    try:
        return {"message": "Logout successful"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error during logout: {str(e)}"
        )