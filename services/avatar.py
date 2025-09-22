from fastapi import HTTPException, UploadFile, status
from bson import ObjectId
from typing import Dict
from models.avatar import avatarOut
from utils.db import get_db
import os
import uuid

upload_dir = "./uploads/avatars"

if not os.path.exists(upload_dir):
    os.makedirs(upload_dir)
    
try:
    # Ensure unique avatar per user
    _db = get_db()
    _db["avatar"].create_index("user_id", unique=True)
except Exception:
    # Index creation should not block app startup
    pass


async def upload_avatar(file: UploadFile, current_user: Dict) -> avatarOut:
    user_id = str(current_user.get("user_id"))
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    content_type = (file.content_type or "").lower()
    allowed_types = {"image/jpeg", "image/jpg", "image/png", "image/*"}

    # Read content first to allow type sniffing when needed
    content = await file.read()

    # Determine extension: prefer filename ext, else infer from content-type, else sniff
    filename = file.filename or ""
    file_extension = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    ct_to_ext = {"image/jpeg": "jpg", "image/jpg": "jpg", "image/png": "png", "image/*": ""}
    if not file_extension and content_type in ct_to_ext:
        file_extension = ct_to_ext.get(content_type, "")

    # If content-type isn't explicitly allowed or extension unresolved, sniff bytes
    def _is_png(data: bytes) -> bool:
        return len(data) >= 8 and data[:8] == b"\x89PNG\r\n\x1a\n"

    def _is_jpeg(data: bytes) -> bool:
        return len(data) >= 2 and data[0:2] == b"\xff\xd8"

    if content_type not in {"image/jpeg", "image/jpg", "image/png"} or not file_extension:
        if _is_png(content):
            content_type = "image/png"
            file_extension = "png"
        elif _is_jpeg(content):
            content_type = "image/jpeg"
            file_extension = "jpg"
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only JPEG and PNG are allowed")

    if not file_extension:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Could not determine file extension from upload")

    file_name = f"{uuid.uuid4()}.{file_extension}"
    file_path = os.path.join(upload_dir, file_name)

    try:
        with open(file_path, "wb") as buffer:
            buffer.write(content)

        database = get_db()
        collection = database["avatar"]

        # Determine ObjectId form if possible
        user_oid = None
        try:
            user_oid = ObjectId(user_id)
        except Exception:
            user_oid = None

        # Find existing avatar by either ObjectId or string user_id
        if user_oid is not None:
            existing_avatar = collection.find_one({"$or": [{"user_id": user_oid}, {"user_id_str": user_id}]})
        else:
            existing_avatar = collection.find_one({"user_id_str": user_id})
        if existing_avatar and os.path.exists(existing_avatar.get("avatar_url", "")):
            try:
                os.remove(existing_avatar["avatar_url"])
            except Exception:
                pass

        # Fetch user info to store alongside avatar
        employees = database["employees"]
        admins = database["admins"]
        user_doc = None
        if user_oid is not None:
            user_doc = employees.find_one({"_id": user_oid}) or admins.find_one({"_id": user_oid})

        # Build new data to set/update
        data_to_set = {
            "user_id_str": user_id,
            "avatar_url": file_path,
            "user_info": {
                "id": user_oid if user_oid is not None else None,
                "employee_id": user_doc.get("employee_id") if user_doc else None,
                "full_name": user_doc.get("full_name") if user_doc else None,
                "role": user_doc.get("role") if user_doc else None,
                "status": user_doc.get("status") if user_doc else None,
                "phone": user_doc.get("phone") if user_doc else None,
                "email": user_doc.get("email") if user_doc else None,
            },
        }
        if user_oid is not None:
            data_to_set["user_id"] = user_oid

        if existing_avatar:
            # Update existing doc without altering _id
            collection.update_one({"_id": existing_avatar["_id"]}, {"$set": data_to_set})
            doc_id = existing_avatar["_id"]
            effective_user_id = existing_avatar.get("user_id", user_oid) or existing_avatar.get("user_id_str", user_id)
        else:
            # Insert new doc with new _id
            new_doc = {"_id": ObjectId(), **data_to_set}
            collection.insert_one(new_doc)
            doc_id = new_doc["_id"]
            effective_user_id = new_doc.get("user_id", user_oid) or new_doc.get("user_id_str", user_id)

        return avatarOut(id=str(doc_id), user_id=str(effective_user_id), avatar_url=data_to_set["avatar_url"])
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to upload avatar: {str(e)}")


def get_avatar(user_id: str, current_user: Dict) -> avatarOut:
    database = get_db()
    collection = database["avatar"]
    # Try by ObjectId first, fallback to string field
    found_avatar = None
    try:
        user_oid = ObjectId(user_id)
        found_avatar = collection.find_one({"user_id": user_oid})
    except Exception:
        found_avatar = collection.find_one({"user_id_str": user_id})
    if not found_avatar:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Avatar not found")
    if str(current_user.get("user_id")) != user_id and current_user.get("role") not in ["admin1", "admin2"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can only get your own avatar")
    return avatarOut(id=str(found_avatar["_id"]), user_id=str(found_avatar["user_id"]), avatar_url=found_avatar["avatar_url"])


def delete_avatar(user_id: str, current_user: Dict) -> Dict[str, str]:
    if str(current_user.get("user_id")) != user_id and current_user.get("role") not in ["admin1", "admin2"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can only delete your own avatar")

    database = get_db()
    collection = database["avatar"]
    # Try by ObjectId first, fallback to string field
    found_avatar = None
    try:
        user_oid = ObjectId(user_id)
        found_avatar = collection.find_one({"user_id": user_oid})
    except Exception:
        found_avatar = collection.find_one({"user_id_str": user_id})
    if not found_avatar:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Avatar not found")

    try:
        avatar_path = found_avatar.get("avatar_url", "")
        if avatar_path and os.path.exists(avatar_path):
            os.remove(avatar_path)
        if "_id" in found_avatar:
            collection.delete_one({"_id": found_avatar["_id"]})
        else:
            collection.delete_one({"user_id_str": user_id})
        return {"message": "Avatar deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


def delete_my_avatar(current_user: Dict) -> Dict[str, str]:
    user_id = str(current_user.get("user_id"))
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

    database = get_db()
    collection = database["avatar"]

    # Try by ObjectId first, fallback to string
    found_avatar = None
    try:
        user_oid = ObjectId(user_id)
        found_avatar = collection.find_one({"$or": [{"user_id": user_oid}, {"user_id_str": user_id}]})
    except Exception:
        found_avatar = collection.find_one({"user_id_str": user_id})

    if not found_avatar:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Avatar not found")

    try:
        avatar_path = found_avatar.get("avatar_url", "")
        if avatar_path and os.path.exists(avatar_path):
            os.remove(avatar_path)
        collection.delete_one({"_id": found_avatar["_id"]})
        return {"message": "Avatar deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
