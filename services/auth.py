from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from utils.db import get_db
from utils.jwt import create_access_token, verify_token, TokenError
from utils.password_hash import verify_password, hash_password
from services.log import logger

security = HTTPBearer(auto_error=False)

def _normalize_token(raw_token: str | None) -> str | None:
    if not raw_token:
        return raw_token
    
    # Handle None or empty string
    if not isinstance(raw_token, str):
        return None
    
    token = raw_token.strip()
    
    # Handle empty token after strip
    if not token:
        return None
    
    # Remove surrounding quotes if present (single or double)
    while len(token) >= 2 and token[0] in ('"', "'") and token[-1] == token[0]:
        token = token[1:-1].strip()
    
    # Handle multiple Bearer prefixes
    while token.lower().startswith("bearer "):
        parts = token.split(None, 1)
        if len(parts) > 1:
            token = parts[1].strip()
        else:
            break
    
    # Remove quotes again in case they were around the inner token
    while len(token) >= 2 and token[0] in ('"', "'") and token[-1] == token[0]:
        token = token[1:-1].strip()
    
    # Final validation - token should not be empty and should look like a JWT
    if not token or len(token.split('.')) != 3:
        return None
    
    return token

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    request: Request = None,
):
    token_value: str | None = None
    if credentials and credentials.credentials:
        token_value = _normalize_token(credentials.credentials)
    if not token_value and request is not None:
        cookie_val = request.cookies.get("access_token")
        if cookie_val:
            parts = cookie_val.split()
            token_candidate = parts[1] if len(parts) == 2 and parts[0].lower() == "bearer" else cookie_val
            token_value = _normalize_token(token_candidate)
    if not token_value:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing credentials")
    payload = verify_token(token_value)
    if isinstance(payload, dict):
        return payload
    # Map specific token errors to clearer messages
    error_detail = "Invalid token"
    if isinstance(payload, TokenError):
        if payload == TokenError.EXPIRED:
            error_detail = "Token expired"
        elif payload == TokenError.INVALID_SIGNATURE:
            error_detail = "Invalid token signature"
        elif payload == TokenError.INVALID_ALGORITHM:
            error_detail = "Invalid token algorithm"
        elif payload == TokenError.INVALID_FORMAT:
            error_detail = "Invalid token format"
        elif payload == TokenError.INVALID_PAYLOAD:
            error_detail = "Invalid token payload"
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=error_detail)

def require_roles(*roles):
    def role_dependency(
        credentials: HTTPAuthorizationCredentials = Depends(security),
        request: Request = None,
    ):
        token_value: str | None = None
        if credentials and credentials.credentials:
            token_value = _normalize_token(credentials.credentials)
        if not token_value and request is not None:
            cookie_val = request.cookies.get("access_token")
            if cookie_val:
                parts = cookie_val.split()
                token_candidate = parts[1] if len(parts) == 2 and parts[0].lower() == "bearer" else cookie_val
                token_value = _normalize_token(token_candidate)
        if not token_value:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing credentials")
        payload = verify_token(token_value)
        if not isinstance(payload, dict):
            error_detail = "Invalid or expired token"
            if isinstance(payload, TokenError):
                if payload == TokenError.EXPIRED:
                    error_detail = "Token expired"
                elif payload == TokenError.INVALID_SIGNATURE:
                    error_detail = "Invalid token signature"
                elif payload == TokenError.INVALID_ALGORITHM:
                    error_detail = "Invalid token algorithm"
                elif payload == TokenError.INVALID_FORMAT:
                    error_detail = "Invalid token format"
                elif payload == TokenError.INVALID_PAYLOAD:
                    error_detail = "Invalid token payload"
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=error_detail)
        if "role" not in payload:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token format")
        if payload["role"] not in roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
        return payload
    return role_dependency

def login(employee_id: str, password: str):
    db = get_db()
    employees = db["employees"]
    try:
        emp_id = int(employee_id)
    except ValueError:
        emp_id = employee_id
    user = employees.find_one({"employee_id": emp_id})
    if not user or not user.get("password_hash") or not verify_password(password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid employee ID or password")
    
    # Deactivate all existing tokens for this user
    try:
        from services.token import deactivate_user_tokens
        deactivate_user_tokens(str(user["_id"]))
    except Exception as e:
        print(f"Warning: Could not deactivate old tokens: {e}")
    
    payload = {"user_id": str(user["_id"]), "role": user["role"]}
    token = create_access_token(payload, subject=str(user["_id"]))
    return {
        "user_id": str(user["_id"]),
        "role": user["role"],
        "token": token
    }

def register(employee_id: str, password: str, role: str, phone: str, birthdate: str):
    db = get_db()
    employees = db["employees"]
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
        "full_name": f"User {emp_id}",
        "password_hash": hashed,
        "role": role,
        "status": "active",
        "phone": phone,
        "birthdate": birthdate,
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    })
    return {"message": "User registered successfully"}
