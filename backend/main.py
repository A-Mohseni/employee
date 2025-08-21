from fastapi import FastAPI
from router.user import router as user_router
from router.purchase_item import router as purchase_item_router
from router.report import router as report_router

app = FastAPI(redoc_url="/redoc")

app.include_router(user_router)
app.include_router(purchase_item_router)
app.include_router(report_router)


@app.get("/")
def read_root():
    return {"message": "hello welcome to fastapi"}
