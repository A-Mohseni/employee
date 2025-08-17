from asyncio import create_task
from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional
from typing import Literal
from bson import ObjectId

class user_create(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    phone_number: str
    first_name: str
    last_name: str
    role: Literal["employee", "manager", "supervisor"]
    password_hash: str

class user_update(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    phone_number: Optional[str] = None  
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    tokens: Optional[list[str]] = None
    role: Optional[Literal["employee", "manager", "supervisor"]] = None
    password_hash: Optional[str] = None

class user_out(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    user_id: str
    phone_number: str  
    first_name: str
    last_name: str
    tokens: Optional[list[str]] = None  # توکن را optional کردم
    role: Optional[Literal["employee", "manager", "supervisor"]] 
    created_at: datetime
    updated_at: datetime