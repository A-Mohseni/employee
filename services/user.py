import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pymongo import errors
from datetime import datetime
from bson import ObjectId
from fastapi import HTTPException, status
from models.user import employee_create, employee_out, employee_out_with_password, employee_out_with_token, employee_update, PyObjectId
from services.token import create_token
from utils.db import get_db
from typing import List
from utils.password_hash import hash_password
from services.log import create_log
from models.log import logCreate
from utils.helpers import mask_password


def create_user(user: employee_create, current_user: dict, return_token: bool = True):
    if current_user.get("role") not in ("admin1", "admin2"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin1/admin2 can create a new user",
        )

    db = get_db()
    
    user_collection = db["employees"]
    if user_collection.find_one({"employee_id": user.employee_id}):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="employee_id already exists")

    now = datetime.now()
    allowed_assignable_roles = {"employee", "manager_women", "manager_men"}
    if user.role not in allowed_assignable_roles:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid role. Only employee, manager_women, manager_men are assignable.",
        )
    hashed_password: str | None = None
    if user.password:
        try:
            hashed_password = hash_password(user.password)
        except Exception:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid password provided")
    user_data = {
        "_id": ObjectId(),
        "employee_id": user.employee_id,
        "full_name": user.full_name,
        "role": user.role,
        "status": user.status,
        "password_hash": hashed_password,
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
        result = employee_out(
            id=str(user_data["_id"]),
            employee_id=user_data["employee_id"],
            full_name=user_data["full_name"],
            role=user_data["role"],
            status=user_data["status"],
            created_at=user_data["created_at"],
            updated_at=user_data["updated_at"],
        )
        try:
            if current_user and current_user.get("user_id"):
                create_log(
                    logCreate(
                        action_type="create_user",
                        user_id=current_user["user_id"],
                        description=f"Created user {user_data['employee_id']} - {user_data['full_name']}"
                    ),
                    current_user,
                )
        except Exception:
            pass
        return result


def get_all_users(current_user: dict) -> List[employee_out_with_password]:
    if current_user.get("role") != "admin1":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the administrator can view all users",
        )

    db = get_db()
    
    user_collection = db["employees"]
    
    try:
        users = list(user_collection.find())
        return [
            employee_out_with_password(
                id=str(user["_id"]),
                employee_id=user["employee_id"],
                full_name=user["full_name"],
                role=user["role"],
                status=user["status"],
                password_hash=mask_password(len(user.get("password_hash", ""))),
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
    if current_user.get("role") != "admin1":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the administrator can delete a user",
        )

    db = get_db()
    
    user_collection = db["employees"]
    result = user_collection.delete_one({"_id": ObjectId(user_id)})
    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    try:
        if current_user and current_user.get("user_id"):
            create_log(
                logCreate(
                    action_type="delete_user",
                    user_id=current_user["user_id"],
                    description=f"Deleted user {_id_str if (_id_str := user_id) else user_id}"
                ),
                current_user,
            )
    except Exception:
        pass
    return {"message": "user deleted"}


def update_user(user_id: str, user_data: employee_update, current_user: dict):
    if current_user.get("role") != "admin1":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the administrator can update a user",
        )

    db = get_db()
    
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
    if user_data.password is not None:
        try:
            update_fields["password_hash"] = hash_password(user_data.password)
        except Exception:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid password provided")

    user_collection.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": update_fields}
    )

    updated_user = user_collection.find_one({"_id": ObjectId(user_id)})
    result = employee_out_with_password(
        id=str(updated_user["_id"]),
        employee_id=updated_user["employee_id"],
        full_name=updated_user["full_name"],
        role=updated_user["role"],
        status=updated_user["status"],
        password_hash=mask_password(len(updated_user.get("password_hash", ""))),
        created_at=updated_user["created_at"],
        updated_at=updated_user["updated_at"],
    )
    try:
        if current_user and current_user.get("user_id"):
            create_log(
                logCreate(
                    action_type="update_user",
                    user_id=current_user["user_id"],
                    description=f"Updated user {updated_user['employee_id']} - {updated_user['full_name']}"
                ),
                current_user,
            )
    except Exception:
        pass
    return result
