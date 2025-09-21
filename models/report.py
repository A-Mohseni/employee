from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from typing import Optional, Literal
from bson import ObjectId


class PyObjectId(ObjectId):
    @classmethod
    def __get_pydantic_json_schema__(cls, field_schema, field):
        field_schema.update(type="string", format="objectid")
        return field_schema


ReportStatus = Literal["pending", "approved", "rejected"]


class report_create(BaseModel):
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )
    content: str = Field(..., min_length=3, max_length=2000)


class report_update(BaseModel):
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )
    content: Optional[str] = Field(None, min_length=3, max_length=2000)


class report_out(BaseModel):
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )
    id: str = Field(alias="_id")
    created_by: str
    content: str
    approved_by: Optional[str] = None
    status: ReportStatus
    created_at: datetime
    updated_at: Optional[datetime] = None
    