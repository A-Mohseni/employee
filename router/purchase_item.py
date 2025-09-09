import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import APIRouter, Body, Depends, HTTPException, Query, Path, status
from typing import Optional, Dict, Any, List
from utils.error_handler import exception_handler
from models.purchase_item import PurchaseItemCreate, PurchaseItemOut, PurchaseItemUpdate
from services.purchase_item import (
    create_purchase_item,
    delete_purchase_item,
    update_purchase_item,
    get_purchase_items,
)
from services.auth import require_roles

router = APIRouter(prefix="/purchase-items", tags=["purchase-items"])
from utils.error_handler import exception_handler

@exception_handler
@router.post("/", response_model=PurchaseItemOut, status_code=status.HTTP_201_CREATED)
def create_new_purchase_items(
    data: PurchaseItemCreate = Body(...),
    current_user: dict = Depends(require_roles("admin1", "admin2"))
):
    try:
        return create_purchase_item(data, current_user)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e) or "Internal Server Error")

@exception_handler
@router.get("/{item_id}", response_model=PurchaseItemOut)
async def get_single_purchase_item(
    item_id: str = Path(...),
    current_user: dict = Depends(require_roles("admin1", "admin2")),
):
    try:
        items = get_purchase_items(item_id=item_id, limit=1, offset=0, current_user=current_user)
        if not items:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item Not Found")
        return items[0]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e) or "Internal Server Error")

@exception_handler
@router.get("/", response_model=List[PurchaseItemOut])
async def list_purchase_items(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    current_user: dict = Depends(require_roles("admin1", "admin2")),
):
    try:
        return get_purchase_items(limit=limit, offset=offset, current_user=current_user)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e) or "Internal Server Error")

@exception_handler
@router.put("/{item_id}", response_model=PurchaseItemOut)
async def update_existing_purchase_item(
    item_id: str = Path(...),
    update_data: PurchaseItemUpdate = Body(...),
    current_user: dict = Depends(require_roles("admin1", "admin2"))
):
    try:
        return update_purchase_item(item_id=item_id, update_data=update_data, current_user=current_user)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e) or "Internal Server Error")

@exception_handler
@router.delete("/{item_id}", response_model=Dict[str, Any])
async def delete_existing_purchase_item(
    item_id: str = Path(...),
    current_user: dict = Depends(require_roles("admin1", "admin2"))
):
    try:
        return delete_purchase_item(item_id=item_id, current_user=current_user)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e) or "Internal Server Error")

