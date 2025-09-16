import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import APIRouter, Body, Depends, HTTPException, Query, Path, status
from typing import Optional, Dict, Any, List
from datetime import datetime

from utils.error_handler import exception_handler
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
from services.purchase_item import (
    create_purchase_item,
    delete_purchase_item,
    update_purchase_item,
    get_purchase_items,
    purchase_item_service
)
from services.auth import require_roles

router = APIRouter(
    prefix="/purchase-items",
    tags=["Purchase Items"],
    responses={
        404: {"description": "Item not found"},
        400: {"description": "Invalid request"},
        500: {"description": "Server error"}
    }
)


@exception_handler
@router.post(
    "/",
    response_model=PurchaseItemOut,
    status_code=status.HTTP_201_CREATED,
    summary="Create new purchase item",
    description="Create a new purchase item with all required information"
)
async def create_new_purchase_item(
    data: PurchaseItemCreate = Body(..., description="Purchase item information"),
    current_user: dict = Depends(require_roles("admin1", "admin2"))
):
    try:
        return create_purchase_item(data, current_user)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Error creating purchase item: {str(e)}"
        )


@exception_handler
@router.get(
    "/{item_id}",
    response_model=PurchaseItemOut,
    summary="Get purchase item",
    description="Get purchase item information by ID"
)
async def get_single_purchase_item(
    item_id: str = Path(..., description="Purchase item ID"),
    current_user: dict = Depends(require_roles("admin1", "admin2"))
):
    try:
        return purchase_item_service.get_purchase_item_by_id(item_id, current_user)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting purchase item: {str(e)}"
        )


@exception_handler
@router.get(
    "/",
    response_model=List[PurchaseItemOut],
    summary="List purchase items",
    description="Get list of purchase items with filtering and sorting options"
)
async def list_purchase_items(
    limit: int = Query(20, ge=1, le=200, description="Number of items per page"),
    offset: int = Query(0, ge=0, description="Number of items to skip"),
    
    sort_by: str = Query("created_at", description="Sort field"),
    sort_order: str = Query("desc", description="Sort order (asc/desc)"),
    
    name: Optional[str] = Query(None, description="Search in item name"),
    category: Optional[PurchaseCategory] = Query(None, description="Filter by category"),
    priority: Optional[PriorityLevel] = Query(None, description="Filter by priority"),
    status: Optional[PurchaseStatus] = Query(None, description="Filter by status"),
    
    supplier: Optional[str] = Query(None, description="Filter by supplier"),
    budget_code: Optional[str] = Query(None, description="Filter by budget code"),
    created_by: Optional[str] = Query(None, description="Filter by creator"),
    
    created_from: Optional[datetime] = Query(None, description="Created from date"),
    created_to: Optional[datetime] = Query(None, description="Created to date"),
    required_from: Optional[datetime] = Query(None, description="Required from date"),
    required_to: Optional[datetime] = Query(None, description="Required to date"),
    
    min_price: Optional[float] = Query(None, ge=0, description="Minimum price"),
    max_price: Optional[float] = Query(None, ge=0, description="Maximum price"),
    
    current_user: dict = Depends(require_roles("admin1", "admin2"))
):
    try:
        filters = PurchaseItemFilter(
            name=name,
            category=category,
            priority=priority,
            status=status,
            supplier=supplier,
            budget_code=budget_code,
            created_by=created_by,
            created_from=created_from,
            created_to=created_to,
            required_from=required_from,
            required_to=required_to,
            min_price=min_price,
            max_price=max_price
        )
        
        return purchase_item_service.get_purchase_items(
            filters=filters,
            limit=limit,
            offset=offset,
            sort_by=sort_by,
            sort_order=sort_order,
            current_user=current_user
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting purchase items: {str(e)}"
        )


@exception_handler
@router.put(
    "/{item_id}",
    response_model=PurchaseItemOut,
    summary="Update purchase item",
    description="Update existing purchase item information"
)
async def update_existing_purchase_item(
    item_id: str = Path(..., description="Purchase item ID"),
    update_data: PurchaseItemUpdate = Body(..., description="Update information"),
    current_user: dict = Depends(require_roles("admin1", "admin2"))
):
    try:
        return update_purchase_item(item_id=item_id, update_data=update_data, current_user=current_user)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating purchase item: {str(e)}"
        )


@exception_handler
@router.delete(
    "/{item_id}",
    response_model=Dict[str, Any],
    summary="Delete purchase item",
    description="Delete a purchase item from the system"
)
async def delete_existing_purchase_item(
    item_id: str = Path(..., description="Purchase item ID"),
    current_user: dict = Depends(require_roles("admin1", "admin2"))
):
    try:
        return delete_purchase_item(item_id=item_id, current_user=current_user)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting purchase item: {str(e)}"
        )


@exception_handler
@router.get(
    "/summary/stats",
    response_model=PurchaseItemSummary,
    summary="Purchase summary statistics",
    description="Get overall statistics and summary of purchase items"
)
async def get_purchase_summary(
    current_user: dict = Depends(require_roles("admin1", "admin2"))
):
    try:
        return purchase_item_service.get_purchase_summary(current_user)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting summary statistics: {str(e)}"
        )


@exception_handler
@router.get(
    "/categories/list",
    response_model=List[str],
    summary="List categories",
    description="Get list of all available categories"
)
async def get_categories_list(
    current_user: dict = Depends(require_roles("admin1", "admin2"))
):
    try:
        return [category.value for category in PurchaseCategory]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting categories list: {str(e)}"
        )


@exception_handler
@router.get(
    "/priorities/list",
    response_model=List[str],
    summary="List priorities",
    description="Get list of all available priorities"
)
async def get_priorities_list(
    current_user: dict = Depends(require_roles("admin1", "admin2"))
):
    try:
        return [priority.value for priority in PriorityLevel]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting priorities list: {str(e)}"
        )


@exception_handler
@router.get(
    "/statuses/list",
    response_model=List[str],
    summary="List statuses",
    description="Get list of all available statuses"
)
async def get_statuses_list(
    current_user: dict = Depends(require_roles("admin1", "admin2"))
):
    try:
        return [status.value for status in PurchaseStatus]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting statuses list: {str(e)}"
        )