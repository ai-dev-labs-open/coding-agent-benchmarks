def total_quantity(items: list[dict[str, int]]) -> int:
    return sum(item["quantity"] for item in items)
