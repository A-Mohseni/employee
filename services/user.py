import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pymongo import errors
from datetime import datetime
from bson import ObjectId
from fastapi import HTTPException, status
from models.user import employee_create, employee_out, employee_out_with_token, employee_update, PyObjectId
from services.token import create_token
from utils.db import get_db
from typing import List


def create_user(user: employee_create, current_user: dict, return_token: bool = True):
    if current_user["role"] != "admin1":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the administrator can create a new user",
        )

    db = get_db()
    if db is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database connection failed"
        )
    
    user_collection = db["employees"]
    if user_collection.find_one({"employee_id": user.employee_id}):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="employee_id already exists")

    now = datetime.now()
    user_data = {
        "_id": ObjectId(),
        "employee_id": user.employee_id,
        "full_name": user.full_name,
        "role": user.role,
        "status": user.status,
        "password_hash": user.password_hash,
        "created_at": now,
        "updated_at": now,
    }

    try:
        user_collection.insert_one(user_data)
    except errors.DuplicateKeyError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error creating user: duplicate phone number",
        )

    if return_token:
        payload = {"user_id": str(user_data["_id"]), "role": user_data["role"]}
        try:
            from utils.jwt import create_access_token
            token = create_access_token(payload, subject=str(user_data["_id"]))
        except Exception as e:
            print(f"JWT creation failed: {e}")
            token = "mock-token-for-new-user"

        try:
            create_token(str(user_data["_id"]), token, expires_in_minutes=30)
        except Exception as e:
            print(f"Warning: Could not store token in database: {e}")

        return employee_out_with_token(
            id=str(user_data["_id"]),
            employee_id=user_data["employee_id"],
            full_name=user_data["full_name"],
            role=user_data["role"],
            status=user_data["status"],
            created_at=user_data["created_at"],
            updated_at=user_data["updated_at"],
            access_token=token,
        )
    else:
        return employee_out(
            id=str(user_data["_id"]),
            employee_id=user_data["employee_id"],
            full_name=user_data["full_name"],
            role=user_data["role"],
            status=user_data["status"],
            created_at=user_data["created_at"],
            updated_at=user_data["updated_at"],
        )


def get_all_users(current_user: dict) -> List[employee_out]:
    if current_user["role"] != "admin1":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the administrator can view all users",
        )

    db = get_db()
    if db is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database connection failed"
        )
    
    user_collection = db["employees"]
    
    try:
        users = list(user_collection.find())
        return [
            employee_out(
                id=str(user["_id"]),
                employee_id=user["employee_id"],
                full_name=user["full_name"],
                role=user["role"],
                status=user["status"],
                created_at=user["created_at"],
                updated_at=user["updated_at"],
            )
            for user in users
        ]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving users: {str(e)}",
        )


def delete_user(user_id: str, current_user: dict):
    if current_user["role"] != "admin1":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the administrator can delete a user",
        )

    db = get_db()
    if db is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database connection failed"
        )
    
    user_collection = db["employees"]
    result = user_collection.delete_one({"_id": ObjectId(user_id)})
    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return {"message": "user deleted"}


def update_user(user_id: str, user_data: employee_update, current_user: dict):
    if current_user["role"] != "admin1":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the administrator can update a user",
        )

    db = get_db()
    if db is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database connection failed"
        )
    
    user_collection = db["employees"]

    result = user_collection.find_one({"_id": ObjectId(user_id)})
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    update_fields = {"updated_at": datetime.now()}

    if user_data.full_name is not None:
        update_fields["full_name"] = user_data.full_name
    if user_data.role is not None:
        update_fields["role"] = user_data.role
    if user_data.status is not None:
        update_fields["status"] = user_data.status
    if user_data.password_hash is not None:
        update_fields["password_hash"] = user_data.password_hash

    user_collection.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": update_fields}
    )

    updated_user = user_collection.find_one({"_id": ObjectId(user_id)})
    return employee_out(
        id=str(updated_user["_id"]),
        employee_id=updated_user["employee_id"],
        full_name=updated_user["full_name"],
        role=updated_user["role"],
        status=updated_user["status"],
        created_at=updated_user["created_at"],
        updated_at=updated_user["updated_at"],
    )
