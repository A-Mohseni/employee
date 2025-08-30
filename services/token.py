from datetime import datetime, timedelta
from typing import Optional
import hashlib
from utils.db import get_db


def create_token(user_id: str, token: str, expires_in_minutes: int = 30) -> bool:
    """
    Store a token in the database with hash and expiration
    """
    try:
        db = get_db()
        tokens_collection = db.tokens
        
        # Hash the token for security
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        
        # Calculate expiration time
        expires_at = datetime.utcnow() + timedelta(minutes=expires_in_minutes)
        
        # Create token document
        token_doc = {
            "user_id": user_id,
            "token_hash": token_hash,
            "expires_at": expires_at,
            "is_active": True,
            "created_at": datetime.utcnow()
        }
        
        # Insert into database
        result = tokens_collection.insert_one(token_doc)
        return result.inserted_id is not None
        
    except Exception as e:
        print(f"Error creating token: {e}")
        return False


def verify_stored_token(token: str, user_id: str) -> bool:
    """
    Verify if a token exists in the database and is still valid
    """
    try:
        db = get_db()
        tokens_collection = db.tokens
        
        # Hash the token to compare with stored hash
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        
        # Find token in database
        token_doc = tokens_collection.find_one({
            "user_id": user_id,
            "token_hash": token_hash,
            "is_active": True,
            "expires_at": {"$gt": datetime.utcnow()}
        })
        
        return token_doc is not None
        
    except Exception as e:
        print(f"Error verifying token: {e}")
        return False


def deactivate_token(token: str, user_id: str) -> bool:
    """
    Deactivate a token (mark as inactive) for logout
    """
    try:
        db = get_db()
        tokens_collection = db.tokens
        
        # Hash the token to find it in database
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        
        # Update token to inactive
        result = tokens_collection.update_one(
            {
                "user_id": user_id,
                "token_hash": token_hash,
                "is_active": True
            },
            {
                "$set": {
                    "is_active": False,
                    "deactivated_at": datetime.utcnow()
                }
            }
        )
        
        return result.modified_count > 0
        
    except Exception as e:
        print(f"Error deactivating token: {e}")
        return False


def cleanup_expired_tokens() -> int:
    """
    Clean up expired tokens from the database
    Returns the number of tokens removed
    """
    try:
        db = get_db()
        tokens_collection = db.tokens
        
        # Remove tokens that have expired
        result = tokens_collection.delete_many({
            "expires_at": {"$lt": datetime.utcnow()}
        })
        
        return result.deleted_count
        
    except Exception as e:
        print(f"Error cleaning up expired tokens: {e}")
        return 0
