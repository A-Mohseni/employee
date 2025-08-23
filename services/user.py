import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pymongo import errors
from datetime import datetime
from bson import ObjectId
from fastapi import HTTPException, status
from models.user import user_create, user_out, user_update, PyObjectId
from utils.db import get_db
from typing import List


def create_user(user: user_create, current_user: dict):
    if current_user["role"] != "manager":
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
    
    user_collection = db["user"]

    if user_collection.find_one({"phone_number": user.phone_number}):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Phone number is already registered",
        )

    now = datetime.now()
    user_data = {
        "_id": ObjectId(),
        "phone_number": user.phone_number,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "tokens": [],
        "role": user.role,
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

    return user_out(
        user_id=user_data["_id"],
        first_name=user_data["first_name"],
        last_name=user_data["last_name"],
        phone_number=user_data["phone_number"],
        tokens=user_data["tokens"],
        role=user_data["role"],
        created_at=user_data["created_at"],
        updated_at=user_data["updated_at"],
    )


def get_all_users(current_user: dict) -> List[user_out]:
    """
    Get all users from the database
    Only managers can access this endpoint
    """
    if current_user["role"] != "manager":
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
    
    user_collection = db["user"]
    
    try:
        users = list(user_collection.find())
        return [
            user_out(
                user_id=user["_id"],
                first_name=user["first_name"],
                last_name=user["last_name"],
                phone_number=user["phone_number"],
                tokens=user["tokens"],
                role=user["role"],
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
    if current_user["role"] != "manager":
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
    
    user_collection = db["user"]
    result = user_collection.delete_one({"_id": ObjectId(user_id)})
    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return {"message": "user deleted"}


def update_user(user_id: str, user_data: user_update, current_user: dict):
    if current_user["role"] != "manager":
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
    
    user_collection = db["user"]

    result = user_collection.find_one({"_id": ObjectId(user_id)})
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    update_fields = {"updated_at": datetime.now()}

    if user_data.first_name is not None:
        update_fields["first_name"] = user_data.first_name
    if user_data.last_name is not None:
        update_fields["last_name"] = user_data.last_name
    if user_data.phone_number is not None:
        update_fields["phone_number"] = user_data.phone_number
    if user_data.tokens is not None:
        update_fields["tokens"] = user_data.tokens
    if user_data.role is not None:
        update_fields["role"] = user_data.role
    if user_data.password_hash is not None:
        update_fields["password_hash"] = user_data.password_hash

    user_collection.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": update_fields}
    )

    updated_user = user_collection.find_one({"_id": ObjectId(user_id)})
    return user_out(
        user_id=updated_user["_id"],
        first_name=updated_user["first_name"],
        last_name=updated_user["last_name"],
        phone_number=updated_user["phone_number"],
        tokens=updated_user["tokens"],
        role=updated_user["role"],
        created_at=updated_user["created_at"],
        updated_at=updated_user["updated_at"],
    )
