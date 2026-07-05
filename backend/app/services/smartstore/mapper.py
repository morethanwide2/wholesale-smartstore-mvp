from sqlalchemy.orm import selectinload

from app.models import MasterProduct


def build_product_payload(master_product: MasterProduct) -> dict:
    if not master_product.cleaned_name:
        raise ValueError("cleaned_name is required")
    if not master_product.main_image_url:
        raise ValueError("main_image_url is required")

    return {
        "originProduct": {
            "name": master_product.cleaned_name,
            "salePrice": master_product.sale_price,
            "status": master_product.status,
            "images": {
                "representativeImageUrl": master_product.main_image_url,
                "detailImageUrls": master_product.detail_image_urls or [],
            },
            "detailContent": master_product.description or "",
            "brand": master_product.brand,
            "manufacturer": master_product.manufacturer,
            "origin": master_product.origin,
            "searchTags": master_product.search_tags or [],
            "certificationInfo": master_product.certification_info or {},
            "noticeInfo": master_product.notice_info_json or {},
            "deliveryInfo": {
                "deliveryFeeType": "PAID" if master_product.shipping_fee else "FREE",
                "baseFee": master_product.shipping_fee,
            },
        },
        "options": [
            {
                "internalOptionCode": option.internal_option_code,
                "optionName": option.option_name or "기본",
                "optionValue": option.option_value or "단일",
                "salePrice": option.sale_price,
                "stockQuantity": option.stock_quantity,
                "status": option.status,
            }
            for option in master_product.options
        ],
    }


def load_options() -> list:
    return [selectinload(MasterProduct.options)]
