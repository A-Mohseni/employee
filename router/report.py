import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import APIRouter, Body, Depends, HTTPException, status, Path, Query
from typing import List, Optional

from models.report import report_create, report_update, report_out
from services.report import (
    create_report, get_reports, update_report, delete_report, approve_report
)
from services.auth import get_current_user, require_roles

router = APIRouter(prefix="/reports", tags=["reports"])
from utils.error_handler import exception_handler


@router.post("/", response_model=report_out, status_code=status.HTTP_201_CREATED)
async def create_new_report(
    data: report_create = Body(...),
    current_user: dict = Depends(get_current_user)
):
    try:
        return create_report(data, current_user)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e) or "Internal Server Error")


@router.get("/", response_model=List[report_out])
async def list_reports(
    user_id: Optional[str] = Query(None),
    report_status: Optional[str] = Query(None),
    limit: int = Query(20, ge=1),
    offset: int = Query(0, ge=0),
    current_user: dict = Depends(get_current_user)
):
    try:
        return get_reports(user_id, report_status, limit, offset, current_user)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e) or "Internal Server Error")


@router.put("/{report_id}", response_model=report_out)
async def update_existing_report(
    report_id: str = Path(...),
    update_data: report_update = Body(...),
    current_user: dict = Depends(get_current_user)
):
    try:
        return update_report(report_id, update_data, current_user)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e) or "Internal Server Error")


@router.delete("/{report_id}", status_code=status.HTTP_200_OK)
async def delete_existing_report(
    report_id: str = Path(...),
    current_user: dict = Depends(get_current_user)
):
    try:
        return delete_report(report_id, current_user)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e) or "Internal Server Error")


@router.post("/{report_id}/approve", response_model=report_out)
async def approve_existing_report(
    report_id: str = Path(...),
    current_user: dict = Depends(require_roles("manager_women", "manager_men", "admin1", "admin2"))
):
    try:
        return approve_report(report_id, current_user)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e) or "Internal Server Error")


