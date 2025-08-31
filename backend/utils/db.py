from pymongo import MongoClient
from typing import Optional

_client: Optional[MongoClient] = None

def get_db():
    global _client
    
    if _client is None:
        try:
            _client = MongoClient("mongodb://localhost:27017/")
        except Exception as e:
            print(f"Error connecting to MongoDB: {e}")
            return None
    
    try:
        return _client["employee_db"]
    except Exception as e:
        print(f"Error accessing database: {e}")
        return None

def close_db():
    global _client
    if _client:
        _client.close()
        _client = None
