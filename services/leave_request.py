import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime
from typing import Optional, List
from bson import ObjectId
from fastapi import HTTPException, status

from models.leave_request import LeaveRequestCreate, LeaveRequestOut, LeaveRequestUpdate
from utils.db import get_db
from services.log import service_exception, logger


@service_exception
def create_leave_request(data: LeaveRequestCreate, current_user: dict) -> dict:
    db = get_db()
    collection = db["leave_requests"]
    now = datetime.now()
    doc = {
        "request_date": data.request_date,
        "start_date": data.start_date,
        "end_date": data.end_date,
        "reason": data.reason,
        "status": "pending_phase1",
        "created_by": current_user.get("user_id") if current_user else None,
        "created_at": now,
        "updated_at": now,
    }
    try:
        result = collection.insert_one(doc)
        doc["_id"] = result.inserted_id
        return doc
    except Exception as exc:
        logger.exception("Error creating leave request: %s", exc)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create leave request")


@service_exception
def get_leave_requests(
    user_id: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    current_user: dict = None,
) -> List[dict]:
    db = get_db()
    collection = db["leave_requests"]
    query = {}
    if user_id:
        try:
            query["created_by"] = int(user_id)
        except Exception:
            query["created_by"] = user_id
    try:
        cursor = collection.find(query).skip(offset).limit(limit)
        return list(cursor)
    except Exception as exc:
        logger.exception("Error fetching leave requests: %s", exc)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to fetch leave requests")


@service_exception
def update_leave_request(leave_id: str, update_data: LeaveRequestUpdate, current_user: dict = None) -> dict:
    db = get_db()
    collection = db["leave_requests"]
    existing = collection.find_one({"_id": ObjectId(leave_id)})
    if not existing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Leave request not found")

    update_fields = {k: v for k, v in update_data.dict(exclude_unset=True).items()}
    if not update_fields:
        return existing

    update_fields["updated_at"] = datetime.now()
    try:
        collection.update_one({"_id": ObjectId(leave_id)}, {"$set": update_fields})
        return collection.find_one({"_id": ObjectId(leave_id)})
    except Exception as exc:
        logger.exception("Error updating leave request %s: %s", leave_id, exc)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update leave request")


@service_exception
def delete_leave_request(leave_id: str, current_user: dict) -> dict:
    db = get_db()
    collection = db["leave_requests"]
    existing = collection.find_one({"_id": ObjectId(leave_id)})
    if not existing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Leave request not found")
    try:
        res = collection.delete_one({"_id": ObjectId(leave_id)})
        if res.deleted_count == 0:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to delete leave request")
        return {"message": "Leave request deleted"}
    except Exception as exc:
        logger.exception("Error deleting leave request %s: %s", leave_id, exc)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to delete leave request")


# اضافه‌شده: تایید مرحله اول مرخصی
@service_exception
def approve_leave_phase1(leave_id: str, current_user: dict) -> dict:
    """
    Approve leave request for phase 1.
    - تنها کاربران دارای نقش manager یا hr مجازند.
    - فیلد status به 'approved_phase1' تغییر می‌کند و approved_by_phase1 و updated_at ذخیره می‌شود.
    """
    db = get_db()
    collection = db["leave_requests"]
    existing = collection.find_one({"_id": ObjectId(leave_id)})
    if not existing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Leave request not found")

    user_role = current_user.get("role") if current_user else None
    allowed_roles = {"manager", "hr"}
    if user_role not in allowed_roles:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    try:
        now = datetime.now()
        update_payload = {
            "status": "approved_phase1",
            "approved_by_phase1": current_user.get("user_id"),
            "updated_at": now,
        }
        collection.update_one({"_id": ObjectId(leave_id)}, {"$set": update_payload})
        updated = collection.find_one({"_id": ObjectId(leave_id)})
        return updated
    except Exception as exc:
        logger.exception("Error approving leave (phase1) %s: %s", leave_id, exc)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to approve leave (phase1)")


@service_exception
def approve_leave_phase2(leave_id: str, current_user: dict) -> dict:
    """
    Approve leave request for phase 2.
    - فقط کاربران با نقش 'manager' یا 'hr' مجازند.
    - status به 'approved_phase2' تغییر می‌کند و approved_by_phase2 و updated_at ذخیره می‌شود.
    """
    db = get_db()
    collection = db["leave_requests"]
    existing = collection.find_one({"_id": ObjectId(leave_id)})
    if not existing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Leave request not found")

    user_role = current_user.get("role") if current_user else None
    allowed_roles = {"manager", "hr"}
    if user_role not in allowed_roles:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    try:
        now = datetime.now()
        update_payload = {
            "status": "approved_phase2",
            "approved_by_phase2": current_user.get("user_id"),
            "updated_at": now,
        }
        collection.update_one({"_id": ObjectId(leave_id)}, {"$set": update_payload})
        updated = collection.find_one({"_id": ObjectId(leave_id)})
        return updated
    except Exception as exc:
        logger.exception("Error approving leave (phase2) %s: %s", leave_id, exc)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to approve leave (phase2)")