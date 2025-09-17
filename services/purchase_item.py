import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime
from typing import List, Optional, Dict, Any
from bson import ObjectId
from fastapi import HTTPException, status
from pymongo import ASCENDING, DESCENDING

from models.purchase_item import (
    PurchaseItemCreate,
    PurchaseItemOut,
    PurchaseItemUpdate,
    PurchaseItemFilter,
    PurchaseItemSummary,
    PurchaseStatus,
    PriorityLevel,
    PurchaseCategory
)
from services.auth import get_current_user
from utils.db import get_db
from services.log import logger, create_log
from models.log import logCreate


class PurchaseItemService:
    
    def __init__(self):
        self.db = get_db("purchases_db")
        self.collection = self.db["purchaseItems"]
        self._create_indexes()
    
    def _create_indexes(self):
        try:
            self.collection.create_index([("name", "text"), ("description", "text")])
            self.collection.create_index([("category", ASCENDING)])
            self.collection.create_index([("priority", ASCENDING)])
            self.collection.create_index([("status", ASCENDING)])
            self.collection.create_index([("created_by", ASCENDING)])
            self.collection.create_index([("created_at", DESCENDING)])
            self.collection.create_index([("required_date", ASCENDING)])
            self.collection.create_index([("supplier", ASCENDING)])
            self.collection.create_index([("budget_code", ASCENDING)])
            
            self.collection.create_index([
                ("category", ASCENDING),
                ("priority", ASCENDING),
                ("status", ASCENDING)
            ])
            
            logger.info("Purchase item indexes created successfully")
        except Exception as e:
            logger.error(f"Error creating indexes: {str(e)}")
    
    def create_purchase_item(self, data: PurchaseItemCreate, current_user: dict) -> PurchaseItemOut:
        try:
            total_price = None
            if data.quantity and data.unit_price:
                total_price = data.quantity * data.unit_price
            
            doc = {
                "name": data.name,
                "description": data.description,
                "quantity": data.quantity,
                "unit_price": data.unit_price,
                "total_price": total_price,
                "priority": data.priority,
                "status": data.status,
                "category": data.category,
                "notes": data.notes,
                "supplier": data.supplier,
                "budget_code": data.budget_code,
                "required_date": data.required_date,
                "created_by": current_user.get("user_id"),
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
            }
            
            result = self.collection.insert_one(doc)
            
            logger.info(f"Purchase item created: {result.inserted_id} by user: {current_user.get('user_id')}")
            try:
                if current_user and current_user.get("user_id"):
                    create_log(
                        logCreate(
                            action_type="purchase_create",
                            user_id=current_user["user_id"],
                            description=f"Created purchase item {str(result.inserted_id)} - {doc['name']}"
                        ),
                        current_user,
                    )
            except Exception:
                pass
            
            return self._doc_to_purchase_item_out(doc, result.inserted_id)
            
        except Exception as e:
            logger.error(f"Error creating purchase item: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error creating purchase item"
            )
    
    def get_purchase_item_by_id(self, item_id: str, current_user: dict) -> PurchaseItemOut:
        try:
            if not ObjectId.is_valid(item_id):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid item ID"
                )
            
            doc = self.collection.find_one({"_id": ObjectId(item_id)})
            if not doc:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Purchase item not found"
                )
            
            return self._doc_to_purchase_item_out(doc, doc["_id"])
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting purchase item: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error getting purchase item"
            )
    
    def get_purchase_items(
        self,
        filters: Optional[PurchaseItemFilter] = None,
        limit: int = 20,
        offset: int = 0,
        sort_by: str = "created_at",
        sort_order: str = "desc",
        current_user: Optional[dict] = None,
    ) -> List[PurchaseItemOut]:
        try:
            filter_query = self._build_filter_query(filters)
            
            sort_direction = DESCENDING if sort_order.lower() == "desc" else ASCENDING
            sort_field = sort_by if sort_by in ["name", "quantity", "priority", "status", "category", "created_at", "updated_at"] else "created_at"
            
            cursor = self.collection.find(filter_query).sort(sort_field, sort_direction).skip(offset).limit(limit)
            
            items = []
            for doc in cursor:
                items.append(self._doc_to_purchase_item_out(doc, doc["_id"]))
            
            return items
            
        except Exception as e:
            logger.error(f"Error getting purchase items: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error getting purchase items"
            )
    
    def update_purchase_item(
        self, item_id: str, update_data: PurchaseItemUpdate, current_user: dict
    ) -> PurchaseItemOut:
        try:
            if not ObjectId.is_valid(item_id):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid item ID"
                )
            
            doc = self.collection.find_one({"_id": ObjectId(item_id)})
            if not doc:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Purchase item not found"
                )
            
            update_fields = update_data.model_dump(exclude_unset=True)
            if not update_fields:
                return self._doc_to_purchase_item_out(doc, doc["_id"])
            
            if "quantity" in update_fields or "unit_price" in update_fields:
                quantity = update_fields.get("quantity", doc.get("quantity"))
                unit_price = update_fields.get("unit_price", doc.get("unit_price"))
                if quantity and unit_price:
                    update_fields["total_price"] = quantity * unit_price
            
            update_fields["updated_at"] = datetime.now()
            
            self.collection.update_one(
                {"_id": ObjectId(item_id)},
                {"$set": update_fields}
            )
            
            updated_doc = self.collection.find_one({"_id": ObjectId(item_id)})
            
            logger.info(f"Purchase item updated: {item_id} by user: {current_user.get('user_id')}")
            try:
                if current_user and current_user.get("user_id"):
                    create_log(
                        logCreate(
                            action_type="purchase_update",
                            user_id=current_user["user_id"],
                            description=f"Updated purchase item {item_id}"
                        ),
                        current_user,
                    )
            except Exception:
                pass
            
            return self._doc_to_purchase_item_out(updated_doc, updated_doc["_id"])
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error updating purchase item: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error updating purchase item"
            )
    
    def delete_purchase_item(self, item_id: str, current_user: dict) -> Dict[str, Any]:
        try:
            if not ObjectId.is_valid(item_id):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid item ID"
                )
            
            doc = self.collection.find_one({"_id": ObjectId(item_id)})
            if not doc:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Purchase item not found"
                )
            
            result = self.collection.delete_one({"_id": ObjectId(item_id)})
            
            if result.deleted_count > 0:
                logger.info(f"Purchase item deleted: {item_id} by user: {current_user.get('user_id')}")
                try:
                    if current_user and current_user.get("user_id"):
                        create_log(
                            logCreate(
                                action_type="purchase_delete",
                                user_id=current_user["user_id"],
                                description=f"Deleted purchase item {item_id}"
                            ),
                            current_user,
                        )
                except Exception:
                    pass
                return {"message": "Purchase item successfully deleted"}
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Error deleting purchase item"
                )
                
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error deleting purchase item: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error deleting purchase item"
            )
    
    def get_purchase_summary(self, current_user: dict) -> PurchaseItemSummary:
        try:
            total_items = self.collection.count_documents({})
            pending_items = self.collection.count_documents({"status": PurchaseStatus.PENDING})
            approved_items = self.collection.count_documents({"status": PurchaseStatus.APPROVED})
            purchased_items = self.collection.count_documents({"status": PurchaseStatus.PURCHASED})
            
            pipeline = [
                {"$match": {"total_price": {"$exists": True, "$ne": None}}},
                {"$group": {"_id": None, "total": {"$sum": "$total_price"}}}
            ]
            budget_result = list(self.collection.aggregate(pipeline))
            total_budget = budget_result[0]["total"] if budget_result else 0.0
            
            category_pipeline = [
                {"$group": {"_id": "$category", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}}
            ]
            category_breakdown = {}
            for item in self.collection.aggregate(category_pipeline):
                category_breakdown[item["_id"]] = item["count"]
            
            priority_pipeline = [
                {"$group": {"_id": "$priority", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}}
            ]
            priority_breakdown = {}
            for item in self.collection.aggregate(priority_pipeline):
                priority_breakdown[item["_id"]] = item["count"]
            
            return PurchaseItemSummary(
                total_items=total_items,
                pending_items=pending_items,
                approved_items=approved_items,
                purchased_items=purchased_items,
                total_budget=total_budget,
                category_breakdown=category_breakdown,
                priority_breakdown=priority_breakdown
            )
            
        except Exception as e:
            logger.error(f"Error getting purchase summary: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error getting purchase summary"
            )
    
    def _build_filter_query(self, filters: Optional[PurchaseItemFilter]) -> Dict[str, Any]:
        if not filters:
            return {}
        
        query = {}
        
        if filters.name:
            query["$or"] = [
                {"name": {"$regex": filters.name, "$options": "i"}},
                {"description": {"$regex": filters.name, "$options": "i"}}
            ]
        
        if filters.category:
            query["category"] = filters.category
        
        if filters.priority:
            query["priority"] = filters.priority
        
        if filters.status:
            query["status"] = filters.status
        
        if filters.supplier:
            query["supplier"] = {"$regex": filters.supplier, "$options": "i"}
        
        if filters.budget_code:
            query["budget_code"] = filters.budget_code
        
        if filters.created_by:
            query["created_by"] = filters.created_by
        
        if filters.created_from or filters.created_to:
            date_query = {}
            if filters.created_from:
                date_query["$gte"] = filters.created_from
            if filters.created_to:
                date_query["$lte"] = filters.created_to
            query["created_at"] = date_query
        
        if filters.required_from or filters.required_to:
            date_query = {}
            if filters.required_from:
                date_query["$gte"] = filters.required_from
            if filters.required_to:
                date_query["$lte"] = filters.required_to
            query["required_date"] = date_query
        
        if filters.min_price or filters.max_price:
            price_query = {}
            if filters.min_price:
                price_query["$gte"] = filters.min_price
            if filters.max_price:
                price_query["$lte"] = filters.max_price
            query["total_price"] = price_query
        
        return query
    
    def _doc_to_purchase_item_out(self, doc: Dict[str, Any], item_id: ObjectId) -> PurchaseItemOut:
        return PurchaseItemOut(
            item_id=str(item_id),
            name=doc["name"],
            description=doc.get("description"),
            quantity=doc["quantity"],
            unit_price=doc.get("unit_price"),
            total_price=doc.get("total_price"),
            category=doc["category"],
            priority=doc["priority"],
            status=doc["status"],
            notes=doc.get("notes"),
            supplier=doc.get("supplier"),
            budget_code=doc.get("budget_code"),
            required_date=doc.get("required_date"),
            created_by=doc["created_by"],
            created_at=doc["created_at"],
            updated_at=doc["updated_at"]
        )


purchase_item_service = PurchaseItemService()


def create_purchase_item(data: PurchaseItemCreate, current_user: dict) -> PurchaseItemOut:
    return purchase_item_service.create_purchase_item(data, current_user)


def get_purchase_items(
    item_id: Optional[str] = None,
    limit: int = 20,
    offset: int = 0,
    current_user: Optional[dict] = None,
) -> List[PurchaseItemOut]:
    if item_id:
        return [purchase_item_service.get_purchase_item_by_id(item_id, current_user)]
    return purchase_item_service.get_purchase_items(limit=limit, offset=offset, current_user=current_user)


def update_purchase_item(
    item_id: str, update_data: PurchaseItemUpdate, current_user: dict
) -> PurchaseItemOut:
    return purchase_item_service.update_purchase_item(item_id, update_data, current_user)


def delete_purchase_item(item_id: str, current_user: dict) -> dict:
    return purchase_item_service.delete_purchase_item(item_id, current_user)