from typing import Any, Dict, List
from datetime import datetime

def format_datetime(dt: datetime) -> str:
    return dt.isoformat() if dt else None

def safe_get(data: Dict[str, Any], key: str, default: Any = None) -> Any:
    return data.get(key, default)

def filter_dict(data: Dict[str, Any], allowed_keys: List[str]) -> Dict[str, Any]:
    return {k: v for k, v in data.items() if k in allowed_keys}

def mask_password(password_length: int) -> str:
    if password_length <= 0:
        return "Please enter password"
    return "*" * password_length