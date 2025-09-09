from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Body, Depends, HTTPException, Query, Path, status
from models.checklist import ChecklistCreate, ChecklistOut, ChecklistUpdate
from services.checklist import create_checklist, update_checklist, get_checklist, delete_checklist
from services.auth import get_current_user, require_roles
from utils.error_handler import exception_handler

router = APIRouter(prefix="/checklists", tags=["checklists"])


@exception_handler
@router.post("/", response_model=ChecklistOut, status_code=status.HTTP_201_CREATED)
async def create_new_checklist(
        data: ChecklistCreate = Body(...),
        current_user: dict = Depends(require_roles("manager", "admin1", "admin2"))
):
    return create_checklist(data, current_user)


@exception_handler
@router.get("/", response_model=List[ChecklistOut])
async def list_checklists(
        task_id: Optional[str] = Query(None),
        title: Optional[str] = Query(None),
        description: Optional[str] = Query(None),
        limit: int = Query(20, ge=1, le=100),
        offset: int = Query(0, ge=0),
        current_user: dict = Depends(get_current_user)
):
    return get_checklist(
        task_id=task_id,
        title=title,
        description=description,
        limit=limit,
        offset=offset,
        current_user=current_user,
    )


@exception_handler
@router.put("/{checklist_id}", response_model=ChecklistOut)
async def update_existing_checklist(
        checklist_id: str = Path(..., description="checklist id"),
        update_data: ChecklistUpdate = Body(...),
        current_user: dict = Depends(get_current_user)
):
    return update_checklist(checklist_id, update_data, current_user)


@exception_handler
@router.delete("/{checklist_id}", response_model=Dict[str, Any])
async def delete_existing_checklist(
        checklist_id: str = Path(..., description="checklist id"),
        current_user: dict = Depends(get_current_user)
):
    return delete_checklist(checklist_id, current_user)