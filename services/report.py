from pymongo import errors
from datetime import datetime
from bson import ObjectId
from fastapi import HTTPException, status
from starlette.status import HTTP_403_FORBIDDEN
from models.report import report_creat, report_out, report_update
from utils.db import get_db
from typing import Optional


def create_report(data: report_creat, current_user: dict):
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
        "hours_worked": data.hours_worked,
        "date": data.date,
        "description": data.description,
        "status": "pending",
        "approved_by": None,
        "created_at": datetime.now()
    }
    reports_collection.insert_one(report_data)

    return report_out(
        report_id=str(report_data["_id"]),
        user_id=str(report_data["user_id"]),
        date=report_data["date"],
        description=report_data["description"],
        hours_worked=report_data["hours_worked"],
        status=report_data["status"],
        approved_by=report_data["approved_by"],
        created_at=report_data["created_at"],
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
    
    reports = []
    for doc in cursor:
        reports.append(
            report_out(
                report_id=str(doc["_id"]),
                user_id=str(doc["user_id"]),
                date=doc["date"],
                description=doc["description"],
                hours_worked=doc["hours_worked"],
                status=doc["status"],
                approved_by=doc["approved_by"],
                created_at=doc["created_at"],
            )
        )

    return reports


def update_report(report_id: str, update_data: report_update, current_user: dict) -> report_out:
    db = get_db()
    reports_collection = db["reports"]
    existing_report = reports_collection.find_one({"_id": ObjectId(report_id)})
    if not existing_report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="report not found"
        )
    if str(existing_report["user_id"]) != current_user["user_id"] or current_user["role"] != "employee":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="only employee can edit reports!!"
        )
    
    update_fields = {"created_at": existing_report["created_at"]}
    if update_data.description is not None:
        update_fields["description"] = update_data.description 
    if update_data.hours_worked is not None:
        update_fields["hours_worked"] = update_data.hours_worked
    if len(update_fields) == 1:
        # Nothing to update; return current state
        return report_out(
            report_id=str(existing_report["_id"]),
            user_id=str(existing_report["user_id"]),
            date=existing_report["date"],
            description=existing_report["description"],
            hours_worked=existing_report["hours_worked"],
            status=existing_report["status"],
            approved_by=existing_report["approved_by"],
            created_at=existing_report["created_at"],
        )
    reports_collection.update_one(
        {"_id": ObjectId(report_id)},
        {"$set": update_fields}
        )

    updated_doc = reports_collection.find_one({"_id": ObjectId(report_id)})
    return report_out(
        report_id=str(updated_doc["_id"]),
        user_id=str(updated_doc["user_id"]),
        date=updated_doc["date"],
        description=updated_doc["description"],
        hours_worked=updated_doc["hours_worked"],
        status=updated_doc["status"],
        approved_by=updated_doc["approved_by"],
        created_at=updated_doc["created_at"],
    )



def delete_Reports(report_id: str, current_user: dict):
    db = get_db()
    reports_collection = db["reports"]
    doc = reports_collection.find_one({"_id": ObjectId(report_id)})
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="reoprt not found"
        )    

    is_owner = str(doc["user_id"]) == current_user["user_id"]
    is_manager = current_user["role"] == "manager"
    if not is_owner and not is_manager:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN,
            detail="no access"
        )
    reports_collection.delete_one({"_id": ObjectId(report_id)})
    return {"message": "Report successfully deleted"}