from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Supplier, SupplierProduct, SupplierProductOption
from app.services.api_log_service import create_api_log
from app.services.supplier_api.client_factory import get_supplier_client


def ensure_mock_supplier(db: Session, supplier_id: int | None = None) -> Supplier:
    supplier = db.get(Supplier, supplier_id) if supplier_id else None
    if supplier:
        return supplier

    supplier = db.scalar(select(Supplier).where(Supplier.code == "mock_supplier"))
    if supplier:
        return supplier

    supplier = Supplier(id=supplier_id, name="Mock 도매몰", code="mock_supplier", api_base_url="mock://supplier")
    db.add(supplier)
    db.flush()
    return supplier


def import_products(db: Session, supplier_id: int) -> dict:
    supplier = ensure_mock_supplier(db, supplier_id)
    client = get_supplier_client()
    products = client.list_products()
    created = 0
    updated = 0
    option_count = 0

    for payload in products:
        product = db.scalar(
            select(SupplierProduct).where(
                SupplierProduct.supplier_id == supplier.id,
                SupplierProduct.supplier_product_id == payload["supplier_product_id"],
            )
        )
        if product is None:
            product = SupplierProduct(supplier_id=supplier.id, supplier_product_id=payload["supplier_product_id"])
            db.add(product)
            created += 1
        else:
            updated += 1

        product.raw_product_name = payload["raw_product_name"]
        product.raw_description = payload.get("raw_description")
        product.raw_category = payload.get("raw_category")
        product.brand = payload.get("brand")
        product.manufacturer = payload.get("manufacturer")
        product.origin = payload.get("origin")
        product.supply_price = payload.get("supply_price", 0)
        product.shipping_fee = payload.get("shipping_fee", 0)
        product.stock_quantity = payload.get("stock_quantity", 0)
        product.is_sold_out = payload.get("is_sold_out", False)
        product.is_discontinued = payload.get("is_discontinued", False)
        product.main_image_url = payload.get("main_image_url")
        product.detail_image_urls = payload.get("detail_image_urls", [])
        product.certification_info = payload.get("certification_info", {})
        product.raw_payload_json = payload
        product.last_synced_at = "2026-07-04T00:00:00"
        db.flush()

        for option_payload in payload.get("options", []):
            option = db.scalar(
                select(SupplierProductOption).where(
                    SupplierProductOption.supplier_product_id == product.id,
                    SupplierProductOption.supplier_option_id == option_payload["supplier_option_id"],
                )
            )
            if option is None:
                option = SupplierProductOption(
                    supplier_product_id=product.id,
                    supplier_option_id=option_payload["supplier_option_id"],
                )
                db.add(option)

            option.option_name = option_payload.get("option_name")
            option.option_value = option_payload.get("option_value")
            option.option_price = option_payload.get("option_price", 0)
            option.supply_price = option_payload.get("supply_price", product.supply_price)
            option.stock_quantity = option_payload.get("stock_quantity", 0)
            option.is_sold_out = option_payload.get("is_sold_out", False)
            option.is_discontinued = option_payload.get("is_discontinued", False)
            option.raw_payload_json = option_payload
            option_count += 1

    create_api_log(
        db=db,
        service_name="mock_supplier",
        endpoint="/products",
        method="GET",
        request_json={"supplier_id": supplier.id},
        response_json={"created": created, "updated": updated, "options": option_count},
        status_code=200,
        success=True,
    )
    db.commit()
    return {"supplier_id": supplier.id, "created": created, "updated": updated, "options": option_count}
