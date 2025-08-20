from fastapi import APIRouter

router = APIRouter(prefix="/purchase-items", tags=["purchase-items"])

@router.get("/")
def get_purchase_items():
    """
    Get all purchase items
    """
    return {"message": "Purchase items endpoint"}
