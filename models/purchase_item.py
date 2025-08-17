from pydantic import BaseModel,Field
from datetime import datetime,date
from typing import Optional
from typing import Literal
from bson import ObjectId

class PurchaseItem_creat(BaseModel):
    item_id: ObjectId
    name: str
    quantity: int
    priority: str ["low", "medium", "high"]
    status: str
    created_by: ObjectId 
    created_at: datetime
    updated_at: datetime
    notes: str
    category: str
    description : str



class PurchaseItem_update(BaseModel):
    item_id: ObjectId
    name:Optional[str]=None
    quantity: Optional[int]=None
    priority: Optional[str]=Literal["low", "medium", "high"]
    status:Optional[str]=None
    created_by: ObjectId 
    created_at: Optional[datetime]=None
    updated_at: Optional[datetime]=None
    notes:Optional[str] =None
    category: Optional[str["office_supplies","equipment","other"]]=None
    description :Optional[str] =None



class PurchaseItem_out(BaseModel):
    item_id: ObjectId
    name: str
    quantity: int
    priority: str ["low", "medium", "high"]
    status: str=Field["pending", "purchased", "canceled"]
    created_by: ObjectId 
    created_at: datetime
    updated_at: datetime
    notes: str
    category: str=Field["office_supplies", "equipment", "other"]
    description : str
