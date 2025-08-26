from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime, date
from typing import Optional, Literal
from bson import ObjectId
from enum import Enum


class PyObjectId(ObjectId):
    @classmethod
    def __get_pydantic_json_schema__(cls, field_schema, field):
        field_schema.update(type="string", format="objectid")
        return field_schema


class PriorityEnum(str, Enum):
    lower = "lower"
    medium = "medium"
    high = "high"


class ChecklistCreate(BaseModel):
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )
    title: str = Field(..., max_length=100)
    task_id: str = Field(default_factory=lambda: str(ObjectId()))
    description: str
    is_completed: bool = False
    assigned_to: str = Field(default_factory=lambda: str(ObjectId()))
    due_date: date
    priority: PriorityEnum = PriorityEnum.medium
    created_by: str = Field(default_factory=lambda: str(ObjectId()))
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class ChecklistUpdate(BaseModel):
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )
    title: Optional[str] = Field(None, max_length=100)
    task_id: Optional[str] = None
    description: Optional[str] = None
    is_completed: Optional[bool] = None
    assigned_to: Optional[str] = None
    due_date: Optional[date] = None
    priority: Optional[PriorityEnum] = None
    updated_at: datetime = Field(default_factory=datetime.now)


class ChecklistOut(BaseModel):
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )
    checklist_id: str = Field(default_factory=lambda: str(ObjectId()))
    title: str
    task_id: str = Field(default_factory=lambda: str(ObjectId()))
    description: str
    is_completed: bool
    assigned_to: str = Field(default_factory=lambda: str(ObjectId()))
    due_date: date
    priority: PriorityEnum
    created_by: str = Field(default_factory=lambda: str(ObjectId()))
    created_at: datetime
    updated_at: datetime