import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime
from typing import List, Optional
from bson import ObjectId
from fastapi import HTTPException, status

from models.report import report_creat, report_update, report_out, PyObjectId
from services.auth import get_current_user
from utils.db import get_db


def create_report(data: report_creat, current_user: dict) -> report_out:
    if current_user["role"] not in ["employee", "manager"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only employees and managers can create reports",
        )

    db = get_db()
    if db is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database connection failed"
        )
    
    report_collection = db["reports"]

    report_data = {
        "_id": ObjectId(),
        "user_id": data.user_id,
        "date": data.date,
        "description": data.description,
        "hours_worked": data.hours_worked,
        "status": data.status,
        "approved_by": data.approved_by,
        "created_at": datetime.now(),
    }

    result = report_collection.insert_one(report_data)

    return report_out(
        report_id=result.inserted_id,
        user_id=report_data["user_id"],
        date=report_data["date"],
        description=report_data["description"],
        hours_worked=report_data["hours_worked"],
        status=report_data["status"],
        approved_by=report_data["approved_by"],
        created_at=report_data["created_at"],
    )


def get_reports(
    user_id: Optional[str] = None,
    report_status: Optional[str] = None,
    limit: int = 20,
    offset: int = 0,
    current_user: Optional[dict] = None,
) -> List[report_out]:
    db = get_db()
    if db is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database connection failed"
        )
    
    report_collection = db["reports"]

    filter_query: dict = {}
    if user_id:
        filter_query["user_id"] = ObjectId(user_id)
    if report_status:
        filter_query["status"] = report_status
    if current_user and current_user.get("role") == "employee":
        filter_query["user_id"] = ObjectId(current_user["user_id"])

    cursor = report_collection.find(filter_query).skip(offset).limit(limit)
    items: List[report_out] = []
    for doc in cursor:
        items.append(
            report_out(
                report_id=doc["_id"],
                user_id=doc["user_id"],
                date=doc["date"],
                description=doc["description"],
                hours_worked=doc["hours_worked"],
                status=doc["status"],
                approved_by=doc["approved_by"],
                created_at=doc["created_at"],
            )
        )
    return items


def update_report(
    report_id: str, update_data: report_update, current_user: dict
) -> report_out:
    db = get_db()
    if db is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database connection failed"
        )
    
    report_collection = db["reports"]
    existing_report = report_collection.find_one({"_id": ObjectId(report_id)})
    if not existing_report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Report Not Found"
        )

    if current_user["role"] != "manager" and str(existing_report["user_id"]) != current_user["user_id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the report owner or managers can update reports",
        )

    update_fields = update_data.model_dump(exclude_unset=True)
    if not update_fields:
        return report_out(
            report_id=existing_report["_id"],
            user_id=existing_report["user_id"],
            date=existing_report["date"],
            description=existing_report["description"],
            hours_worked=existing_report["hours_worked"],
            status=existing_report["status"],
            approved_by=existing_report["approved_by"],
            created_at=existing_report["created_at"],
        )

    update_fields["updated_at"] = datetime.now()
    report_collection.update_one({"_id": ObjectId(report_id)}, {"$set": update_fields})
    updated_doc = report_collection.find_one({"_id": ObjectId(report_id)})
    return report_out(
        report_id=updated_doc["_id"],
        user_id=updated_doc["user_id"],
        date=updated_doc["date"],
        description=updated_doc["description"],
        hours_worked=updated_doc["hours_worked"],
        status=updated_doc["status"],
        approved_by=updated_doc["approved_by"],
        created_at=updated_doc["created_at"],
    )


def delete_Reports(report_id: str, current_user: dict) -> dict:
    db = get_db()
    if db is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database connection failed"
        )
    
    report_collection = db["reports"]
    doc = report_collection.find_one({"_id": ObjectId(report_id)})
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report Not Found"
        )

    if current_user["role"] != "manager" and str(doc["user_id"]) != current_user["user_id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the report owner or managers can delete reports"
        )

    result = report_collection.delete_one({"_id": ObjectId(report_id)})
    if result.deleted_count > 0:
        return {"message": "Report successfully deleted."}
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete report"
        )