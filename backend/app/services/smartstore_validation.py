from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models import ErrorQueue, MasterProduct


FORBIDDEN_TAG_WORDS = [
    "가품",
    "헬스",
    "덤벨",
    "케틀벨",
    "키링",
    "키보드",
    "스피너",
    "축구",
]

OPTION_RESTRICTED_CATEGORY_WORDS = ["패션", "잡화", "스포츠", "테스트"]


def validate_master_for_smartstore(db: Session, master_product_id: int) -> dict:
    master = db.scalar(
        select(MasterProduct)
        .options(selectinload(MasterProduct.options))
        .where(MasterProduct.id == master_product_id)
    )
    if master is None:
        raise ValueError("master product not found")

    issues: list[dict] = []
    name = master.cleaned_name or master.product_name or ""
    category = master.category_id or ""

    if not name.strip():
        issues.append(_issue("missing_product_name", "cleaned_name", "error", "상품명이 비어 있습니다."))
    if len(name) > 100:
        issues.append(_issue("product_name_too_long", "cleaned_name", "error", "상품명은 100자 이하로 줄여야 합니다."))
    if not master.main_image_url:
        issues.append(_issue("missing_main_image", "main_image_url", "error", "대표 이미지가 없습니다."))
    if not category:
        issues.append(_issue("missing_category", "category_id", "error", "스마트스토어 카테고리 매핑이 필요합니다."))
    if "테스트" in category:
        issues.append(
            _issue(
                "category_meta_lookup_failed",
                "category_id",
                "error",
                "카테고리 메타 조회에 실패했습니다. 카테고리 코드와 권한을 확인해야 합니다.",
            )
        )
    if master.sale_price <= 0:
        issues.append(_issue("invalid_sale_price", "sale_price", "error", "판매가가 0원 이하입니다."))
    if not master.options:
        issues.append(_issue("missing_options", "options", "error", "옵션이 없습니다."))

    for word in FORBIDDEN_TAG_WORDS:
        if word in name:
            issues.append(
                _issue(
                    "forbidden_tag_word",
                    "cleaned_name",
                    "error",
                    f"태그/상품명에 등록 불가 단어가 포함되어 있습니다: {word}",
                )
            )

    option_values = " ".join([option.option_value or "" for option in master.options])
    for word in FORBIDDEN_TAG_WORDS:
        if word in option_values:
            issues.append(
                _issue(
                    "forbidden_option_word",
                    "options",
                    "error",
                    f"옵션값에 등록 불가 단어가 포함되어 있습니다: {word}",
                )
            )

    if any(word in category for word in OPTION_RESTRICTED_CATEGORY_WORDS) and len(master.options) > 1:
        issues.append(
            _issue(
                "category_option_not_supported",
                "options",
                "error",
                "해당 카테고리에 등록 가능한 옵션 구조가 아닐 수 있습니다.",
            )
        )

    if ("가전" in category or "어린이" in name) and not master.description:
        issues.append(
            _issue(
                "certification_or_required_info_missing",
                "description",
                "warning",
                "인증/고시정보가 필요한 상품일 수 있습니다. 등록 전 확인이 필요합니다.",
            )
        )

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


def _issue(code: str, field: str, severity: str, message: str) -> dict:
    return {"code": code, "field": field, "severity": severity, "message": message}
