from app.utils.rounding import round_price


def calculate_sale_price(supply_price: int, shipping_fee: int, margin_rate: float, round_unit: int = 100) -> int:
    if margin_rate <= 0:
        raise ValueError("margin_rate must be greater than 0")
    base_price = supply_price + shipping_fee
    return round_price(base_price * (1 + margin_rate), round_unit)


def calculate_expected_margin(sale_price: int, supply_price: int, shipping_fee: int) -> int:
    return sale_price - supply_price - shipping_fee
