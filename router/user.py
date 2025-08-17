from fastapi import APIRouter, Depends, HTTPException, status, Body, Path
from starlette.status import HTTP_200_OK
from models.user import user_create, user_out, user_update
from services.user import create_user, update_user, delete_user, get_all_users
from services.auth import get_current_user
from typing import List

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/", response_model=List[user_out], status_code=status.HTTP_200_OK)
def get_users(current_user: dict = Depends(get_current_user)):
    """
    Get all users from the database
    Only managers can access this endpoint
    """
    try:
        return get_all_users(current_user)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving users: {str(e)}",
        )


@router.post("/", response_model=user_out, status_code=status.HTTP_201_CREATED)
def create_new_user(user: user_create, current_user: dict = Depends(get_current_user)):
    try:
        return create_user(user, current_user)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating user: {str(e)}",
        )


@router.put("/{user_id}", response_model=user_out, status_code=HTTP_200_OK)
def update_existing_user(
    user_id: str = Path(..., description="user_id for edit", example="507f1f77bcf86cd799439011"),
    update_data: user_update = Body(..., description="New data to update (names only)"),
    current_user: dict = Depends(get_current_user),
):
    try:
        return update_user(user_id, update_data, current_user)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error editing user: {str(e)}",
        )


@router.delete("/{user_id}", response_model=user_out, status_code=status.HTTP_200_OK)
def deleting_user(
    user_id: str = Path(..., description="user_id for delete", example="507f1f77bcf86cd799439011"),
    current_user: dict = Depends(get_current_user),
): 
    try:
        return delete_user(user_id, current_user)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting user: {str(e)}"
        )
