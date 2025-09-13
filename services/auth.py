from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from utils.db import get_db
from utils.jwt import create_access_token, verify_token
from utils.password_hash import verify_password, hash_password
from services.log import logger

security = HTTPBearer(auto_error=False)

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    request: Request = None,
):
    token_value: str | None = None
    # 1) Prefer Authorization header (HTTPBearer)
    if credentials and credentials.credentials:
        token_value = credentials.credentials
    # 2) Fallback to HttpOnly cookie named 'access_token' (value may be 'Bearer <token>')
    if not token_value and request is not None:
        cookie_val = request.cookies.get("access_token")
        if cookie_val:
            parts = cookie_val.split()
            token_value = parts[1] if len(parts) == 2 and parts[0].lower() == "bearer" else cookie_val
    if not token_value:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing credentials")
    payload = verify_token(token_value)
    if isinstance(payload, dict):
        return payload
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

def require_roles(*roles):
    def role_dependency(
        credentials: HTTPAuthorizationCredentials = Depends(security),
        request: Request = None,
    ):
        # Reuse token extraction logic
        token_value: str | None = None
        if credentials and credentials.credentials:
            token_value = credentials.credentials
        if not token_value and request is not None:
            cookie_val = request.cookies.get("access_token")
            if cookie_val:
                parts = cookie_val.split()
                token_value = parts[1] if len(parts) == 2 and parts[0].lower() == "bearer" else cookie_val
        if not token_value:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing credentials")
        payload = verify_token(token_value)
        if not isinstance(payload, dict):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")
        if "role" not in payload:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token format")
        if payload["role"] not in roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
        return payload
    return role_dependency

def login(employee_id: str, password: str):
    db = get_db()
    employees = db["employees"]
    # convert employee_id to int if present as string
    try:
        emp_id = int(employee_id)
    except ValueError:
        emp_id = employee_id
    user = employees.find_one({"employee_id": emp_id})
    if not user or not user.get("password_hash") or not verify_password(password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid employee ID or password")
    payload = {"user_id": str(user["_id"]), "role": user["role"]}
    token = create_access_token(payload, subject=str(user["_id"]))
    return {
        "user_id": str(user["_id"]),
        "role": user["role"],
        "token": token
    }

def register(employee_id: str, password: str, role: str):
    db = get_db()
    employees = db["employees"]
    # convert employee_id to int if present as string
    try:
        emp_id = int(employee_id)
    except ValueError:
        emp_id = employee_id
    if employees.find_one({"employee_id": emp_id}):
        raise HTTPException(status_code=400, detail="Employee ID already exists")
    hashed = hash_password(password)
    from datetime import datetime
    from bson import ObjectId
    employees.insert_one({
        "_id": ObjectId(),
        "employee_id": emp_id,
        "full_name": f"User {emp_id}",  # Default name
        "password_hash": hashed,
        "role": role,
        "status": "active",
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    })
    return {"message": "User registered successfully"}
