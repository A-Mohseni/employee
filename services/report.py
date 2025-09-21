import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime
from typing import List, Optional
from bson import ObjectId
from fastapi import HTTPException, status

from models.report import report_create, report_update, report_out
from utils.db import get_db
from services.log import logger, create_log
from models.log import logCreate
from pymongo import ASCENDING, DESCENDING


def create_report_indexes():
    try:
        db = get_db()
        report_collection = db["reports"]
        
        report_collection.create_index([("created_by", ASCENDING)])
        report_collection.create_index([("status", ASCENDING)])
        report_collection.create_index([("created_at", DESCENDING)])
        report_collection.create_index([("approved_by", ASCENDING)])
        
        logger.info("Report indexes created successfully")
    except Exception as e:
        logger.error(f"Error creating report indexes: {str(e)}")


create_report_indexes()


def create_report(data: report_create, current_user: dict) -> report_out:
    if current_user.get("role") not in ["employee", "manager_women", "manager_men", "admin1", "admin2"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    db = get_db()
    report_collection = db["reports"]

    report_data = {
        "_id": ObjectId(),
        "created_by": current_user.get("user_id"),
        "content": data.content,
        "approved_by": None,
        "status": "pending",
        "created_at": datetime.now(),
        "updated_at": None,
    }

    result = report_collection.insert_one(report_data)
    try:
        if current_user and current_user.get("user_id"):
            create_log(
                logCreate(
                    action_type="report_create",
                    user_id=current_user["user_id"],
                    description=f"Created report {str(result.inserted_id)}"
                ),
                current_user,
            )
    except Exception:
        pass

    return report_out(
        _id=str(result.inserted_id),
        created_by=str(report_data["created_by"]),
        content=report_data["content"],
        approved_by=report_data["approved_by"],
        status=report_data["status"],
        created_at=report_data["created_at"],
        updated_at=report_data["updated_at"],
    )


def get_reports(
    user_id: Optional[str] = None,
    report_status: Optional[str] = None,
    limit: int = 20,
    offset: int = 0,
    current_user: Optional[dict] = None,
) -> List[report_out]:
    db = get_db()
    report_collection = db["reports"]

    filter_query: dict = {}
    if current_user and current_user.get("role") == "employee":
        filter_query["created_by"] = current_user.get("user_id")
    else:
        if current_user and current_user.get("role") in ("manager_women", "manager_men"):
            if report_status:
                filter_query["status"] = report_status
        else:
            if user_id:
                filter_query["created_by"] = user_id
            if report_status:
                filter_query["status"] = report_status

    cursor = report_collection.find(filter_query).skip(offset).limit(limit)
    items: List[report_out] = []
    for doc in cursor:
        items.append(
            report_out(
                _id=str(doc["_id"]),
                created_by=str(doc["created_by"]),
                content=doc["content"],
                approved_by=doc.get("approved_by"),
                status=doc["status"],
                created_at=doc["created_at"],
                updated_at=doc.get("updated_at"),
            )
        )
    return items


def update_report(
    report_id: str, update_data: report_update, current_user: dict
) -> report_out:
    db = get_db()
    report_collection = db["reports"]
    existing_report = report_collection.find_one({"_id": ObjectId(report_id)})
    if not existing_report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Report Not Found"
        )
    if current_user.get("role") == "employee" and str(existing_report["created_by"]) != current_user.get("user_id"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    update_fields = update_data.model_dump(exclude_unset=True)
    if not update_fields:
        return report_out(
            _id=str(existing_report["_id"]),
            created_by=str(existing_report["created_by"]),
            content=existing_report["content"],
            approved_by=existing_report.get("approved_by"),
            status=existing_report["status"],
            created_at=existing_report["created_at"],
            updated_at=existing_report.get("updated_at"),
        )

    update_fields["updated_at"] = datetime.now()
    report_collection.update_one({"_id": ObjectId(report_id)}, {"$set": update_fields})
    updated_doc = report_collection.find_one({"_id": ObjectId(report_id)})
    try:
        if current_user and current_user.get("user_id"):
            create_log(
                logCreate(
                    action_type="report_update",
                    user_id=current_user["user_id"],
                    description=f"Updated report {report_id}"
                ),
                current_user,
            )
    except Exception:
        pass
    return report_out(
        _id=str(updated_doc["_id"]),
        created_by=str(updated_doc["created_by"]),
        content=updated_doc["content"],
        approved_by=updated_doc.get("approved_by"),
        status=updated_doc["status"],
        created_at=updated_doc["created_at"],
        updated_at=updated_doc.get("updated_at"),
    )


def delete_report(report_id: str, current_user: dict) -> dict:
    db = get_db()
    report_collection = db["reports"]
    doc = report_collection.find_one({"_id": ObjectId(report_id)})
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report Not Found"
        )
    if current_user.get("role") == "employee" and str(doc["created_by"]) != current_user.get("user_id"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    result = report_collection.delete_one({"_id": ObjectId(report_id)})
    if result.deleted_count > 0:
        try:
            if current_user and current_user.get("user_id"):
                create_log(
                    logCreate(
                        action_type="report_delete",
                        user_id=current_user["user_id"],
                        description=f"Deleted report {report_id}"
                    ),
                    current_user,
                )
        except Exception:
            pass
        return {"message": "Report successfully deleted."}
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete report"
        )


def approve_report(report_id: str, current_user: dict) -> report_out:
    if current_user.get("role") not in ["manager_women", "manager_men", "admin1", "admin2"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    db = get_db()
    report_collection = db["reports"]
    
    try:
        doc = report_collection.find_one({"_id": ObjectId(report_id)})
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid report ID format")
    
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report Not Found")
    
    if doc["status"] != "pending":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid state for approval")
    
    update_data = {
        "approved_by": current_user.get("user_id"),
        "status": "approved",
        "updated_at": datetime.now(),
    }
    
    report_collection.update_one(
        {"_id": ObjectId(report_id)},
        {"$set": update_data}
    )
    
    updated = report_collection.find_one({"_id": ObjectId(report_id)})
    
    try:
        if current_user and current_user.get("user_id"):
            create_log(
                logCreate(
                    action_type="report_approve",
                    user_id=current_user["user_id"],
                    description=f"Approved report {report_id}"
                ),
                current_user,
            )
    except Exception:
        pass
    
    return report_out(
        _id=str(updated["_id"]),
        created_by=str(updated["created_by"]),
        content=updated["content"],
        approved_by=updated.get("approved_by"),
        status=updated["status"],
        created_at=updated["created_at"],
        updated_at=updated.get("updated_at"),
    )