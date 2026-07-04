from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.database import get_db
from app.models import MasterProduct, MasterProductOption, SupplierProduct
from app.services.master_product_service import approve_master_product as approve_master
from app.services.master_product_service import create_master_from_supplier

router = APIRouter(tags=["products"])


class MasterProductUpdate(BaseModel):
    display_name: str | None = None
    cleaned_name: str | None = None
    description: str | None = None
    category_id: str | None = None
    brand: str | None = None
    manufacturer: str | None = None
    origin: str | None = None
    search_tags: list[str] | None = None
    notice_info_json: dict | None = None
    sale_price: int | None = None
    shipping_fee: int | None = None
    main_image_url: str | None = None
    detail_image_urls: list[str] | None = None
    certification_info: dict | None = None
    needs_review: bool | None = None


class MasterProductOptionUpdate(BaseModel):
    option_name: str | None = None
    option_value: str | None = None
    sale_price: int | None = None
    stock_quantity: int | None = None
    status: str | None = None


@router.get("/supplier-products")
def list_supplier_products(
    keyword: str | None = None,
    is_sold_out: bool | None = None,
    is_discontinued: bool | None = None,
    db: Session = Depends(get_db),
) -> dict[str, list]:
    query = select(SupplierProduct).options(selectinload(SupplierProduct.options)).order_by(SupplierProduct.id)
    if keyword:
        query = query.where(SupplierProduct.raw_product_name.contains(keyword))
    if is_sold_out is not None:
        query = query.where(SupplierProduct.is_sold_out == is_sold_out)
    if is_discontinued is not None:
        query = query.where(SupplierProduct.is_discontinued == is_discontinued)

    products = db.scalars(query).all()
    return {
        "items": [
            {
                "id": product.id,
                "supplier_product_id": product.supplier_product_id,
                "name": product.raw_product_name,
                "supply_price": product.supply_price,
                "shipping_fee": product.shipping_fee,
                "stock_quantity": product.stock_quantity,
                "is_sold_out": product.is_sold_out,
                "is_discontinued": product.is_discontinued,
                "option_count": len(product.options),
            }
            for product in products
        ]
    }


