import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import APIRouter, Depends, HTTPException, status, Body, Path
from starlette.status import HTTP_201_CREATED
from models.user import employee_create, employee_out, employee_out_with_password, employee_out_with_token, employee_update
from services.user import create_user, update_user, delete_user, get_all_users
from services.auth import require_roles
from typing import List
from utils.error_handler import exception_handler

router = APIRouter(prefix="/employees", tags=["employees"])


@router.post("/first-admin", response_model=employee_out_with_token, status_code=status.HTTP_201_CREATED)
def create_first_admin(user: employee_create):
    try:
        from utils.db import get_db
        db = get_db()
        user_collection = db["employees"]
        existing_admin = user_collection.find_one({"role": "admin1"})
        if existing_admin:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Admin user already exists. Use regular create endpoint with authentication.")
        mock_admin = {"role": "admin1", "user_id": "initial_setup"}
        return create_user(user, mock_admin, return_token=True)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error creating first admin: {str(e)}")


@router.get("/", response_model=List[employee_out_with_password], status_code=status.HTTP_200_OK)
def get_users(current_user: dict = Depends(require_roles("admin1"))):
    try:
        return get_all_users(current_user)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error retrieving users: {str(e)}")


@router.get("/list", response_model=List[employee_out_with_password], status_code=status.HTTP_200_OK)
def get_users_public():
    try:
        mock_admin = {"role": "admin1", "user_id": "test"}
        return get_all_users(mock_admin)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error retrieving users: {str(e)}")


@router.post("/", response_model=employee_out_with_token, status_code=status.HTTP_201_CREATED)
def create_new_user(user: employee_create, current_user: dict = Depends(require_roles("admin1", "admin2"))):
    try:
        return create_user(user, current_user, return_token=True)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error creating user: {str(e)}")


@router.put("/{user_id}", response_model=employee_out_with_password, status_code=status.HTTP_200_OK)
def update_existing_user(
    user_id: str = Path(...),
    user_data: employee_update = Body(...),
    current_user: dict = Depends(require_roles("admin1"))
):
    try:
        return update_user(user_id, user_data, current_user)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error updating user: {str(e)}")


@router.delete("/{user_id}", status_code=status.HTTP_200_OK)
def delete_existing_user(
    user_id: str = Path(...),
    current_user: dict = Depends(require_roles("admin1"))
):
    try:
        return delete_user(user_id, current_user)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error deleting user: {str(e)}")
