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
    LeaveStatus,
    PyObjectId,
)
from utils.db import get_db


def create_leave_request(data: LeaveRequestCreate, current_user: dict) -> LeaveRequestOut:
    if current_user["role"] not in ["employee", "manager_women", "manager_men", "admin1", "admin2"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="not access")

    db = get_db()
    if db is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database connection failed"
        )
    
    leave_collection = db["leave_requests"]

    doc = {
        "created_by": ObjectId(data.created_by),
        "request_date": data.request_date,
        "start_date": data.start_date,
        "end_date": data.end_date,
        "reason": data.reason,
        "approval_phase1_by": None,
        "approval_phase1_at": None,
        "approval_phase2_by": None,
        "approval_phase2_at": None,
        "status": "pending_phase1",
        "created_at": datetime.now(),
        "updated_at": None,
    }
    result = leave_collection.insert_one(doc)

    return LeaveRequestOut(
        request_id=str(result.inserted_id),
        created_by=str(doc["created_by"]),
        request_date=doc["request_date"],
        start_date=doc["start_date"],
        end_date=doc["end_date"],
        reason=doc["reason"],
        approval_phase1_by=doc["approval_phase1_by"],
        approval_phase1_at=doc["approval_phase1_at"],
        approval_phase2_by=doc["approval_phase2_by"],
        approval_phase2_at=doc["approval_phase2_at"],
        status=doc["status"],
        created_at=doc["created_at"],
        updated_at=doc["updated_at"],
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
    
    leave_collection = db["leave_requests"]

    filter_query: dict = {}
    if request_id:
        filter_query["_id"] = ObjectId(request_id)
    if user_id:
        filter_query["created_by"] = ObjectId(user_id)
    if current_user and current_user.get("role") == "employee":
        filter_query["created_by"] = ObjectId(current_user["user_id"])

    cursor = leave_collection.find(filter_query).skip(offset).limit(limit)
    items: List[LeaveRequestOut] = []
    for doc in cursor:
        items.append(
            LeaveRequestOut(
                request_id=str(doc["_id"]),
                created_by=str(doc["created_by"]),
                request_date=doc["request_date"],
                start_date=doc["start_date"],
                end_date=doc["end_date"],
                reason=doc["reason"],
                approval_phase1_by=doc.get("approval_phase1_by"),
                approval_phase1_at=doc.get("approval_phase1_at"),
                approval_phase2_by=doc.get("approval_phase2_by"),
                approval_phase2_at=doc.get("approval_phase2_at"),
                status=doc["status"],
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
    
    leave_collection = db["leave_requests"]
    doc = leave_collection.find_one({"_id": ObjectId(request_id)})
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Request Not Found"
        )

    if current_user["role"] == "employee" and str(doc["created_by"]) != current_user["user_id"]:
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
        request_id=str(updated["_id"]),
        created_by=str(updated["created_by"]),
        request_date=updated["request_date"],
        start_date=updated["start_date"],
        end_date=updated["end_date"],
        reason=updated["reason"],
        approval_phase1_by=updated.get("approval_phase1_by"),
        approval_phase1_at=updated.get("approval_phase1_at"),
        approval_phase2_by=updated.get("approval_phase2_by"),
        approval_phase2_at=updated.get("approval_phase2_at"),
        status=updated["status"],
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
    
    leave_collection = db["leave_requests"]
    doc = leave_collection.find_one({"_id": ObjectId(request_id)})
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="request NotFound"
        )
    if current_user["role"] == "employee" and str(doc["created_by"]) != current_user["user_id"]:
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


def approve_leave_phase1(request_id: str, current_user: dict) -> LeaveRequestOut:
    if current_user["role"] != "admin2":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only Admin2 can approve phase 1")
    db = get_db()
    leave_collection = db["leave_requests"]
    doc = leave_collection.find_one({"_id": ObjectId(request_id)})
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Request Not Found")
    if doc["status"] != "pending_phase1":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid state for phase1 approval")
    leave_collection.update_one(
        {"_id": ObjectId(request_id)},
        {"$set": {
            "approval_phase1_by": ObjectId(current_user["user_id"]),
            "approval_phase1_at": datetime.now(),
            "status": "pending_phase2",
            "updated_at": datetime.now()
        }}
    )
    return get_leave_requests(request_id=request_id, limit=1)[0]


def approve_leave_phase2(request_id: str, current_user: dict) -> LeaveRequestOut:
    if current_user["role"] != "manager_women":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only Manager Women can approve phase 2")
    db = get_db()
    leave_collection = db["leave_requests"]
    doc = leave_collection.find_one({"_id": ObjectId(request_id)})
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Request Not Found")
    if doc["status"] != "pending_phase2":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid state for phase2 approval")
    leave_collection.update_one(
        {"_id": ObjectId(request_id)},
        {"$set": {
            "approval_phase2_by": ObjectId(current_user["user_id"]),
            "approval_phase2_at": datetime.now(),
            "status": "approved",
            "updated_at": datetime.now()
        }}
    )
    return get_leave_requests(request_id=request_id, limit=1)[0]