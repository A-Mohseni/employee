import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, Request, HTTPException
from router.leave_request import router as leave_request_router
from router.user import router as user_router
from router.report import router as report_router
from router.purchase_item import router as purchase_item_router
from router.checklist import router as checklist_router
from router.auth import router as auth_router
from pydantic import BaseModel
from fastapi.responses import PlainTextResponse, JSONResponse
import traceback
import os
from fastapi.openapi.utils import get_openapi
from fastapi.routing import APIRoute
from router.dashboard import router as dashboadrd_router



app = FastAPI(
    title="Employee Management API",
    description="API for managing employee data, leave requests, and more",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    tb = "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))
    print(tb)
    return JSONResponse(status_code=500, content={"detail": "Internal Server Error"})


app.include_router(auth_router)
app.include_router(user_router)
app.include_router(leave_request_router)
app.include_router(report_router)
app.include_router(purchase_item_router)
app.include_router(checklist_router)
app.include_router(dashboadrd_router)

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


async def create_default_admins():
    """Create default admin accounts on startup"""
    try:
        from utils.db import get_db
        from utils.password_hash import hash_password
        from datetime import datetime
        from bson import ObjectId
        
        db = get_db()
        admins = db["admins"]
        
        # Check if any admin exists
        if admins.count_documents({}) > 0:
            print("✅ Admins already exist, skipping default admin creation")
            return
        
        # Create default super admin
        admin_data = {
            "_id": ObjectId(),
            "employee_id": "00001",
            "full_name": "مدیر اصلی سیستم",
            "password_hash": hash_password("admin123!"),
            "role": "admin1",
            "status": "active",
            "phone": "09123456789",
            "email": "admin@company.com",
            "is_super_admin": True,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
        
        admins.insert_one(admin_data)
        print("✅ Default super admin created successfully!")
        print("   Employee ID: 00001")
        print("   Password: admin123!")
        print("   ⚠️  Please change the default password after first login!")
        
    except Exception as e:
        print(f"❌ Error creating default admin: {e}")

@app.on_event("startup")
async def startup_event():
    """Application startup event"""
    print("🚀 Starting Employee Management System...")
    
    # Create default admins
    await create_default_admins()
    
    # OpenAPI diagnosis (if enabled)
    if os.getenv("DEBUG_OPENAPI", "1") != "1":
        return
    routes = [r for r in app.routes if isinstance(r, APIRoute)]
    for route in routes:
        try:
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
