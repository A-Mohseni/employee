from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from utils.db import get_db
from utils.jwt import create_access_token, verify_token
from utils.password_hash import verify_password, hash_password
from services.log import service_exception, logger

security = HTTPBearer()

@service_exception
def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if not credentials or not credentials.credentials:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing credentials")
    payload = verify_token(credentials.credentials)
    if isinstance(payload, dict):
        return payload
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

def require_roles(*roles):
    def role_dependency(credentials: HTTPAuthorizationCredentials = Depends(security)):
        payload = verify_token(credentials.credentials)
        if not isinstance(payload, dict) or "role" not in payload or payload["role"] not in roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
        return payload
    return role_dependency  # فقط تابع را برگردانید، نه Depends(role_dependency)

@service_exception
def login(employee_id: str, password: str):
    db = get_db()
    employees = db["employees"]
    # convert employee_id to int if present as string
    try:
        emp_id = int(employee_id)
    except ValueError:
        emp_id = employee_id
    user = employees.find_one({"employee_id": emp_id})
    if not user or not verify_password(password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid employee ID or password")
    payload = {"user_id": str(emp_id), "role": user["role"]}
    token = create_access_token(payload, subject=str(emp_id))
    return {
        "user_id": str(emp_id),
        "role": user["role"],
        "token": token
    }

@service_exception
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
    employees.insert_one({
        "employee_id": emp_id,
        "password_hash": hashed,
        "role": role
    })
    return {"message": "User registered successfully"}
