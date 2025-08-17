from pymongo import errors
from datetime import datetime
from bson import ObjectId
from fastapi import HTTPException, status
from starlette.status import HTTP_403_FORBIDDEN
from models import report
from models.report import report_creat, report_out, report_update
from utils.db import get_db
from typing import List, Optional


def create_report(report: report_creat, current_user: dict):
    if current_user["role"] != "employee":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=" only employee can add report!! "
        ) 

    db = get_db()
    reports_collection = db["reports"]

    report_data = {
        "_id": ObjectId(),
        "user_id": ObjectId(current_user["user_id"]),
        "hours_worked": report.hours_worked,
        "date": report.data,  
        "description": report.description,
        "status": "pending",
        "approved_by": None,
        "created_at": datetime.now()
    }
    reports_collection.insert_one(report_data)

    return report_out(
        report_id=report_data["_id"],
        user_id=report_data["user_id"],
        description=report_data["description"], 
        hours_worked=report_data["hours_worked"],
        status=report_data["status"],
        approved_by=report_data["approved_by"],
        created_at=report_data["created_at"]
    )


def get_reports(
    user_id: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 20,
    offset: int = 0,
    current_user: dict = None
) -> list[report_out]:
    db = get_db()
    reports_collection = db["reports"]

    filter_query = {}
    if user_id:
        filter_query["user_id"] = ObjectId(user_id)
    if status:
        filter_query["status"] = status
    

    cursor = reports_collection.find(filter_query).skip(offset).limit(limit)
    
    reports = [
        report_out(
            report_id=report["_id"],
            user_id=report["user_id"],
            date=report["date"],
            description=report["description"],
            hours_worked=report["hours_worked"],
            status=report["status"],
            approved_by=report["approved_by"],
            created_at=report["created_at"]
        )
        for report in cursor
    ]

    return reports


def update_report(report_id: str, update_data: report_update, current_user: dict) -> report_out:
    db = get_db() 
    reports_collection = db["reports"]
    report = reports_collection.find_one({"_id": ObjectId(report_id)})
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="report not found"
        )
    if str(report["user_id"]) != current_user["user_id"] or current_user["role"] != "employee":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="only employee can edit reports!!"
        )
    
    update_fields = {"created_at": report["created_at"]}
    if update_data.description is not None:
        update_fields["description"] = update_data.description 
    if update_data.hours_worked is not None:
        update_fields["hours_worked"] = update_data.hours_worked
    if len(update_fields)==1:
        return report_out
    reports_collection.update_one(
        {"_id": ObjectId(report_id)},
        {"$set": update_fields}
        )

    update_report=reports_collection.find_one({"_id":ObjectId(report_id)})
    return report_out(**update_report)