@router.post("/master-products/from-supplier/{supplier_product_id}")
def create_master_product(supplier_product_id: int, db: Session = Depends(get_db)) -> dict:
    try:
        master = create_master_from_supplier(db, supplier_product_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return {"status": "ok", "master_product_id": master.id, "internal_product_code": master.internal_product_code}


@router.get("/supplier-products/{supplier_product_id}")
def get_supplier_product_detail(supplier_product_id: int, db: Session = Depends(get_db)) -> dict:
    product = db.scalar(
        select(SupplierProduct)
        .options(selectinload(SupplierProduct.options))
        .where(SupplierProduct.id == supplier_product_id)
    )
    if product is None:
        raise HTTPException(status_code=404, detail="supplier product not found")

    return {
        "id": product.id,
        "supplier_product_id": product.supplier_product_id,
        "raw_product_name": product.raw_product_name,
        "raw_description": product.raw_description,
        "raw_category": product.raw_category,
        "brand": product.brand,
        "manufacturer": product.manufacturer,
        "origin": product.origin,
        "supply_price": product.supply_price,
        "shipping_fee": product.shipping_fee,
        "stock_quantity": product.stock_quantity,
        "is_sold_out": product.is_sold_out,
        "is_discontinued": product.is_discontinued,
        "main_image_url": product.main_image_url,
        "detail_image_urls": product.detail_image_urls or [],
        "certification_info": product.certification_info or {},
        "raw_payload_json": product.raw_payload_json or {},
        "options": [
            {
                "id": option.id,
                "supplier_option_id": option.supplier_option_id,
                "option_name": option.option_name,
                "option_value": option.option_value,
                "option_price": option.option_price,
                "supply_price": option.supply_price,
                "stock_quantity": option.stock_quantity,
                "is_sold_out": option.is_sold_out,
                "is_discontinued": option.is_discontinued,
            }
            for option in product.options
        ],
    }


@router.get("/master-products")
def list_master_products(
    keyword: str | None = None,
    status: str | None = None,
    review_status: str | None = None,
    needs_review: bool | None = None,
    db: Session = Depends(get_db),
) -> dict[str, list]:
    query = select(MasterProduct).options(selectinload(MasterProduct.options)).order_by(MasterProduct.id)
    if keyword:
        query = query.where(MasterProduct.cleaned_name.contains(keyword))
    if status:
        query = query.where(MasterProduct.status == status)
    if review_status:
        query = query.where(MasterProduct.review_status == review_status)
    if needs_review is not None:
        query = query.where(MasterProduct.needs_review == needs_review)

    products = db.scalars(query).all()
    return {
        "items": [
            {
                "id": product.id,
                "internal_product_code": product.internal_product_code,
                "name": product.cleaned_name,
                "brand": product.brand,
                "origin": product.origin,
                "supply_price": product.supply_price,
                "shipping_fee": product.shipping_fee,
                "sale_price": product.sale_price,
                "margin_rate": float(product.margin_rate),
                "expected_margin_amount": product.expected_margin_amount,
                "status": product.status,
                "review_status": product.review_status,
                "needs_review": product.needs_review,
                "validation_status": product.validation_status,
                "option_count": len(product.options),
            }
            for product in products
        ]
    }


@router.post("/master-products/{master_product_id}/approve")
def approve_master_product(master_product_id: int, db: Session = Depends(get_db)) -> dict:
    try:
        master = approve_master(db, master_product_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return {"status": "ok", "master_product_id": master.id, "product_status": master.status}


@router.get("/master-products/{master_product_id}")
def get_master_product_detail(master_product_id: int, db: Session = Depends(get_db)) -> dict:
    product = db.scalar(
        select(MasterProduct)
        .options(
            selectinload(MasterProduct.options),
            selectinload(MasterProduct.supplier_product).selectinload(SupplierProduct.options),
        )
        .where(MasterProduct.id == master_product_id)
    )
    if product is None:
        raise HTTPException(status_code=404, detail="master product not found")

    supplier = product.supplier_product
    return {
        "id": product.id,
        "internal_product_code": product.internal_product_code,
        "supplier_product_id": product.supplier_product_id,
        "product_name": product.product_name,
        "display_name": product.display_name,
        "cleaned_name": product.cleaned_name,
        "description": product.description,
        "category_id": product.category_id,
        "brand": product.brand,
        "manufacturer": product.manufacturer,
        "origin": product.origin,
        "search_tags": product.search_tags or [],
        "notice_info_json": product.notice_info_json or {},
        "supply_price": product.supply_price,
        "shipping_fee": product.shipping_fee,
        "sale_price": product.sale_price,
        "margin_rate": float(product.margin_rate),
        "expected_margin_amount": product.expected_margin_amount,
        "main_image_url": product.main_image_url,
        "detail_image_urls": product.detail_image_urls or [],
        "certification_info": product.certification_info or {},
        "status": product.status,
        "review_status": product.review_status,
        "price_review_required": product.price_review_required,
        "needs_review": product.needs_review,
        "validation_status": product.validation_status,
        "validation_issues_json": product.validation_issues_json or [],
        "options": [
            {
                "id": option.id,
                "internal_option_code": option.internal_option_code,
                "supplier_option_id": option.supplier_option_id,
                "option_name": option.option_name,
                "option_value": option.option_value,
                "supply_price": option.supply_price,
                "sale_price": option.sale_price,
                "stock_quantity": option.stock_quantity,
                "status": option.status,
            }
            for option in product.options
        ],
        "supplier_source": {
            "supplier_product_id": supplier.supplier_product_id,
            "raw_product_name": supplier.raw_product_name,
            "raw_description": supplier.raw_description,
            "raw_category": supplier.raw_category,
            "brand": supplier.brand,
            "manufacturer": supplier.manufacturer,
            "origin": supplier.origin,
            "main_image_url": supplier.main_image_url,
            "detail_image_urls": supplier.detail_image_urls or [],
            "certification_info": supplier.certification_info or {},
            "options": [
                {
                    "id": option.id,
                    "supplier_option_id": option.supplier_option_id,
                    "option_name": option.option_name,
                    "option_value": option.option_value,
                    "supply_price": option.supply_price,
                    "stock_quantity": option.stock_quantity,
                    "is_sold_out": option.is_sold_out,
                    "is_discontinued": option.is_discontinued,
                }
                for option in supplier.options
            ],
        },
    }


@router.patch("/master-products/{master_product_id}")
def update_master_product(
    master_product_id: int,
    payload: MasterProductUpdate,
    db: Session = Depends(get_db),
) -> dict:
    product = db.get(MasterProduct, master_product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="master product not found")

    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(product, field, value)
    db.commit()
    db.refresh(product)
    return {"status": "ok", "master_product_id": product.id}


@router.patch("/master-product-options/{master_option_id}")
def update_master_product_option(
    master_option_id: int,
    payload: MasterProductOptionUpdate,
    db: Session = Depends(get_db),
) -> dict:
    option = db.get(MasterProductOption, master_option_id)
    if option is None:
        raise HTTPException(status_code=404, detail="master product option not found")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(option, field, value)
    db.commit()
    db.refresh(option)
    return {"status": "ok", "master_option_id": option.id}
