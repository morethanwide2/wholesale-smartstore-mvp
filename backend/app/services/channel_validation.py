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
    attributes = _merged_attributes(profile)
    issues: list[dict] = []

    product_name = profile.channel_product_name or master.cleaned_name or master.product_name or ""
    name_limit = CHANNEL_NAME_LIMITS.get(channel_code, 100)
    if not product_name.strip():
        issues.append(_issue("missing_product_name", "channel_product_name", "error", "채널 상품명이 필요합니다."))
    if len(product_name) > name_limit:
        issues.append(_issue("product_name_too_long", "channel_product_name", "error", f"상품명은 {name_limit}자 이하여야 합니다."))
    if not profile.channel_category_id:
        issues.append(_issue("missing_channel_category", "channel_category_id", "error", "채널 카테고리 ID가 필요합니다."))
    if not profile.channel_sale_price or profile.channel_sale_price <= 0:
        issues.append(_issue("invalid_sale_price", "channel_sale_price", "error", "채널 판매가는 0원보다 커야 합니다."))
    if profile.channel_sale_price and profile.channel_sale_price < master.supply_price + master.shipping_fee:
        issues.append(_issue("possible_negative_margin", "channel_sale_price", "warning", "판매가가 공급가와 배송비 합계보다 낮을 수 있습니다."))
    if not master.main_image_url:
        issues.append(_issue("missing_main_image", "main_image_url", "error", "대표이미지가 필요합니다."))
    if not master.description and not master.detail_image_urls:
        issues.append(_issue("missing_detail_page", "description", "warning", "상세설명 또는 상세이미지가 비어 있습니다."))
    if not master.options:
        issues.append(_issue("missing_options", "options", "error", "옵션 정보가 필요합니다."))

    for key in CHANNEL_REQUIRED_ATTRIBUTES.get(channel_code, []):
        if not attributes.get(key):
            issues.append(_issue("missing_required_attribute", f"attributes.{key}", "error", f"채널 필수 속성이 비어 있습니다: {key}"))

    if _looks_certification_sensitive(master.category_id or "") and not master.certification_info:
        issues.append(_issue("missing_certification_info", "certification_info", "warning", "인증정보가 필요할 수 있는 카테고리입니다."))

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


def _merged_attributes(profile: ChannelProductProfile) -> dict:
    master = profile.master_product
    supplier = master.supplier_product
    notice = master.notice_info_json or {}
    attributes = dict(profile.channel_attributes_json or {})
    attributes.setdefault("brand", master.brand or supplier.brand)
    attributes.setdefault("manufacturer", master.manufacturer or supplier.manufacturer)
    attributes.setdefault("origin", master.origin or supplier.origin)
    attributes.setdefault("notice_category", notice.get("notice_category"))
    attributes.setdefault("model_name", notice.get("model_name"))
    return attributes


def _looks_certification_sensitive(category: str) -> bool:
    keywords = ["kids", "child", "baby", "electric", "electronics", "fan", "bottle", "toy", "어린이", "유아", "전기", "안전", "인증"]
    lowered = category.lower()
    return any(keyword in lowered for keyword in keywords)


def _issue(code: str, field: str, severity: str, message: str) -> dict:
    return {"code": code, "field": field, "severity": severity, "message": message}
