import os
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any, Union
from jose import jwt, JWTError
from fastapi import HTTPException, status
from enum import Enum

SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-1234567890")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))

class TokenError(Enum):
    INVALID_FORMAT = "invalid_format"
    EXPIRED = "expired"
    INVALID_SIGNATURE = "invalid_signature"
    INVALID_ALGORITHM = "invalid_algorithm"
    INVALID_PAYLOAD = "invalid_payload"

def create_access_token(
    data: Dict[str, Any], 
    expires_delta: Optional[timedelta] = None,
    subject: Optional[str] = None
) -> str:
    if not data or not isinstance(data, dict):
        raise ValueError("Data must be a non-empty dictionary")
    
    to_encode = data.copy()
    
    now = datetime.now(timezone.utc)
    
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({
        "exp": expire,
        "iat": now,
        "nbf": now,
        "type": "access"
    })
    
    if subject:
        to_encode["sub"] = subject
    
    # Allow default key for development
    # if SECRET_KEY == "your-secret-key-1234567890":
    #     raise ValueError("JWT_SECRET_KEY environment variable must be set in production")
    
    try:
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    except Exception as e:
        raise ValueError(f"Failed to create token: {str(e)}")

def create_refresh_token(subject: str) -> str:
    if not subject:
        raise ValueError("Subject is required for refresh token")
    
    now = datetime.now(timezone.utc)
    expire = now + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    
    to_encode = {
        "exp": expire,
        "iat": now,
        "nbf": now,
        "sub": subject,
        "type": "refresh"
    }
    
    try:
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    except Exception as e:
        raise ValueError(f"Failed to create refresh token: {str(e)}")

def verify_token(token: str) -> Union[Dict[str, Any], TokenError]:
    if not token or not isinstance(token, str):
        return TokenError.INVALID_FORMAT
    
    try:
        payload = jwt.decode(
            token, 
            SECRET_KEY, 
            algorithms=[ALGORITHM],
            options={
                "verify_signature": True,
                "verify_exp": True,
                "verify_nbf": True
            }
        )
        return payload
    except jwt.ExpiredSignatureError:
        return TokenError.EXPIRED
    except jwt.JWSError:
        return TokenError.INVALID_SIGNATURE
    except jwt.JWTError:
        return TokenError.INVALID_FORMAT
    except Exception:
        return TokenError.INVALID_PAYLOAD

def is_token_expired(token: str) -> bool:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM], options={"verify_signature": False})
        exp = payload.get("exp")
        if not exp:
            return True
        
        exp_datetime = datetime.fromtimestamp(exp, tz=timezone.utc)
        return datetime.now(timezone.utc) > exp_datetime
    except:
        return True

def get_token_payload(token: str) -> Optional[Dict[str, Any]]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM], options={"verify_signature": False})
        return payload
    except:
        return None
