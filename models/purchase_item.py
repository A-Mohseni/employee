from pydantic import BaseModel, Field, ConfigDict, validator
from datetime import datetime
from typing import Optional, Literal, List
from bson import ObjectId
from enum import Enum


class PyObjectId(ObjectId):
    @classmethod
    def __get_pydantic_json_schema__(cls, field_schema, field):
        field_schema.update(type="string", format="objectid")
        return field_schema


class PriorityLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class PurchaseStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    PURCHASED = "purchased"
    DELIVERED = "delivered"
    CANCELED = "canceled"
    REJECTED = "rejected"


class PurchaseCategory(str, Enum):
    OFFICE_SUPPLIES = "office_supplies"
    EQUIPMENT = "equipment"
    TECHNOLOGY = "technology"
    FURNITURE = "furniture"
    MAINTENANCE = "maintenance"
    OTHER = "other"


class PurchaseItemCreate(BaseModel):
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str},
        use_enum_values=True
    )
    
    name: str = Field(..., min_length=1, max_length=200, description="Item name")
    description: Optional[str] = Field(None, max_length=1000, description="Item description")
    quantity: int = Field(..., gt=0, le=10000, description="Required quantity")
    unit_price: Optional[float] = Field(None, ge=0, description="Unit price")
    
    category: PurchaseCategory = Field(default=PurchaseCategory.OTHER, description="Category")
    priority: PriorityLevel = Field(default=PriorityLevel.LOW, description="Priority")
    status: PurchaseStatus = Field(default=PurchaseStatus.PENDING, description="Status")
    
    notes: Optional[str] = Field(None, max_length=500, description="Notes")
    supplier: Optional[str] = Field(None, max_length=100, description="Supplier")
    budget_code: Optional[str] = Field(None, max_length=50, description="Budget code")
    
    required_date: Optional[datetime] = Field(None, description="Required date")
    created_by: Optional[str] = Field(None, description="Created by")
    created_at: datetime = Field(default_factory=datetime.now, description="Created at")
    updated_at: datetime = Field(default_factory=datetime.now, description="Updated at")
    
    @validator('name')
    def validate_name(cls, v):
        if not v.strip():
            raise ValueError('Item name cannot be empty')
        return v.strip()
    
    @validator('description')
    def validate_description(cls, v):
        if v is not None:
            return v.strip() if v.strip() else None
        return v


class PurchaseItemUpdate(BaseModel):
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str},
        use_enum_values=True
    )
    
    name: Optional[str] = Field(None, min_length=1, max_length=200, description="Item name")
    description: Optional[str] = Field(None, max_length=1000, description="Item description")
    quantity: Optional[int] = Field(None, gt=0, le=10000, description="Required quantity")
    unit_price: Optional[float] = Field(None, ge=0, description="Unit price")
    
    category: Optional[PurchaseCategory] = Field(None, description="Category")
    priority: Optional[PriorityLevel] = Field(None, description="Priority")
    status: Optional[PurchaseStatus] = Field(None, description="Status")
    
    notes: Optional[str] = Field(None, max_length=500, description="Notes")
    supplier: Optional[str] = Field(None, max_length=100, description="Supplier")
    budget_code: Optional[str] = Field(None, max_length=50, description="Budget code")
    
    required_date: Optional[datetime] = Field(None, description="Required date")
    updated_at: datetime = Field(default_factory=datetime.now, description="Updated at")
    
    @validator('name')
    def validate_name(cls, v):
        if v is not None and not v.strip():
            raise ValueError('Item name cannot be empty')
        return v.strip() if v else v
    
    @validator('description')
    def validate_description(cls, v):
        if v is not None:
            return v.strip() if v.strip() else None
        return v


class PurchaseItemOut(BaseModel):
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str},
        use_enum_values=True
    )
    
    item_id: str = Field(..., description="Item ID")
    
    name: str = Field(..., description="Item name")
    description: Optional[str] = Field(None, description="Item description")
    quantity: int = Field(..., description="Required quantity")
    unit_price: Optional[float] = Field(None, description="Unit price")
    total_price: Optional[float] = Field(None, description="Total price")
    
    category: PurchaseCategory = Field(..., description="Category")
    priority: PriorityLevel = Field(..., description="Priority")
    status: PurchaseStatus = Field(..., description="Status")
    
    notes: Optional[str] = Field(None, description="Notes")
    supplier: Optional[str] = Field(None, description="Supplier")
    budget_code: Optional[str] = Field(None, description="Budget code")
    
    required_date: Optional[datetime] = Field(None, description="Required date")
    created_by: str = Field(..., description="Created by")
    created_at: datetime = Field(..., description="Created at")
    updated_at: datetime = Field(..., description="Updated at")
    
    @validator('total_price', pre=True, always=True)
    def calculate_total_price(cls, v, values):
        if 'quantity' in values and 'unit_price' in values:
            quantity = values.get('quantity')
            unit_price = values.get('unit_price')
            if quantity and unit_price:
                return quantity * unit_price
        return v


class PurchaseItemFilter(BaseModel):
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str},
        use_enum_values=True
    )
    
    name: Optional[str] = Field(None, description="Search in name")
    category: Optional[PurchaseCategory] = Field(None, description="Filter by category")
    priority: Optional[PriorityLevel] = Field(None, description="Filter by priority")
    status: Optional[PurchaseStatus] = Field(None, description="Filter by status")
    
    supplier: Optional[str] = Field(None, description="Filter by supplier")
    budget_code: Optional[str] = Field(None, description="Filter by budget code")
    created_by: Optional[str] = Field(None, description="Filter by creator")
    
    created_from: Optional[datetime] = Field(None, description="Created from date")
    created_to: Optional[datetime] = Field(None, description="Created to date")
    required_from: Optional[datetime] = Field(None, description="Required from date")
    required_to: Optional[datetime] = Field(None, description="Required to date")
    
    min_price: Optional[float] = Field(None, ge=0, description="Minimum price")
    max_price: Optional[float] = Field(None, ge=0, description="Maximum price")


class PurchaseItemSummary(BaseModel):
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str},
        use_enum_values=True
    )
    
    total_items: int = Field(..., description="Total items")
    pending_items: int = Field(..., description="Pending items")
    approved_items: int = Field(..., description="Approved items")
    purchased_items: int = Field(..., description="Purchased items")
    total_budget: float = Field(..., description="Total budget")
    category_breakdown: dict = Field(..., description="Category breakdown")
    priority_breakdown: dict = Field(..., description="Priority breakdown")
