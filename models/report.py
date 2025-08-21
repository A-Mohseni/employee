from pydantic import BaseModel, ConfigDict
from datetime import datetime,date
from typing import Optional
from typing import Literal
from bson import ObjectId
class report_creat(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    report_id: str
    user_id: str
    date: date
    description: str
    hours_worked: int
    status:str
    approved_by: str
    created_at: datetime

class report_update(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    report_id: Optional[str]=None
    user_id: Optional[str] = None
    date: date
    description: Optional[str]=None
    hours_worked:Optional [int]=None
    status:Optional[str]=None
    approved_by: Optional[str]=None
    created_at: datetime



class report_out(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    report_id: str
    user_id: str
    date: date
    description: str
    hours_worked: int
    status:str
    approved_by: str
    created_at: datetime