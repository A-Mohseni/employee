from pydantic import BaseModel, ConfigDict, Field, field_validator
from datetime import datetime
from typing import Optional, Literal
from bson import ObjectId


class PyObjectId(ObjectId):
    @classmethod
    def __get_pydantic_json_schema__(cls, field_schema, field):
        field_schema.update(type="string", format="objectid")
        return field_schema


EmployeeRole = Literal["admin1", "admin2", "manager_women", "manager_men", "employee"]
EmployeeStatus = Literal["active", "inactive"]


class TokenCreate(BaseModel):
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )

    user_id: str
    token_hash: str
    expires_at: datetime
    is_active: bool = True


class TokenOut(BaseModel):
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )

    id: str
    user_id: str
    token_hash: str
    expires_at: datetime
    is_active: bool
    created_at: datetime


class employee_create(BaseModel):
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )

    employee_id: int = Field(..., ge=10, le=999, description="Unique 2–3 digit employee id")
    full_name: str = Field(..., min_length=3, max_length=100)
    role: EmployeeRole
    status: EmployeeStatus = "active"
    password_hash: Optional[str] = None

    @field_validator("employee_id")
    @classmethod
    def validate_employee_id(cls, v: int) -> int:
        if not (10 <= v <= 999):
            raise ValueError("employee_id must be a 2–3 digit integer (10-999)")
        return v


class employee_update(BaseModel):
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )

    full_name: Optional[str] = Field(None, min_length=3, max_length=100)
    role: Optional[EmployeeRole] = None
    status: Optional[EmployeeStatus] = None
    password_hash: Optional[str] = None


class employee_out(BaseModel):
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )

    id: str
    employee_id: int
    full_name: str
    role: EmployeeRole
    status: EmployeeStatus
    created_at: datetime
    updated_at: datetime


class employee_out_with_token(BaseModel):
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )

    id: str
    employee_id: int
    full_name: str
    role: EmployeeRole
    status: EmployeeStatus
    created_at: datetime
    updated_at: datetime
    access_token: str
    token_type: str = "bearer"