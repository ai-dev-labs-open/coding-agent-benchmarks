from inventory import low_stock_items, total_quantity


ITEMS = [
    {"name": "apples", "quantity": 5},
    {"name": "oranges", "quantity": 2},
    {"name": "bananas", "quantity": 1},
]


def test_total_quantity() -> None:
    assert total_quantity(ITEMS) == 8


def test_low_stock_items_are_sorted() -> None:
    assert low_stock_items(ITEMS, threshold=3) == ["bananas", "oranges"]
