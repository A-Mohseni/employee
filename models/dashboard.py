from bson import ObjectId, objectid
from pydantic import BaseModel
from typing import Optional

from pydantic_core.core_schema import none_schema


class DashboardStats(BaseModel):
    total_reports:int
    reports_by_status:dict
    total_leave_request:int
    leave_request_by_status:dict
    user_id : Optional[str]=None

class config:
    json_encoders={ObjectId:str}

    