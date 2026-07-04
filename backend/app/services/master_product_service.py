from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.config import get_settings
from app.models import MasterProduct, MasterProductOption, SupplierProduct
from app.services.price_calculator import calculate_expected_margin, calculate_sale_price
from app.services.product_cleaner import clean_product_name


def create_master_from_supplier(db: Session, supplier_product_id: int) -> MasterProduct:
    supplier_product = db.scalar(
        select(SupplierProduct)
        .options(selectinload(SupplierProduct.options))
        .where(SupplierProduct.id == supplier_product_id)
    )
    if supplier_product is None:
        raise ValueError("supplier product not found")

    existing = db.scalar(select(MasterProduct).where(MasterProduct.supplier_product_id == supplier_product.id))
    if existing:
        return existing

    settings = get_settings()
    clean_result = clean_product_name(supplier_product.raw_product_name)
    sale_price = calculate_sale_price(
        supplier_product.supply_price,
        supplier_product.shipping_fee,
        settings.default_margin_rate,
        settings.default_price_round_unit,
    )
    status = "discontinued" if supplier_product.is_discontinued else "sold_out" if supplier_product.is_sold_out else "draft"
    master = MasterProduct(
        internal_product_code=f"MP-{supplier_product.id:06d}",
        supplier_product_id=supplier_product.id,
        product_name=supplier_product.raw_product_name,
        display_name=clean_result.cleaned_name,
        cleaned_name=clean_result.cleaned_name,
        description=supplier_product.raw_description,
        category_id=supplier_product.raw_category,
        supply_price=supplier_product.supply_price,
        shipping_fee=supplier_product.shipping_fee,
        sale_price=sale_price,
        margin_rate=settings.default_margin_rate,
        expected_margin_amount=calculate_expected_margin(sale_price, supplier_product.supply_price, supplier_product.shipping_fee),
        main_image_url=supplier_product.main_image_url,
        detail_image_urls=supplier_product.detail_image_urls,
        certification_info=supplier_product.certification_info,
        status=status,
        review_status="pending",
        needs_review=clean_result.needs_review,
    )
    db.add(master)
    db.flush()

    for supplier_option in supplier_product.options:
        option_sale_price = calculate_sale_price(
            supplier_option.supply_price,
            supplier_product.shipping_fee,
            settings.default_margin_rate,
            settings.default_price_round_unit,
        )
        option_status = "discontinued" if supplier_option.is_discontinued else "sold_out" if supplier_option.is_sold_out else "active"
        db.add(
            MasterProductOption(
                master_product_id=master.id,
                internal_option_code=f"MO-{supplier_option.id:06d}",
                supplier_option_id=supplier_option.id,
                option_name=supplier_option.option_name,
                option_value=supplier_option.option_value,
                supply_price=supplier_option.supply_price,
                sale_price=option_sale_price,
                stock_quantity=supplier_option.stock_quantity,
                status=option_status,
            )
        )

    db.commit()
    db.refresh(master)
    return master


def approve_master_product(db: Session, master_product_id: int) -> MasterProduct:
    master = db.get(MasterProduct, master_product_id)
    if master is None:
        raise ValueError("master product not found")
    master.review_status = "approved"
    if master.status == "draft":
        master.status = "ready"
    db.commit()
    db.refresh(master)
    return master
