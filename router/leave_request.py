import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import APIRouter, Body, Depends, HTTPException, Query, Path, status
from models.leave_request import LeaveRequestCreate, LeaveRequestUpdate, LeaveRequestOut
from services.leave_request import (
    create_leave_request,
    update_leave_request,
    delete_leave_request,
    get_leave_requests,
    approve_leave_phase1,
    approve_leave_phase2,
    reject_leave_request,
)
from services.auth import get_current_user, require_roles
from typing import Optional, List

router = APIRouter(prefix="/leave-requests", tags=["leave_requests"])


@router.post("/", response_model=LeaveRequestOut, status_code=status.HTTP_201_CREATED)
async def create_new_leave_request(
    data: LeaveRequestCreate = Body(...),
    current_user: dict = Depends(require_roles("employee"))
):
    try:
        return create_leave_request(data, current_user)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e) or "Internal Server Error")


@router.get("/", response_model=List[LeaveRequestOut])
async def list_leave_requests(
    user_id: Optional[str] = Query(None),
    current_user: dict = Depends(require_roles("employee", "manager_women", "manager_men", "admin1", "admin2")),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    try:
        return get_leave_requests(
            user_id=user_id,
            limit=limit,
            offset=offset,
            current_user=current_user
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e) or "Internal Server Error")


@router.put("/{request_id}", response_model=LeaveRequestOut)
async def update_existing_leave_request(
    request_id: str = Path(...),
    update_data: LeaveRequestUpdate = Body(...),
    current_user: dict = Depends(get_current_user)
):
    try:
        return update_leave_request(request_id, update_data, current_user)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e) or "Internal Server Error")


@router.delete("/{request_id}", status_code=status.HTTP_200_OK)
async def delete_existing_leave_request(
    request_id: str = Path(...),
    current_user: dict = Depends(get_current_user)
):
    try:
        return delete_leave_request(request_id, current_user)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e) or "Internal Server Error")


@router.post("/{request_id}/approve-phase1", response_model=LeaveRequestOut)
async def approve_phase1(request_id: str = Path(...), current_user: dict = Depends(require_roles("manager_women", "manager_men", "admin1", "admin2"))):
    try:
        return approve_leave_phase1(request_id, current_user)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e) or "Internal Server Error")


@router.post("/{request_id}/approve-phase2", response_model=LeaveRequestOut)
async def approve_phase2(request_id: str = Path(...), current_user: dict = Depends(require_roles("manager_women", "manager_men", "admin1", "admin2"))):
    try:
        return approve_leave_phase2(request_id, current_user)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e) or "Internal Server Error")


@router.post("/{request_id}/reject", response_model=LeaveRequestOut)
async def reject_leave(
    request_id: str = Path(...),
    reason: str = Body(None),
    current_user: dict = Depends(require_roles("manager_women", "manager_men", "admin1", "admin2"))
):
    try:
        return reject_leave_request(request_id, current_user, reason)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e) or "Internal Server Error")




