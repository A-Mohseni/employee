from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional

from models.log import logOut, logCreate
from services.log import get_logs, create_log
from services.auth import require_roles

router = APIRouter(prefix="/logs", tags=["logs"])

@router.get("/", response_model=List[logOut])
def list_logs(
    limit: int = Query(20, ge=1),
    offset: int = Query(0, ge=0),
    recent_hours: Optional[int] = Query(None, description="Filter logs in recent hours"),
    current_user: dict = Depends(require_roles("manager_men", "manager_women", "admin1", "admin2")),
):
    try:
        return get_logs(current_user, limit, offset, recent_hours)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )

@router.post("/", response_model=logOut, status_code=status.HTTP_201_CREATED)
def create_log_endpoint(
    payload: logCreate,
    current_user: dict = Depends(require_roles("manager_men", "manager_women", "admin1", "admin2")),
):
    try:
        return create_log(payload, current_user)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )

