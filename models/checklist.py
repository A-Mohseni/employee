from pydantic import BaseModel, Field
from datetime import datetime, date
from typing import Optional
from typing import Literal
from bson import ObjectId
from enum import Enum


class PriorityEnum(str, Enum):
    lower = "lower"
    medium = "medium"
    high = "high"


class ChecklistCreate(BaseModel):
    title: str = Field(..., max_length=100)
    task_id: ObjectId
    description: str
    is_completed: bool = False
    assigned_to: ObjectId
    due_date: date
    priority: PriorityEnum = PriorityEnum.medium
    created_by: ObjectId
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class ChecklistUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=100)
    task_id: Optional[ObjectId] = None
    description: Optional[str] = None
    is_completed: Optional[bool] = None
    assigned_to: Optional[ObjectId] = None
    due_date: Optional[date] = None
    priority: Optional[PriorityEnum] = None
    updated_at: datetime = Field(default_factory=datetime.now)


class ChecklistOut(BaseModel):
    checklist_id: ObjectId
    title: str
    task_id: ObjectId
    description: str
    is_completed: bool
    assigned_to: ObjectId
    due_date: date
    priority: PriorityEnum
    created_by: ObjectId
    created_at: datetime
    updated_at: datetime