import time

_product_store: dict[str, tuple[object, float]] = {}
_PRODUCT_TTL = 60.0


def _get_cached(store: dict, key: str, ttl: float):
    entry = store.get(key)
    if entry is None:
        return None
    value, ts = entry
    if time.monotonic() - ts > ttl:
        del store[key]
        return None
    return value


def _set_cached(store: dict, key: str, value: object, ttl: float) -> None:
    store[key] = (value, time.monotonic())


def get_product(product_id: str) -> dict | None:
    cached = _get_cached(_product_store, product_id, _PRODUCT_TTL)
    if cached is not None:
        return cached  # type: ignore[return-value]
    product = {"id": product_id, "name": f"Product {product_id}"}
    _set_cached(_product_store, product_id, product, _PRODUCT_TTL)
    return product


def invalidate_product(product_id: str) -> None:
    _product_store.pop(product_id, None)
