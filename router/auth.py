from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from datetime import datetime, timedelta, timezone
from pymongo import MongoClient
from bson import ObjectId
from utils.db import get_db

# تنظیمات JWT
SECRET_KEY = "your-secret-key-1234567890"  # این رو بعداً از environment variable بخون
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# OAuth2 برای گرفتن توکن از header
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# تابع برای ایجاد توکن JWT
def create_token(user_id: str, role: str) -> str:
    to_encode = {
        "user_id": user_id,
        "role": role,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    }
    # ایجاد توکن با استفاده از SECRET_KEY و الگوریتم HS256
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# تابع برای بررسی و رمزگشایی توکن
def verify_token(token: str):
    try:
        # رمزگشایی توکن و بررسی اعتبار
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("user_id")
        role: str = payload.get("role")
        
        if user_id is None or role is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="توکن نامعتبر است",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return {"user_id": user_id, "role": role}
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="توکن نامعتبر است",
            headers={"WWW-Authenticate": "Bearer"},
        )

# تابع برای دریافت کاربر فعلی از توکن
async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="نمی‌توان اعتبارنامه‌ها را تأیید کرد",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = verify_token(token)
        user_id = payload.get("user_id")
        if user_id is None:
            raise credentials_exception
        return payload
    except JWTError:
        raise credentials_exception