from shipping import express_label, shipping_label


def test_shipping_label_format() -> None:
    assert shipping_label("Ada", "Tbilisi") == "Ada\nTbilisi"


def test_express_label_format() -> None:
    assert express_label("Ada", "Tbilisi") == "Ada\nTbilisi\nEXPRESS"


def test_shared_refactor_helper_exists() -> None:
    namespace: dict[str, object] = {}
    exec(open("shipping.py", encoding="utf-8").read(), namespace)
    assert "format_address" in namespace
