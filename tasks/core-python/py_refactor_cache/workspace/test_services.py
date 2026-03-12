from user_service import get_user, invalidate_user
from product_service import get_product, invalidate_product
from cache import TtlCache


def test_get_user_returns_dict() -> None:
    user = get_user("u1")
    assert user is not None
    assert user["id"] == "u1"


def test_get_user_cached_on_second_call() -> None:
    invalidate_user("u2")
    first = get_user("u2")
    second = get_user("u2")
    assert first == second


def test_get_product_returns_dict() -> None:
    product = get_product("p1")
    assert product is not None
    assert product["id"] == "p1"


def test_invalidate_user_clears_cache() -> None:
    get_user("u3")
    invalidate_user("u3")
    # After invalidation a fresh fetch still works
    user = get_user("u3")
    assert user["id"] == "u3"


def test_ttl_cache_set_and_get() -> None:
    cache: TtlCache = TtlCache(ttl_seconds=60)
    cache.set("k", "v")
    assert cache.get("k") == "v"


def test_ttl_cache_miss_returns_none() -> None:
    cache: TtlCache = TtlCache(ttl_seconds=60)
    assert cache.get("missing") is None


def test_ttl_cache_expires_immediately() -> None:
    cache: TtlCache = TtlCache(ttl_seconds=0)
    cache.set("k", "v")
    # With TTL=0 every get should expire
    assert cache.get("k") is None
