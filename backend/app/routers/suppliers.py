from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.product_importer import import_products as import_supplier_products

router = APIRouter(tags=["suppliers"])


@router.post("/suppliers/{supplier_id}/import-products")
def import_products(supplier_id: int, db: Session = Depends(get_db)) -> dict:
    result = import_supplier_products(db, supplier_id)
    return {"status": "ok", **result}
