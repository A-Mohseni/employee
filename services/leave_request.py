from dataclasses import field
from datetime import datetime
from gc import collect
from multiprocessing import Value
from bson import ObjectId, objectid
from fastapi import HTTPException, status
from pymongo.synchronous import collection
from models.leave_request import leave_request_creat,leave_request_update,leave_request_out
from utils.db import get_db
from typing import Optional, Lis


def creat_leaveRequest(data:leave_request_creat,current_user:dict)->leave_request_out:
    if current_user["role"]!="manager":
        raise HTTPException(
               status_code=status.HTTP_403_FORBIDDEN,
               detail="no acces" 
        )
    db=get_db()
    collection=db["leaveRequest"]

    leaveRequest_data={
        "start_date":data.start_date, 
        "end_date": data.end_date,
        "reason": data.reason,
        "status": data.status
   }
    collection.insert_one(leaveRequest_data)
    return leave_request_out(**leaveRequest_data)


def get_leaveRequest(request_id:ObjectId,
    limit:int=20,
    offset:int=0,
    current_user:dict=None
    )->list[leave_request_out]:

    db=get_db()
    collection=db["leaveRequest"]


    filter_query={}
    if request_id:
        filter_query["request_id"]=ObjectId(request_id)
    if current_user["role"]== "eployee":
        filter_query["request_id"]=ObjectId(current_user[request_id])
       
       
    cursor=collection.find(filter_query).limit(limit).skip(offset)
    return [leave_request_out(**item) for item in cursor ]



def update_leaveRequest(request_id:str,update_data:leave_request_update,current_user:dict)->leave_request_out:
    db=get_db()
    collection=db["leaveRequest"]

    LR=collection.find_one({"_id":ObjectId(request_id)})

    if not LR:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="NotFound"
        )
    if str(LR[request_id])== current_user["user_id"] and current_user["role"]!="employee":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=" no acces"
        )

    update_fields={k:v for k,v in update_data.dict(exclude_unset=True).items()}
    update_fields[field]=Value