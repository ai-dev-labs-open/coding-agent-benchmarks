import time

_user_store: dict[str, tuple[object, float]] = {}
_USER_TTL = 30.0


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


def get_user(user_id: str) -> dict | None:
    cached = _get_cached(_user_store, user_id, _USER_TTL)
    if cached is not None:
        return cached  # type: ignore[return-value]
    # Simulate a DB fetch
    user = {"id": user_id, "name": f"User {user_id}"}
    _set_cached(_user_store, user_id, user, _USER_TTL)
    return user


def invalidate_user(user_id: str) -> None:
    _user_store.pop(user_id, None)
