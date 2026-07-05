from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models import ErrorQueue, MasterProduct


FORBIDDEN_TAG_WORDS = [
    "헬스",
    "덤벨",
    "케틀벨",
    "키링",
    "기홀더",
    "스포츠",
    "축구",
]

CERTIFICATION_SENSITIVE_WORDS = [
    "어린이",
    "유아",
    "아동",
    "전기",
    "전동",
    "안전",
    "인증",
    "식품",
    "화장품",
]


def validate_master_for_smartstore(db: Session, master_product_id: int) -> dict:
    master = db.scalar(
        select(MasterProduct)
        .options(selectinload(MasterProduct.options))
        .where(MasterProduct.id == master_product_id)
    )
    if master is None:
        raise ValueError("master product not found")

    result = validate_master_product_shape(master)
    master.validation_status = "passed" if result["valid"] else "failed"
    master.validation_issues_json = result["issues"]
    if result["valid"] and master.review_status == "approved" and master.status == "draft":
        master.status = "ready"
    if not result["valid"]:
        master.needs_review = True
    db.commit()
    return result


def validate_master_product_shape(master: MasterProduct) -> dict:
    issues: list[dict] = []
    name = master.cleaned_name or master.display_name or master.product_name or ""
    category = master.category_id or ""
    description = master.description or ""
    tags = master.search_tags or []

    if not name.strip():
        issues.append(_issue("missing_product_name", "cleaned_name", "error", "상품명이 비어 있습니다."))
    if len(name) > 100:
        issues.append(_issue("product_name_too_long", "cleaned_name", "error", "스마트스토어 상품명은 100자 이내여야 합니다."))
    if not category.strip():
        issues.append(_issue("missing_category", "category_id", "error", "스마트스토어 카테고리 매핑이 필요합니다."))
    if not master.main_image_url:
        issues.append(_issue("missing_main_image", "main_image_url", "error", "대표이미지가 필요합니다."))
    if not description.strip() and not master.detail_image_urls:
        issues.append(_issue("missing_detail_page", "description", "warning", "상세설명 또는 상세이미지가 비어 있습니다."))
    if master.sale_price <= 0:
        issues.append(_issue("invalid_sale_price", "sale_price", "error", "판매가는 0원보다 커야 합니다."))
    if master.sale_price and master.sale_price < master.supply_price + master.shipping_fee:
        issues.append(_issue("negative_margin_risk", "sale_price", "warning", "판매가가 공급가와 배송비 합계보다 낮습니다."))
    if not master.brand:
        issues.append(_issue("missing_brand", "brand", "warning", "브랜드 정보가 비어 있습니다. 없으면 '무브랜드'처럼 명확히 입력하세요."))
    if not master.manufacturer:
        issues.append(_issue("missing_manufacturer", "manufacturer", "warning", "제조사 정보가 비어 있습니다."))
    if not master.origin:
        issues.append(_issue("missing_origin", "origin", "warning", "원산지 정보가 비어 있습니다."))
    if not master.options:
        issues.append(_issue("missing_options", "options", "error", "옵션 정보가 없습니다."))

    active_options = [option for option in master.options if option.status == "active"]
    if master.options and not active_options:
        issues.append(_issue("no_active_options", "options", "error", "판매 가능한 활성 옵션이 없습니다."))

    for option in master.options:
        if option.sale_price <= 0:
            issues.append(_issue("invalid_option_price", "options", "error", f"{option.internal_option_code} 옵션 판매가가 0원 이하입니다."))
        if option.stock_quantity < 0:
            issues.append(_issue("invalid_option_stock", "options", "error", f"{option.internal_option_code} 옵션 재고가 음수입니다."))
        if option.status == "active" and option.stock_quantity == 0:
            issues.append(_issue("active_option_without_stock", "options", "warning", f"{option.internal_option_code} 옵션이 활성 상태지만 재고가 0입니다."))

    searchable_text = " ".join([name, description, " ".join(tags), " ".join([option.option_value or "" for option in master.options])])
    for word in FORBIDDEN_TAG_WORDS:
        if word in searchable_text:
            issues.append(_issue("forbidden_word", "search_tags", "error", f"등록 제한 또는 검수 필요 단어가 포함되어 있습니다: {word}"))

    if _needs_certification(name, category, description) and not master.certification_info:
        issues.append(_issue("missing_certification_info", "certification_info", "warning", "인증/안전정보 확인이 필요한 상품으로 보입니다."))

    has_errors = any(issue["severity"] == "error" for issue in issues)
    return {
        "master_product_id": master.id,
        "valid": not has_errors,
        "error_count": sum(1 for issue in issues if issue["severity"] == "error"),
        "warning_count": sum(1 for issue in issues if issue["severity"] == "warning"),
        "issues": issues,
    }


def create_upload_failure(db: Session, master_product_id: int, validation_result: dict) -> ErrorQueue:
    message = "; ".join(issue["message"] for issue in validation_result["issues"] if issue["severity"] == "error")
    failure = ErrorQueue(
        task_type="smartstore_upload_validation",
        related_entity_type="master_product",
        related_entity_id=master_product_id,
        error_message=message[:2000] or "Smartstore validation failed",
        status="pending",
    )
    db.add(failure)
    return failure


def _needs_certification(name: str, category: str, description: str) -> bool:
    text = f"{name} {category} {description}"
    return any(word in text for word in CERTIFICATION_SENSITIVE_WORDS)


def _issue(code: str, field: str, severity: str, message: str) -> dict:
    return {"code": code, "field": field, "severity": severity, "message": message}
