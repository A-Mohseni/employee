from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime, date
from typing import Optional, Literal
from bson import ObjectId


class PyObjectId(ObjectId):
    @classmethod
    def __get_pydantic_json_schema__(cls, field_schema, field):
        field_schema.update(type="string", format="objectid")
        return field_schema


class report_creat(BaseModel):
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )
    report_id: str = Field(default_factory=lambda: str(ObjectId()))
    user_id: str = Field(default_factory=lambda: str(ObjectId()))
    date: date
    description: str
    hours_worked: int
    status: str
    approved_by: str = Field(default_factory=lambda: str(ObjectId()))
    created_at: datetime


class report_update(BaseModel):
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )
    report_id: Optional[str] = None
    user_id: Optional[str] = None
    date: Optional[date] = None
    description: Optional[str] = None
    hours_worked: Optional[int] = None
    status: Optional[str] = None
    approved_by: Optional[str] = None
    created_at: Optional[datetime] = None


class report_out(BaseModel):
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )
    report_id: str = Field(default_factory=lambda: str(ObjectId()))
    user_id: str = Field(default_factory=lambda: str(ObjectId()))
    date: date
    description: str
    hours_worked: int
    status: str
    approved_by: str = Field(default_factory=lambda: str(ObjectId()))
    created_at: datetime