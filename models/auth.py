from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class LoginRequest(BaseModel):
    employee_id: str
    password: str

class AdminBootstrapRequest(BaseModel):
    employee_id: str
    password: str
    full_name: str
    phone: str
    email: str

class AdminCreate(BaseModel):
    employee_id: str
    full_name: str
    password: str
    phone: str
    email: str
    role: str = "admin1"
    is_super_admin: bool = False

class AdminOut(BaseModel):
    id: str
    employee_id: str | int
    full_name: str
    role: str
    status: str
    phone: str
    email: str
    is_super_admin: bool
    created_at: datetime
    updated_at: datetime
