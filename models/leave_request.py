from pydantic import BaseModel,Field
from datetime import datetime,date
from typing import Optional
from typing import Literal
from bson import ObjectId

class leave_request_creat(BaseModel):
    request_id: ObjectId
    user_id: ObjectId 
    start_date: date
    end_date: date
    reason: str
    status=str
    approved_by: ObjectId 
    created_at: datetime

class leave_request_update(BaseModel):
    request_id: ObjectId
    user_id: ObjectId 
    start_date: Optional[date]=None
    end_date: Optional[date]=None
    reason: Optional[str]=None
    status=Optional[str]=None
    approved_by: ObjectId 
    created_at: datetime


class leave_request_out(BaseModel):
    request_id: ObjectId
    user_id: ObjectId 
    start_date: date
    end_date: date
    reason: str = Field("max lenght 300 char")
    status=Literal["pending", "approved", "rejected"]
    approved_by:Optional [ObjectId] =None
    created_at: datetime