from datetime import datetime
from bson import ObjectId
from fastapi import HTTPException, status
from models.purchase_item import PurchaseItemCreate, PurchaseItemOut, PurchaseItemUpdate
from utils.db import get_db
from typing import Optional, List


def create_purchase_item(data: PurchaseItemCreate, current_user: dict) -> PurchaseItemOut:
    if current_user["role"] not in ["manager"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="not access",
        )

    db = get_db()
    collection = db["purchaseItem"]

    now = datetime.now()
    doc = {
        "name": data.name,
        "quantity": data.quantity,
        "priority": data.priority,
        "status": data.status,
        "created_by": ObjectId(current_user["user_id"]),
        "created_at": now,
        "updated_at": now,
        "notes": data.notes,
        "category": data.category,
        "description": data.description,
    }
    result = collection.insert_one(doc)

    return PurchaseItemOut(
        item_id=result.inserted_id,
        name=doc["name"],
        quantity=doc["quantity"],
        priority=doc["priority"],
        status=doc["status"],
        created_at=doc["created_at"],
        created_by=doc["created_by"],
        updated_at=doc["updated_at"],
        notes=doc.get("notes"),
        category=doc["category"],
        description=doc.get("description"),
    )


def get_purchase_items(
    name: Optional[str] = None,
    item_id: Optional[str] = None,
    limit: int = 20,
    offset: int = 0,
    current_user: Optional[dict] = None,
) -> List[PurchaseItemOut]:
    db = get_db()
    collection = db["purchaseItem"]

    filter_query: dict = {}
    if name:
        filter_query["name"] = name
    if item_id:
        filter_query["_id"] = ObjectId(item_id)

    cursor = collection.find(filter_query).skip(offset).limit(limit)
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


def update_purchase_item(item_id: str, update_data: PurchaseItemUpdate, current_user: dict) -> PurchaseItemOut:
    db = get_db()
    collection = db["purchaseItem"]
    doc = collection.find_one({"_id": ObjectId(item_id)})
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item Not Found")

    if str(doc["created_by"]) != current_user["user_id"] and current_user["role"] != "manager":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="not access")

    update_fields = {k: v for k, v in update_data.model_dump(exclude_unset=True).items()}
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
    collection.update_one({"_id": ObjectId(item_id)}, {"$set": update_fields})
    updated = collection.find_one({"_id": ObjectId(item_id)})
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


def delete_purchase_item(item_id: str, current_user: dict):
    db = get_db()
    collection = db["purchaseItem"]
    doc = collection.find_one({"_id": ObjectId(item_id)})
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item Not Found")

    if str(doc["created_by"]) != current_user["user_id"] and current_user["role"] != "manager":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="not access")

    collection.delete_one({"_id": ObjectId(item_id)})
    return {"message": "Item successfully deleted."}