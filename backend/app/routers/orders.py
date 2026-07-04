from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.order_collector import collect_mock_orders

router = APIRouter(tags=["orders"])


@router.post("/orders/collect")
def collect_orders(db: Session = Depends(get_db)) -> dict:
    result = collect_mock_orders(db)
    return {"status": "ok", **result}
