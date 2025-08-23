import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import Optional
from fastapi import APIRouter, Body, Depends, HTTPException, Query, Path, status
from models.purchase_item import PurchaseItemCreate, PurchaseItemOut, PurchaseItemUpdate
from services.purchase_item import (
    create_purchase_item,
    delete_purchase_item,
    update_purchase_item,
    get_purchase_items,
)
from services.auth import get_current_user

router = APIRouter(prefix="/purchase-items", tags=["purchase-items"])

@router.post("/", response_model=PurchaseItemOut, status_code=status.HTTP_201_CREATED)
def create_new_purchase_items(
    data: PurchaseItemCreate = Body(...),
    current_user: dict = Depends(get_current_user)
):
    try:
        return create_purchase_item(data, current_user)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/{item_id}", response_model=PurchaseItemOut)
async def get_single_purchase_item(
    item_id: str = Path(...),
    current_user: dict = Depends(get_current_user),
):
    try:
        items = get_purchase_items(item_id=item_id, limit=1, offset=0, current_user=current_user)
        if not items:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item Not Found")
        return items[0]
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.put("/{item_id}", response_model=PurchaseItemOut)
async def update_existing_purchase_item(
    item_id: str = Path(...),
    update_data: PurchaseItemUpdate = Body(...),
    current_user: dict = Depends(get_current_user)
):
    try:
        updated = update_purchase_item(item_id=item_id, update_data=update_data, current_user=current_user)
        return updated
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.delete("/{item_id}", response_model=dict)
async def delete_existing_purchase_item(
    item_id: str = Path(...),
    current_user: dict = Depends(get_current_user)
):
    try:
        result = delete_purchase_item(item_id=item_id, current_user=current_user)
        return result
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )                 

