from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from typing import Optional, Literal, List
from bson import ObjectId


class PyObjectId(ObjectId):
    @classmethod
    def __get_pydantic_json_schema__(cls, field_schema, field):
        field_schema.update(type="string", format="objectid")
        return field_schema


class user_create(BaseModel):
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )
    
    phone_number: str
    first_name: str
    last_name: str
    role: Literal["employee", "manager", "supervisor"]
    password_hash: str


class user_update(BaseModel):
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )
    
    phone_number: Optional[str] = None  
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    tokens: Optional[List[str]] = None
    role: Optional[Literal["employee", "manager", "supervisor"]] = None
    password_hash: Optional[str] = None


class user_out(BaseModel):
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )
    
    user_id: str = Field(default_factory=lambda: str(ObjectId()))
    phone_number: str  
    first_name: str
    last_name: str
    tokens: Optional[List[str]] = None
    role: Optional[Literal["employee", "manager", "supervisor"]] = None
    created_at: datetime
    updated_at: datetime