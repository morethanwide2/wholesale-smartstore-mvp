def round_price(value: float, unit: int = 100) -> int:
    if unit <= 0:
        raise ValueError("round unit must be greater than 0")
    return int(round(value / unit) * unit)
