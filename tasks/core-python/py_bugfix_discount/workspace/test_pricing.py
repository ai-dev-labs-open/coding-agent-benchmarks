from pricing import final_price


def test_discount_applies_to_exact_threshold() -> None:
    assert final_price(100) == 90.0


def test_discount_applies_above_threshold() -> None:
    assert final_price(150) == 135.0


def test_no_discount_below_threshold() -> None:
    assert final_price(50) == 50.0
