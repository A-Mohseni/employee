import functools
import asyncio
from fastapi import HTTPException
from fastapi.responses import JSONResponse

def exception_handler(func):
    if asyncio.iscoroutinefunction(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except HTTPException:
                raise
            except Exception as exc:
                return JSONResponse(status_code=500, content={"detail": str(exc) or "Internal Server Error"})
        return wrapper
    else:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except HTTPException:
                raise
            except Exception as exc:
                return JSONResponse(status_code=500, content={"detail": str(exc) or "Internal Server Error"})
        return wrapper