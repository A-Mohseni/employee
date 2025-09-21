from typing import Dict
from fastapi import HTTPException, status
from bson import ObjectId
from models.dashboard import DashboardStats
from utils.db import get_db


def get_dashboard(current_user: dict) -> DashboardStats:
    allowed_roles = {"manager_women", "manager_men", "admin1", "admin2"}
    if current_user.get("role") not in allowed_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No access to dashboard",
        )

    db = get_db()

    reports_coll = db["reports"]
    total_reports = reports_coll.count_documents({})
    reports_by_status_cursor = reports_coll.aggregate([
        {"$group": {"_id": "$status", "count": {"$sum": 1}}}
    ])
    reports_by_status: Dict[str, int] = {doc["_id"]: doc["count"] for doc in reports_by_status_cursor if doc.get("_id") is not None}

    leaves_coll = db["leave_requests"]
    total_leave_request = leaves_coll.count_documents({})
    leave_by_status_cursor = leaves_coll.aggregate([
        {"$group": {"_id": "$status", "count": {"$sum": 1}}}
    ])
    leave_request_by_status: Dict[str, int] = {doc["_id"]: doc["count"] for doc in leave_by_status_cursor if doc.get("_id") is not None}

    return DashboardStats(
        total_reports=total_reports,
        reports_by_status=reports_by_status,
        total_leave_request=total_leave_request,
        leave_request_by_status=leave_request_by_status,
        user_id=str(current_user.get("user_id")) if current_user.get("user_id") is not None else None,
    )