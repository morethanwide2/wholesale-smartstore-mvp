from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models import ChannelProductProfile, MasterProduct, SupplierProduct


CHANNEL_REQUIRED_ATTRIBUTES = {
    "smartstore": ["brand", "manufacturer", "origin"],
    "coupang": ["brand", "manufacturer", "origin", "notice_category"],
    "gmarket": ["brand", "manufacturer", "origin", "model_name"],
    "auction": ["brand", "manufacturer", "origin", "model_name"],
    "elevenstreet": ["brand", "manufacturer", "origin", "notice_category"],
    "toss_shopping": ["brand", "origin"],
    "lotteon": ["brand", "manufacturer", "origin"],
}

CHANNEL_NAME_LIMITS = {
    "smartstore": 100,
    "coupang": 100,
    "gmarket": 100,
    "auction": 100,
    "elevenstreet": 100,
    "toss_shopping": 80,
    "lotteon": 100,
}


def validate_channel_profile(db: Session, profile_id: int) -> dict:
    profile = db.scalar(
        select(ChannelProductProfile)
        .options(
            selectinload(ChannelProductProfile.channel),
            selectinload(ChannelProductProfile.master_product)
            .selectinload(MasterProduct.supplier_product)
            .selectinload(SupplierProduct.options),
            selectinload(ChannelProductProfile.master_product).selectinload(MasterProduct.options),
        )
        .where(ChannelProductProfile.id == profile_id)
    )
    if profile is None:
        raise ValueError("channel product profile not found")

    channel_code = profile.channel.code
    master = profile.master_product
    supplier = master.supplier_product
    attributes = _merged_attributes(profile, supplier)
    issues: list[dict] = []

    product_name = profile.channel_product_name or master.cleaned_name or master.product_name or ""
    name_limit = CHANNEL_NAME_LIMITS.get(channel_code, 100)
    if not product_name.strip():
        issues.append(_issue("missing_product_name", "channel_product_name", "error", "Marketplace product name is required."))
    if len(product_name) > name_limit:
        issues.append(_issue("product_name_too_long", "channel_product_name", "error", f"Product name must be {name_limit} chars or less."))
    if not profile.channel_category_id:
        issues.append(_issue("missing_channel_category", "channel_category_id", "error", "Marketplace category ID is required."))
    if not profile.channel_sale_price or profile.channel_sale_price <= 0:
        issues.append(_issue("invalid_sale_price", "channel_sale_price", "error", "Marketplace sale price must be greater than 0."))
    if profile.channel_sale_price and profile.channel_sale_price < master.supply_price + master.shipping_fee:
        issues.append(_issue("possible_negative_margin", "channel_sale_price", "warning", "Sale price may be lower than supply cost plus shipping fee."))
    if not master.main_image_url:
        issues.append(_issue("missing_main_image", "main_image_url", "error", "Main image is required."))
    if not master.description:
        issues.append(_issue("missing_detail_description", "description", "warning", "Detail description is empty."))
    if not master.options:
        issues.append(_issue("missing_options", "options", "error", "At least one option is required."))

    for key in CHANNEL_REQUIRED_ATTRIBUTES.get(channel_code, []):
        if not attributes.get(key):
            issues.append(_issue("missing_required_attribute", f"attributes.{key}", "error", f"Required marketplace attribute is missing: {key}"))

    if _looks_certification_sensitive(master.category_id or supplier.raw_category or "") and not (master.certification_info or supplier.certification_info):
        issues.append(_issue("missing_certification_info", "certification_info", "warning", "Certification information may be required for this category."))

    has_errors = any(issue["severity"] == "error" for issue in issues)
    result = {
        "profile_id": profile.id,
        "channel_code": channel_code,
        "valid": not has_errors,
        "error_count": sum(1 for issue in issues if issue["severity"] == "error"),
        "warning_count": sum(1 for issue in issues if issue["severity"] == "warning"),
        "required_attributes": CHANNEL_REQUIRED_ATTRIBUTES.get(channel_code, []),
        "resolved_attributes": attributes,
        "issues": issues,
    }
    profile.upload_validation_status = "passed" if result["valid"] else "failed"
    profile.last_validation_json = result
    db.commit()
    return result


def get_required_attributes(channel_code: str) -> dict:
    return {
        "channel_code": channel_code,
        "required_attributes": CHANNEL_REQUIRED_ATTRIBUTES.get(channel_code, []),
        "name_limit": CHANNEL_NAME_LIMITS.get(channel_code, 100),
    }


def _merged_attributes(profile: ChannelProductProfile, supplier: SupplierProduct) -> dict:
    attributes = dict(profile.channel_attributes_json or {})
    attributes.setdefault("brand", supplier.brand)
    attributes.setdefault("manufacturer", supplier.manufacturer)
    attributes.setdefault("origin", supplier.origin)
    return attributes


def _looks_certification_sensitive(category: str) -> bool:
    keywords = ["kids", "child", "baby", "electric", "electronics", "fan", "bottle", "toy", "어린이", "유아", "전기", "가전", "인증"]
    lowered = category.lower()
    return any(keyword in lowered for keyword in keywords)


def _issue(code: str, field: str, severity: str, message: str) -> dict:
    return {"code": code, "field": field, "severity": severity, "message": message}
