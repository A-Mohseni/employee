import functools
from fastapi import HTTPException, status
from services.log import service_exception

def service_exception(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except HTTPException:
            raise
        except Exception as exc:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(exc) or "Internal Server Error"
            )
    return wrapper