from dataclasses import field
from pydantic import BaseModel,Field
from pydantic import ConfigDict
from datetime import datetime
from bson import ObjectId


class logCreate(BaseModel):
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )

    action_type:str=Field(...,max_length=100,description="creat_report")
    user_id:str =Field(...,description="user_id")
    description:str = Field(...,max_length=500,description="activity description")


class logOut(BaseModel):
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )

    id:str=Field(...,alias="_id",description="log_id")
    action_type:str
    user_id:str
    description:str
    created_at:datetime


class config:
    arbitrary_types=True
    json_encoders={ObjectId:str}
    

    
