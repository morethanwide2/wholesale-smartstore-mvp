import pytest

from app.models import MasterProduct, MasterProductOption
from app.services.smartstore.mapper import build_product_payload


def test_build_product_payload_maps_options() -> None:
    master = MasterProduct(
        internal_product_code="MP-000001",
        supplier_product_id=1,
        product_name="원본 상품명",
        cleaned_name="정제 상품명",
        supply_price=10_000,
        shipping_fee=3_000,
        sale_price=16_900,
        margin_rate=0.30,
        expected_margin_amount=3_900,
        main_image_url="https://example.com/main.jpg",
        status="ready",
    )
    master.options = [
        MasterProductOption(
            internal_option_code="MO-000001",
            option_name="색상",
            option_value="블랙",
            sale_price=16_900,
            stock_quantity=10,
            status="active",
        )
    ]

    payload = build_product_payload(master)

    assert payload["originProduct"]["name"] == "정제 상품명"
    assert payload["options"][0]["internalOptionCode"] == "MO-000001"


def test_build_product_payload_requires_name() -> None:
    master = MasterProduct(
        internal_product_code="MP-000001",
        supplier_product_id=1,
        product_name="원본 상품명",
        cleaned_name="",
        supply_price=10_000,
        shipping_fee=3_000,
        sale_price=16_900,
        margin_rate=0.30,
        expected_margin_amount=3_900,
        main_image_url="https://example.com/main.jpg",
        status="ready",
    )

    with pytest.raises(ValueError):
        build_product_payload(master)
