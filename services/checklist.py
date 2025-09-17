from datetime import datetime
from bson import ObjectId
from fastapi import HTTPException, status
from typing import Optional, List
from models.checklist import ChecklistCreate, ChecklistOut, ChecklistUpdate
from utils.db import get_db
from services.log import logger, create_log
from models.log import logCreate


def _map_document_to_checklist_out(document: dict) -> ChecklistOut:
    # mapping simple helper (kept for safety)
    result = ChecklistOut(
        checklist_id=str(document["_id"]),
        title=document["title"],
        task_id=document["task_id"],
        description=document["description"],
        is_completed=document["is_completed"],
        assigned_to=document["assigned_to"],
        due_date=document["due_date"],
        priority=document["priority"],
        role=document.get("role"),
        role_payload=document.get("role_payload"),
        created_by=document["created_by"],
        created_at=document["created_at"],
        updated_at=document["updated_at"],
    )
    return result

def create_checklist(data: ChecklistCreate, current_user: dict) -> ChecklistOut:
    db = get_db("checklists_db")
    collection = db["checklist"]

    now = datetime.now()
    checklist_data = {
        "title": data.title,
        "task_id": data.task_id,
        "description": data.description,
        "is_completed": data.is_completed,
        "assigned_to": data.assigned_to,
        "due_date": datetime.combine(data.due_date, datetime.min.time()),
        "priority": data.priority,
        "role": data.role,
        "role_payload": data.role_payload,
        "created_by": current_user.get("user_id"),
        "created_at": now,
        "updated_at": now,
    }

    result = collection.insert_one(checklist_data)
    checklist_data["_id"] = result.inserted_id
    checklist_data["checklist_id"] = str(result.inserted_id)
    try:
        if current_user and current_user.get("user_id"):
            create_log(
                logCreate(
                    action_type="checklist_create",
                    user_id=current_user["user_id"],
                    description=f"Created checklist {checklist_data['checklist_id']} - {checklist_data['title']}"
                ),
                current_user,
            )
    except Exception:
        pass
    return _map_document_to_checklist_out(checklist_data)


def get_checklist(
    task_id: Optional[str] = None,
    title: Optional[str] = None,
    description: Optional[str] = None,
    limit: int = 20,
    offset: int = 0,
    current_user: dict = None,
) -> List[ChecklistOut]:
    db = get_db("checklists_db")
    collection = db["checklist"]

    filter_query: dict = {}

    if task_id:
        try:
            filter_query["task_id"] = ObjectId(task_id)
        except Exception:
            filter_query["task_id"] = task_id
    if title:
        filter_query["title"] = title
    if description:
        filter_query["description"] = description
    if current_user and current_user.get("role") == "employee":
        try:
            filter_query["assigned_to"] = ObjectId(current_user["user_id"])
        except Exception:
            filter_query["assigned_to"] = current_user["user_id"]

    cursor = collection.find(filter_query).skip(offset).limit(limit)
    items: List[ChecklistOut] = []
    for document in cursor:
        items.append(_map_document_to_checklist_out(document))
    return items


def update_checklist(
    checklist_id: str, update_data: ChecklistUpdate, current_user: dict = None
) -> ChecklistOut:
    db = get_db("checklists_db")
    collection = db["checklist"]

    existing = collection.find_one({"_id": ObjectId(checklist_id)})
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Checklist not found",
        )
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Access denied"
        )
    is_manager = current_user.get("role") in ["manager", "admin1", "admin2"]
    current_user_id = current_user.get("user_id")
    is_owner = current_user_id in {existing.get("assigned_to"), existing.get("created_by")}
    if not (is_manager or is_owner):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Access denied"
        )

    update_fields = {k: v for k, v in update_data.model_dump(exclude_unset=True).items()}
    if not update_fields:
        return _map_document_to_checklist_out(existing)

    update_fields["updated_at"] = datetime.now()

    collection.update_one({"_id": ObjectId(checklist_id)}, {"$set": update_fields})
    updated = collection.find_one({"_id": ObjectId(checklist_id)})
    try:
        if current_user and current_user.get("user_id"):
            create_log(
                logCreate(
                    action_type="checklist_update",
                    user_id=current_user["user_id"],
                    description=f"Updated checklist {checklist_id}"
                ),
                current_user,
            )
    except Exception:
        pass
    return _map_document_to_checklist_out(updated)


def delete_checklist(checklist_id: str, current_user: dict):
    db = get_db("checklists_db")
    collection = db["checklist"]
    existing = collection.find_one({"_id": ObjectId(checklist_id)})
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Checklist not found"
        )
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Access denied"
        )
    is_manager = current_user.get("role") in ["manager", "admin1", "admin2"]
    current_user_id = current_user.get("user_id")
    is_owner = current_user_id in {existing.get("assigned_to"), existing.get("created_by")}
    if not (is_manager or is_owner):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Access denied"
        )
    collection.delete_one({"_id": ObjectId(checklist_id)})
    try:
        if current_user and current_user.get("user_id"):
            create_log(
                logCreate(
                    action_type="checklist_delete",
                    user_id=current_user["user_id"],
                    description=f"Deleted checklist {checklist_id}"
                ),
                current_user,
            )
    except Exception:
        pass
    return {"message": "Checklist successfully deleted."}

