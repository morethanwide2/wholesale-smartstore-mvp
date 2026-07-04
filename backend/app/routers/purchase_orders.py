from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import PurchaseOrder

router = APIRouter(tags=["purchase-orders"])


@router.get("/purchase-orders")
def list_purchase_orders(
    status: str | None = None,
    admin_confirmed: bool | None = None,
    db: Session = Depends(get_db),
) -> dict[str, list]:
    query = select(PurchaseOrder).order_by(PurchaseOrder.id.desc())
    if status:
        query = query.where(PurchaseOrder.purchase_status == status)
    if admin_confirmed is not None:
        query = query.where(PurchaseOrder.admin_confirmed == admin_confirmed)
    purchase_orders = db.scalars(query).all()
    return {
        "items": [
            {
                "id": purchase_order.id,
                "supplier_product_id": purchase_order.supplier_product_id,
                "supplier_option_id": purchase_order.supplier_option_id,
                "quantity": purchase_order.quantity,
                "receiver_name": purchase_order.receiver_name,
                "receiver_phone": purchase_order.receiver_phone,
                "receiver_address": purchase_order.receiver_address,
                "purchase_status": purchase_order.purchase_status,
                "admin_confirmed": purchase_order.admin_confirmed,
            }
            for purchase_order in purchase_orders
        ]
    }
