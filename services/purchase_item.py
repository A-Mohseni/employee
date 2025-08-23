import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime
from typing import List, Optional
from bson import ObjectId
from fastapi import HTTPException, status

from models.purchase_item import (
    PurchaseItemCreate,
    PurchaseItemOut,
    PurchaseItemUpdate,
    PyObjectId
)
from services.auth import get_current_user
from utils.db import get_db


def create_purchase_item(data: PurchaseItemCreate, current_user: dict) -> PurchaseItemOut:
    if current_user["role"] not in ["manager", "supervisor"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only managers and supervisors can create purchase items",
        )

    db = get_db()
    if db is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database connection failed"
        )
    
    purchase_collection = db["purchaseItems"]

    doc = {
        "name": data.name,
        "quantity": data.quantity,
        "priority": data.priority,
        "status": data.status,
        "notes": data.notes,
        "category": data.category,
        "description": data.description,
        "created_by": current_user["user_id"],
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
    }

    result = purchase_collection.insert_one(doc)

    return PurchaseItemOut(
        item_id=result.inserted_id,
        name=doc["name"],
        quantity=doc["quantity"],
        priority=doc["priority"],
        status=doc["status"],
        created_by=doc["created_by"],
        created_at=doc["created_at"],
        updated_at=doc["updated_at"],
        notes=doc["notes"],
        category=doc["category"],
        description=doc["description"],
    )


def get_purchase_items(
    item_id: Optional[str] = None,
    limit: int = 20,
    offset: int = 0,
    current_user: Optional[dict] = None,
) -> List[PurchaseItemOut]:
    db = get_db()
    if db is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database connection failed"
        )
    
    purchase_collection = db["purchaseItems"]

    filter_query: dict = {}
    if item_id:
        filter_query["_id"] = ObjectId(item_id)

    cursor = purchase_collection.find(filter_query).skip(offset).limit(limit)
    items: List[PurchaseItemOut] = []
    for doc in cursor:
        items.append(
            PurchaseItemOut(
                item_id=doc["_id"],
                name=doc["name"],
                quantity=doc["quantity"],
                priority=doc["priority"],
                status=doc["status"],
                created_by=doc["created_by"],
                created_at=doc["created_at"],
                updated_at=doc["updated_at"],
                notes=doc.get("notes"),
                category=doc["category"],
                description=doc.get("description"),
            )
        )
    return items


def update_purchase_item(
    item_id: str, update_data: PurchaseItemUpdate, current_user: dict
) -> PurchaseItemOut:
    db = get_db()
    if db is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database connection failed"
        )
    
    purchase_collection = db["purchaseItems"]
    doc = purchase_collection.find_one({"_id": ObjectId(item_id)})
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Item Not Found"
        )

    if current_user["role"] not in ["manager", "supervisor"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only managers and supervisors can update purchase items",
        )

    update_fields = update_data.model_dump(exclude_unset=True)
    if not update_fields:
        return PurchaseItemOut(
            item_id=doc["_id"],
            name=doc["name"],
            quantity=doc["quantity"],
            priority=doc["priority"],
            status=doc["status"],
            created_by=doc["created_by"],
            created_at=doc["created_at"],
            updated_at=doc["updated_at"],
            notes=doc.get("notes"),
            category=doc["category"],
            description=doc.get("description"),
        )

    update_fields["updated_at"] = datetime.now()
    purchase_collection.update_one({"_id": ObjectId(item_id)}, {"$set": update_fields})
    updated = purchase_collection.find_one({"_id": ObjectId(item_id)})
    return PurchaseItemOut(
        item_id=updated["_id"],
        name=updated["name"],
        quantity=updated["quantity"],
        priority=updated["priority"],
        status=updated["status"],
        created_by=updated["created_by"],
        created_at=updated["created_at"],
        updated_at=updated["updated_at"],
        notes=updated.get("notes"),
        category=updated["category"],
        description=updated.get("description"),
    )


def delete_purchase_item(item_id: str, current_user: dict) -> dict:
    db = get_db()
    if db is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database connection failed"
        )
    
    purchase_collection = db["purchaseItems"]
    doc = purchase_collection.find_one({"_id": ObjectId(item_id)})
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item Not Found"
        )

    if current_user["role"] not in ["manager", "supervisor"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only managers and supervisors can delete purchase items"
        )

    result = purchase_collection.delete_one({"_id": ObjectId(item_id)})
    if result.deleted_count > 0:
        return {"message": "Item successfully deleted."}
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete item"
        )