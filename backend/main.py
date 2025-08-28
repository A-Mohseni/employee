import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, Request
from router.leave_request import router as leave_request_router
from router.user import router as user_router
from router.report import router as report_router
from router.purchase_item import router as purchase_item_router
from router.checklist import router as checklist_router
from router.auth import router as auth_router
from pydantic import BaseModel
from fastapi.responses import PlainTextResponse
import traceback
import os
from fastapi.openapi.utils import get_openapi
from fastapi.routing import APIRoute




app = FastAPI(
    title="Employee Management API",
    description="API for managing employee data, leave requests, and more",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)


# Global exception handler to log full tracebacks for easier debugging
@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    tb = "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))
    print(tb)
    return PlainTextResponse("Internal Server Error", status_code=500)


# Register application routers
app.include_router(auth_router)
app.include_router(user_router)
app.include_router(leave_request_router)
app.include_router(report_router)
app.include_router(purchase_item_router)
app.include_router(checklist_router)


class TestModel(BaseModel):
    name: str
    age: int


@app.get("/")
def read_root():
    return {"message": "hello welcome to fastapi"}


@app.get("/test")
def test_endpoint():
    return {"message": "test endpoint working"}


@app.post("/test-model")
def test_model(data: TestModel):
    return {"received": data}


# Optional: diagnose which route breaks OpenAPI by printing file and line
@app.on_event("startup")
async def diagnose_openapi():
    if os.getenv("DEBUG_OPENAPI", "1") != "1":
        return
    routes = [r for r in app.routes if isinstance(r, APIRoute)]
    for route in routes:
        try:
            # Build OpenAPI only for this single route
            get_openapi(
                title="diag",
                version="1.0.0",
                routes=[route],
                description=None,
            )
        except Exception as exc:
            endpoint = route.endpoint
            try:
                filename = endpoint.__code__.co_filename
                lineno = endpoint.__code__.co_firstlineno
            except Exception:
                filename = str(endpoint)
                lineno = -1
            print("[OPENAPI-ERROR] path=", route.path, "name=", route.name)
            print("  endpoint=", endpoint.__module__, getattr(endpoint, "__name__", str(endpoint)))
            print("  location=", filename, ":", lineno)
            print("  detail=", repr(exc))
