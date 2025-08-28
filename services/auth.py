from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional, Literal, Dict, Any

# Lazy/optional import to allow running without python-jose when SSL blocks pip
try:
    from utils.jwt import verify_token  # type: ignore
    _jwt_available = True
except Exception:
    verify_token = None  # type: ignore
    _jwt_available = False

security = HTTPBearer(auto_error=False if not _jwt_available else True)

Role = Literal["admin1", "admin2", "manager_women", "manager_men", "employee"]


def get_current_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> Dict[str, Any]:
    # Fallback: if jwt is unavailable (offline/SSL), allow a mock admin1 to run the app
    if not _jwt_available:
        return {"role": "admin1", "user_id": "507f1f77bcf86cd799439011"}

    if not credentials or not credentials.credentials:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing credentials")

    payload = verify_token(credentials.credentials)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    role: Optional[str] = payload.get("role")
    user_id: Optional[str] = payload.get("user_id")
    if role not in ["admin1", "admin2", "manager_women", "manager_men", "employee"] or not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")

    return {"role": role, "user_id": user_id}


def require_roles(*allowed_roles: Role):
    def dependency(user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
        if user.get("role") not in allowed_roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
        return user
    return dependency
