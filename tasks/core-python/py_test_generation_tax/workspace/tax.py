def add_tax(amount: float, rate: float = 0.1) -> float:
    return round(amount * (1 + rate), 2)
