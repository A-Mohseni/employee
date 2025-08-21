from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional, Literal
from bson import ObjectId


class PurchaseItemCreate(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    name: str = Field(..., max_length=100)
    quantity: int = Field(..., gt=0)
    priority: Literal["low", "medium", "high"] = "low"
    status: Literal["pending", "purchased", "canceled"] = "pending"
    notes: Optional[str] = None
    category: Literal["office_supplies", "equipment", "other"] = "other"
    description: Optional[str] = None
    created_by: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class PurchaseItemUpdate(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    name: Optional[str] = Field(None, max_length=100)
    quantity: Optional[int] = Field(None, gt=0)
    priority: Optional[Literal["low", "medium", "high"]] = None
    status: Optional[Literal["pending", "purchased", "canceled"]] = None
    notes: Optional[str] = None
    category: Optional[Literal["office_supplies", "equipment", "other"]] = None
    description: Optional[str] = None
    updated_at: datetime = Field(default_factory=datetime.now)


class PurchaseItemOut(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
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
