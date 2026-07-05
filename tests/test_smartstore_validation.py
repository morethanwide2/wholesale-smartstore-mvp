from app.models import MasterProduct, MasterProductOption
from app.services.smartstore_validation import FORBIDDEN_TAG_WORDS, validate_master_product_shape


def test_forbidden_words_include_shopling_failure_examples() -> None:
    assert "헬스" in FORBIDDEN_TAG_WORDS
    assert "덤벨" in FORBIDDEN_TAG_WORDS
    assert "키링" in FORBIDDEN_TAG_WORDS


def test_validation_catches_missing_market_required_data() -> None:
    master = MasterProduct(
        internal_product_code="MP-000001",
        supplier_product_id=1,
        product_name="테스트 상품",
        cleaned_name="테스트 상품",
        supply_price=10_000,
        shipping_fee=3_000,
        sale_price=16_900,
        margin_rate=0.30,
        expected_margin_amount=3_900,
        category_id="생활용품",
        status="ready",
    )
    master.options = [
        MasterProductOption(
            internal_option_code="MO-000001",
            option_name="색상",
            option_value="화이트",
            sale_price=16_900,
            stock_quantity=10,
            status="active",
        )
    ]

    result = validate_master_product_shape(master)

    assert result["valid"] is False
    assert any(issue["code"] == "missing_main_image" for issue in result["issues"])


def test_validation_passes_when_core_listing_data_exists() -> None:
    master = MasterProduct(
        internal_product_code="MP-000002",
        supplier_product_id=1,
        product_name="스테인리스 텀블러 500ml",
        cleaned_name="스테인리스 텀블러 500ml",
        description="일상용 텀블러 상세설명",
        category_id="생활용품",
        brand="무브랜드",
        manufacturer="테스트 제조사",
        origin="중국",
        supply_price=9_500,
        shipping_fee=3_000,
        sale_price=16_200,
        margin_rate=0.30,
        expected_margin_amount=3_700,
        main_image_url="https://example.com/main.jpg",
        status="ready",
    )
    master.options = [
        MasterProductOption(
            internal_option_code="MO-000002",
            option_name="기본",
            option_value="단일",
            sale_price=16_200,
            stock_quantity=10,
            status="active",
        )
    ]

    result = validate_master_product_shape(master)

    assert result["valid"] is True
    assert result["error_count"] == 0
