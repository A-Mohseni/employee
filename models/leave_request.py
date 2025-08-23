from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime, date
from typing import Optional, Literal, Any
from bson import ObjectId


class PyObjectId(ObjectId):
    @classmethod
    def __get_pydantic_json_schema__(cls, field_schema, field):
        field_schema.update(type="string", format="objectid")
        return field_schema


class LeaveRequestCreate(BaseModel):
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )
    user_id: PyObjectId = Field(default_factory=PyObjectId)
    start_date: date
    end_date: date
    reason: str = Field(..., max_length=300)
    status: Literal["pending", "approved", "rejected"] = "pending"
    created_at: datetime = Field(default_factory=datetime.now)


class LeaveRequestUpdate(BaseModel):
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    reason: Optional[str] = Field(None, max_length=300)
    status: Optional[Literal["pending", "approved", "rejected"]] = None
    approved_by: Optional[PyObjectId] = None
    updated_at: datetime = Field(default_factory=datetime.now)


class LeaveRequestOut(BaseModel):
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )
    request_id: PyObjectId = Field(default_factory=PyObjectId)
    user_id: PyObjectId = Field(default_factory=PyObjectId)
    start_date: date
    end_date: date
    reason: str
    status: Literal["pending", "approved", "rejected"]
    approved_by: Optional[PyObjectId] = None
    created_at: datetime
    updated_at: Optional[datetime] = None