from typing import Any, Dict, List
from datetime import datetime

def format_datetime(dt: datetime) -> str:
    """Format datetime to string"""
    return dt.isoformat() if dt else None

def safe_get(data: Dict[str, Any], key: str, default: Any = None) -> Any:
    """Safely get value from dictionary"""
    return data.get(key, default)

def filter_dict(data: Dict[str, Any], allowed_keys: List[str]) -> Dict[str, Any]:
    """Filter dictionary to only include allowed keys"""
    return {k: v for k, v in data.items() if k in allowed_keys}
