def final_price(amount: float) -> float:
    """Return the final price after a threshold discount."""
    if amount > 100:
        return round(amount * 0.9, 2)
    return round(amount, 2)
