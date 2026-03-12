def shipping_label(name: str, city: str) -> str:
    return f"{name}\n{city}"


def express_label(name: str, city: str) -> str:
    return f"{name}\n{city}\nEXPRESS"
