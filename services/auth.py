from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional

security = HTTPBearer(auto_error=False)  # Make token optional for testing

def get_current_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> dict:
    """
    Simple authentication function that returns a mock user.
    For testing purposes, this allows access without requiring a real token.
    In production, you would validate the JWT token here.
    """
    # For testing, return a mock manager user to allow the application to run
    # In production, you would validate the JWT token here
    return {
        "role": "manager",
        "user_id": "mock_user_id"
    }
