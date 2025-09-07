from datetime import datetime, timedelta
from typing import Optional
import hashlib
from utils.db import get_db
from services.log import service_exception, logger


@service_exception
def create_token(user_id: str, token: str, expires_in_minutes: int = 30) -> bool:
    try:
        db = get_db()
        tokens_collection = db.tokens
        
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        
        expires_at = datetime.utcnow() + timedelta(minutes=expires_in_minutes)
        
        token_doc = {
            "user_id": user_id,
            "token_hash": token_hash,
            "expires_at": expires_at,
            "is_active": True,
            "created_at": datetime.utcnow()
        }
        
        result = tokens_collection.insert_one(token_doc)
        return result.inserted_id is not None
        
    except Exception as e:
        logger.exception("Error creating token: %s", e)
        return False


@service_exception
def verify_stored_token(token: str, user_id: str) -> bool:
    try:
        db = get_db()
        tokens_collection = db.tokens
        
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        
        token_doc = tokens_collection.find_one({
            "user_id": user_id,
            "token_hash": token_hash,
            "is_active": True,
            "expires_at": {"$gt": datetime.utcnow()}
        })
        
        return token_doc is not None
        
    except Exception as e:
        logger.exception("Error verifying token: %s", e)
        return False


@service_exception
def deactivate_token(token: str, user_id: str) -> bool:
    try:
        db = get_db()
        tokens_collection = db.tokens
        
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        
        result = tokens_collection.update_one(
            {
                "user_id": user_id,
                "token_hash": token_hash,
                "is_active": True
            },
            {
                "$set": {"is_active": False}
            }
        )
        
        return result.modified_count > 0
        
    except Exception as e:
        logger.exception("Error deactivating token: %s", e)
        return False


@service_exception
def cleanup_expired_tokens() -> int:
    try:
        db = get_db()
        tokens_collection = db.tokens
        
        result = tokens_collection.delete_many({
            "expires_at": {"$lt": datetime.utcnow()}
        })
        
        return result.deleted_count
        
    except Exception as e:
        logger.exception("Error cleaning up expired tokens: %s", e)
        return 0
