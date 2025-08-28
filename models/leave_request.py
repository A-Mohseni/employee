from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime, date
from typing import Optional, Literal
from bson import ObjectId


class PyObjectId(ObjectId):
    @classmethod
    def __get_pydantic_json_schema__(cls, field_schema, field):
        field_schema.update(type="string", format="objectid")
        return field_schema


LeaveStatus = Literal["pending_phase1", "pending_phase2", "approved", "rejected"]


class LeaveRequestCreate(BaseModel):
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )
    created_by: str = Field(..., description="employee id (ObjectId string)")
    request_date: date = Field(default_factory=lambda: date.today())
    start_date: date
    end_date: date
    reason: str = Field(..., max_length=300)


class LeaveRequestUpdate(BaseModel):
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    reason: Optional[str] = Field(None, max_length=300)


class LeaveRequestOut(BaseModel):
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )
    request_id: str = Field(default_factory=lambda: str(ObjectId()))
    created_by: str
    request_date: date
    start_date: date
    end_date: date
    reason: str
    approval_phase1_by: Optional[str] = None  # admin2 id
    approval_phase1_at: Optional[datetime] = None
    approval_phase2_by: Optional[str] = None  # manager_women id
    approval_phase2_at: Optional[datetime] = None
    status: LeaveStatus
    created_at: datetime
    updated_at: Optional[datetime] = None