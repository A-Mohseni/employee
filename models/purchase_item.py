from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Literal


class PurchaseItem_creat(BaseModel):
    name: str
    quantity: int
    priority: Literal["low", "medium", "high"] = "low"
    status: Literal["pending", "purchased", "canceled"] = "pending"
    notes: Optional[str] = None
    category: Literal["office_supplies", "equipment", "other"] = "other"
    description: Optional[str] = None


class PurchaseItem_update(BaseModel):
    name: Optional[str] = None
    quantity: Optional[int] = None
    priority: Optional[Literal["low", "medium", "high"]] = None
    status: Optional[Literal["pending", "purchased", "canceled"]] = None
    notes: Optional[str] = None
    category: Optional[Literal["office_supplies", "equipment", "other"]] = None
    description: Optional[str] = None


class PurchaseItem_out(BaseModel):
    item_id: str
    name: str
    quantity: int
    priority: Literal["low", "medium", "high"]
    status: Literal["pending", "purchased", "canceled"]
    created_by: str
    created_at: datetime
    updated_at: datetime
    notes: Optional[str] = None
    category: Literal["office_supplies", "equipment", "other"]
    description: Optional[str] = None
