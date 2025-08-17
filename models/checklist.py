from pydantic import BaseModel,Field
from datetime import datetime,date
from typing import Optional
from typing import Literal
from bson import ObjectId
from enum import Enum


class Checklist_creat(BaseModel):
    checklist_id=ObjectId
    title: str["max len 100 char"]
    task_id=ObjectId
    description=str
    is_completed=bool
    assigned_to:ObjectId
    due_date:date
    priorty:str=Enum["lower","medium","hight"]
    created_by: ObjectId
    created_at: datetime
    updated_at: datetime

class Checklist_update(BaseModel):
    checklist_id=ObjectId
    title: Optional[str["max len 100 char"]]
    task_id=ObjectId
    description=Optional[str]
    is_completed=bool
    assigned_to:ObjectId
    due_date:Optional[date]
    priorty:Optional[str]=Enum["lower","medium","hight"]
    created_by: ObjectId
    created_at: datetime
    updated_at: datetime


class Checklist_creat(BaseModel):
    checklist_id=ObjectId
    title: str["max len 100 char"]
    task_id=ObjectId
    description=str
    is_completed=bool
    assigned_to:ObjectId
    due_date:date
    priorty:str=Enum["lower","medium","hight"]
    created_by: ObjectId
    created_at: datetime
    updated_at: datetime