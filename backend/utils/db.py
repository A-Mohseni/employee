from pymongo import MongoClient
from typing import Optional

# Global MongoDB client
_client: Optional[MongoClient] = None

def get_db():
    """Get MongoDB database connection"""
    global _client
    
    if _client is None:
        try:
            _client = MongoClient("mongodb://localhost:27017/")
        except Exception as e:
            print(f"Error connecting to MongoDB: {e}")
            # For testing, return None if MongoDB is not available
            return None
    
    try:
        return _client["employee_db"]
    except Exception as e:
        print(f"Error accessing database: {e}")
        return None

def close_db():
    """Close MongoDB connection"""
    global _client
    if _client:
        _client.close()
        _client = None
