import pytest

from app.services.price_calculator import calculate_sale_price


def test_calculate_sale_price_with_margin_and_shipping() -> None:
    assert calculate_sale_price(10_000, 3_000, 0.30, 100) == 16_900


def test_calculate_sale_price_rounds_to_100_unit() -> None:
    assert calculate_sale_price(10_050, 3_000, 0.30, 100) == 17_000


def test_calculate_sale_price_rejects_zero_margin() -> None:
    with pytest.raises(ValueError):
        calculate_sale_price(10_000, 3_000, 0, 100)
