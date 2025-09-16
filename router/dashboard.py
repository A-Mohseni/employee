from fastapi import APIRouter,Depends,HTTPException, status
from models.dashboard import DashboardStats
from services.dashboard import get_dashboard
from services.auth import get_current_user

router=APIRouter(prefix="/dashboard",tags=["dashboard"])

@router.get("/",response_model=DashboardStats)
def get_dashboard_endpoint(current_user:dict=Depends(get_current_user)):
    try:
        return get_dashboard(current_user)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=str(e))
