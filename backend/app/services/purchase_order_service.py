from sqlalchemy.orm import Session

from app.models import MasterProduct, Order, OrderItem, PurchaseOrder, SupplierProduct, SupplierProductOption


def create_purchase_order_for_item(db: Session, order: Order, item: OrderItem) -> PurchaseOrder | None:
    if item.mapping_status != "matched" or item.master_product_id is None:
        return None

    master = db.get(MasterProduct, item.master_product_id)
    if master is None:
        return None

    supplier_product = db.get(SupplierProduct, master.supplier_product_id)
    supplier_option = None
    if item.master_option_id:
        for option in master.options:
            if option.id == item.master_option_id and option.supplier_option_id:
                supplier_option = db.get(SupplierProductOption, option.supplier_option_id)
                break
    if supplier_product is None:
        return None

    purchase_order = PurchaseOrder(
        order_item_id=item.id,
        supplier_id=supplier_product.supplier_id,
        supplier_product_id=supplier_product.supplier_product_id,
        supplier_option_id=supplier_option.supplier_option_id if supplier_option else None,
        quantity=item.quantity,
        receiver_name=order.receiver_name,
        receiver_phone=order.receiver_phone,
        receiver_address=order.receiver_address,
        delivery_message=order.delivery_message,
        purchase_status="ready",
        admin_confirmed=False,
    )
    db.add(purchase_order)
    return purchase_order
