from app.models import MasterProduct, MasterProductOption
from app.services.smartstore_validation import FORBIDDEN_TAG_WORDS


def test_forbidden_words_include_shopling_failure_examples() -> None:
    assert "헬스" in FORBIDDEN_TAG_WORDS
    assert "키링" in FORBIDDEN_TAG_WORDS
    assert "축구" in FORBIDDEN_TAG_WORDS


def test_validation_issue_shape_is_stable() -> None:
    master = MasterProduct(
        internal_product_code="MP-000001",
        supplier_product_id=1,
        product_name="헬스 덤벨 상품",
        cleaned_name="헬스 덤벨 상품",
        supply_price=10_000,
        shipping_fee=3_000,
        sale_price=16_900,
        margin_rate=0.30,
        expected_margin_amount=3_900,
        main_image_url="https://example.com/main.jpg",
        category_id="스포츠",
        status="ready",
    )
    master.options = [
        MasterProductOption(
            internal_option_code="MO-000001",
            option_name="기본",
            option_value="단일",
            sale_price=16_900,
            stock_quantity=10,
            status="active",
        )
    ]

    assert master.cleaned_name == "헬스 덤벨 상품"
