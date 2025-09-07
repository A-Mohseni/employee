import logging
import functools
from fastapi import HTTPException, status

logger = logging.getLogger("employee")
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)


def service_exception(func):
    """
    Decorator for service functions: logs exceptions and converts unexpected errors
    to HTTPException(status_code=500).
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except HTTPException:
            # Preserve explicit HTTPExceptions raised inside services
            raise
        except Exception as exc:
            logger.exception("Unhandled exception in %s: %s", func.__name__, exc)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")
    return wrapper