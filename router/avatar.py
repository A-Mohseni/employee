from fastapi import APIRouter, Depends, HTTPException, status, Path, UploadFile, File
from models.avatar import avatarOut
from services.avatar import upload_avatar, get_avatar, delete_avatar, delete_my_avatar as delete_my_avatar_service
from services.auth import get_current_user


router = APIRouter(prefix="/avatar", tags=["avatar"])


@router.post("/me", response_model=avatarOut, status_code=status.HTTP_201_CREATED)
async def upload_user_avatar(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
):
    try:
        return await upload_avatar(file, current_user)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/{user_id}", response_model=avatarOut)
async def get_user_avatar(
    user_id: str = Path(..., description="User ID"),
    current_user: dict = Depends(get_current_user),
):
    try:
        resolved_id = str(current_user.get("user_id")) if user_id.lower() in {"me", "string"} else user_id
        return get_avatar(resolved_id, current_user)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.delete("/{user_id}", status_code=status.HTTP_200_OK)
async def delete_user_avatar(
    user_id: str = Path(..., description="User ID"),
    current_user: dict = Depends(get_current_user),
):
    try:
        # If placeholder or 'me', route to dedicated self-delete to avoid permission issues
        if user_id.lower() in {"me", "string"}:
            return delete_my_avatar_service(current_user)
        return delete_avatar(user_id, current_user)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.delete("/me", status_code=status.HTTP_200_OK)
async def delete_my_avatar_route(
    current_user: dict = Depends(get_current_user),
):
    try:
        return delete_my_avatar_service(current_user)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/me", response_model=avatarOut)
async def get_my_avatar(
    current_user: dict = Depends(get_current_user),
):
    try:
        return get_avatar(str(current_user.get("user_id")), current_user)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))