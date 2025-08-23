import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import APIRouter, Body, Depends, HTTPException, Query, Path
from starlette import status
from starlette.status import HTTP_201_CREATED
from models.leave_request import LeaveRequestCreate, LeaveRequestUpdate, LeaveRequestOut
from services.leave_request import (
    create_leave_request,
    update_leave_request,
    delete_leave_request,
    get_leave_requests
)
from services.auth import get_current_user
from typing import Optional

router = APIRouter(prefix="/leave_request", tags=["leave_request"])


@router.post("/", response_model=LeaveRequestOut, status_code=status.HTTP_201_CREATED)
async def create_new_leave_request(
    data: LeaveRequestCreate = Body(...),
    current_user: dict = Depends(get_current_user)
):
    try:
        item = create_leave_request(data, current_user)
        return item
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/", response_model=list[LeaveRequestOut])
async def list_leave_requests(
    user_id: Optional[str] = Query(None),
    current_user: dict = Depends(get_current_user),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    try:
        result = get_leave_requests(
            user_id=user_id,
            limit=limit,
            offset=offset,
            current_user=current_user
        )
        return result
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.put("/{request_id}", response_model=LeaveRequestOut)
async def update_existing_leave_request(
    request_id: str = Path(...),
    update_data: LeaveRequestUpdate = Body(...),
    current_user: dict = Depends(get_current_user)
):
    try:
        update = update_leave_request(request_id, update_data, current_user)
        return update
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.delete("/{request_id}", status_code=status.HTTP_200_OK)
async def delete_existing_leave_request(
    request_id: str = Path(...),
    current_user: dict = Depends(get_current_user)
):
    try:
        delete = delete_leave_request(request_id, current_user)
        return delete
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

