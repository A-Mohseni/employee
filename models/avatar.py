from pydantic import BaseModel, Field, ConfigDict
from bson import ObjectId


class avatarCreat(BaseModel):
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )

    user_id: str = Field(..., description="user_id")


class avatarOut(BaseModel):
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )

    id: str = Field(..., description="avatar_id")
    user_id: str
    avatar_url: str = Field(..., description="avatar url address")
