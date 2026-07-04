from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models import InventoryLog, MasterProduct, PriceLog, SupplierProduct


def sync_inventory(db: Session) -> dict:
    masters = db.scalars(select(MasterProduct).options(selectinload(MasterProduct.options))).all()
    stock_changes = 0
    price_changes = 0

    for master in masters:
        supplier_product = db.get(SupplierProduct, master.supplier_product_id)
        if supplier_product is None:
            continue

        if master.supply_price != supplier_product.supply_price:
            db.add(
                PriceLog(
                    master_product_id=master.id,
                    previous_supply_price=master.supply_price,
                    new_supply_price=supplier_product.supply_price,
                    previous_sale_price=master.sale_price,
                    new_sale_price=master.sale_price,
                    change_reason="supplier_supply_price_changed",
                )
            )
            master.price_review_required = True
            price_changes += 1

        for option in master.options:
            if option.stock_quantity == 0 and option.status != "sold_out":
                db.add(
                    InventoryLog(
                        master_product_id=master.id,
                        master_option_id=option.id,
                        previous_stock=option.stock_quantity,
                        new_stock=0,
                        change_reason="option_sold_out",
                        source="supplier",
                    )
                )
                option.status = "sold_out"
                stock_changes += 1

        if supplier_product.is_discontinued:
            master.status = "discontinued"
        elif supplier_product.is_sold_out:
            master.status = "sold_out"

    db.commit()
    return {"stock_changes": stock_changes, "price_changes": price_changes}
