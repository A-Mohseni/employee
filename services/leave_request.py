import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime
from typing import List, Optional

from bson import ObjectId
from fastapi import HTTPException, status

from models.leave_request import (
    LeaveRequestCreate,
    LeaveRequestOut,
    LeaveRequestUpdate,
    PyObjectId
)
from utils.db import get_db


def create_leave_request(
    data: LeaveRequestCreate, current_user: dict
) -> LeaveRequestOut:
    if current_user["role"] != "manager":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="not access",
        )

    db = get_db()
    if db is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database connection failed"
        )
    
    leave_collection = db["leaveRequest"]

    doc = {
        "user_id": data.user_id,
        "start_date": data.start_date,
        "end_date": data.end_date,
        "reason": data.reason,
        "status": data.status,
        "created_at": datetime.now(),
    }
    result = leave_collection.insert_one(doc)

    return LeaveRequestOut(
        request_id=result.inserted_id,
        user_id=doc["user_id"],
        start_date=doc["start_date"],
        end_date=doc["end_date"],
        reason=doc["reason"],
        status=doc["status"],
        approved_by=None,
        created_at=doc["created_at"],
        updated_at=None,
    )


def get_leave_requests(
    request_id: Optional[str] = None,
    user_id: Optional[str] = None,
    limit: int = 20,
    offset: int = 0,
    current_user: Optional[dict] = None,
) -> List[LeaveRequestOut]:
    db = get_db()
    if db is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database connection failed"
        )
    
    leave_collection = db["leaveRequest"]

    filter_query: dict = {}
    if request_id:
        filter_query["_id"] = ObjectId(request_id)
    if user_id:
        filter_query["user_id"] = ObjectId(user_id)
    if current_user and current_user.get("role") == "employee":
        filter_query["user_id"] = ObjectId(current_user["user_id"])  # restrict to own

    cursor = leave_collection.find(filter_query).skip(offset).limit(limit)
    items: List[LeaveRequestOut] = []
    for doc in cursor:
        items.append(
            LeaveRequestOut(
                request_id=doc["_id"],
                user_id=doc["user_id"],
                start_date=doc["start_date"],
                end_date=doc["end_date"],
                reason=doc["reason"],
                status=doc["status"],
                approved_by=doc.get("approved_by"),
                created_at=doc["created_at"],
                updated_at=doc.get("updated_at"),
            )
        )
    return items


def update_leave_request(
    request_id: str, update_data: LeaveRequestUpdate, current_user: dict
) -> LeaveRequestOut:
    db = get_db()
    if db is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database connection failed"
        )
    
    leave_collection = db["leaveRequest"]
    doc = leave_collection.find_one({"_id": ObjectId(request_id)})
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Request Not Found"
        )

    if current_user["role"] != "manager" and str(doc["user_id"]) != current_user["user_id"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="not access")

    update_fields = update_data.model_dump(exclude_unset=True)
    if not update_fields:
        return LeaveRequestOut(
            request_id=doc["_id"],
            user_id=doc["user_id"],
            start_date=doc["start_date"],
            end_date=doc["end_date"],
            reason=doc["reason"],
            status=doc["status"],
            approved_by=doc.get("approved_by"),
            created_at=doc["created_at"],
            updated_at=doc.get("updated_at"),
        )

    update_fields["updated_at"] = datetime.now()
    leave_collection.update_one({"_id": ObjectId(request_id)}, {"$set": update_fields})
    updated = leave_collection.find_one({"_id": ObjectId(request_id)})
    return LeaveRequestOut(
        request_id=updated["_id"],
        user_id=updated["user_id"],
        start_date=updated["start_date"],
        end_date=updated["end_date"],
        reason=updated["reason"],
        status=updated["status"],
        approved_by=updated.get("approved_by"),
        created_at=updated["created_at"],
        updated_at=updated.get("updated_at"),
    )


def delete_leave_request(request_id: str, current_user: dict) -> dict:
    db = get_db()
    if db is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database connection failed"
        )
    
    leave_collection = db["leaveRequest"]
    doc = leave_collection.find_one({"_id": ObjectId(request_id)})
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="request NotFound"
        )
    if current_user["role"] != "manager" and str(doc["user_id"]) != current_user["user_id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="not access"
        )
    
    result = leave_collection.delete_one({"_id": ObjectId(request_id)})
    if result.deleted_count > 0:
        return {"message": "request successfully deleted."}
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete request"
        )