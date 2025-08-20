from pydantic import BaseModel, Field
from datetime import datetime, date
from typing import Optional, Literal
from bson import ObjectId


class LeaveRequestCreate(BaseModel):
    user_id: ObjectId
    start_date: date
    end_date: date
    reason: str = Field(..., max_length=300)
    status: Literal["pending", "approved", "rejected"] = "pending"
    created_at: datetime = Field(default_factory=datetime.now)


class LeaveRequestUpdate(BaseModel):
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    reason: Optional[str] = Field(None, max_length=300)
    status: Optional[Literal["pending", "approved", "rejected"]] = None
    approved_by: Optional[ObjectId] = None
    updated_at: datetime = Field(default_factory=datetime.now)


class LeaveRequestOut(BaseModel):
    request_id: ObjectId
    user_id: ObjectId
    start_date: date
    end_date: date
    reason: str
    status: Literal["pending", "approved", "rejected"]
    approved_by: Optional[ObjectId] = None
    created_at: datetime
    updated_at: Optional[datetime] = None