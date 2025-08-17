from fastapi import FastAPI
from router.user import router as user_router

app = FastAPI(redoc_url="/redoc")

app.include_router(user_router)

@app.get("/")
def read_root():
    return {"message": "hello welcome to fastapi"}
