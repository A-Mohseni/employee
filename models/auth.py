from pydantic import BaseModel

class RegisterRequest(BaseModel):
    employee_id: str
    password: str
    role: str
    phone: str
    birthdate: str

class LoginRequest(BaseModel):
    employee_id: str
    password: str