import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(
    title="Employee Management API",
    description="API for managing employee data, leave requests, and more",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)


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
