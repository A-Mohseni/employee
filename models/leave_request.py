from pydantic import BaseModel, Field
from datetime import datetime, date
from typing import Optional, Literal


class leave_request_creat(BaseModel):
    start_date: date
    end_date: date
    reason: str = Field(..., max_length=300)
    status: Literal["pending", "approved", "rejected"] = "pending"


class leave_request_update(BaseModel):
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    reason: Optional[str] = Field(None, max_length=300)
    status: Optional[Literal["pending", "approved", "rejected"]] = None
    approved_by: Optional[str] = None


class leave_request_out(BaseModel):
    request_id: str
    user_id: str
    start_date: date
    end_date: date
    reason: str
    status: Literal["pending", "approved", "rejected"]
    approved_by: Optional[str] = None
    created_at: datetime