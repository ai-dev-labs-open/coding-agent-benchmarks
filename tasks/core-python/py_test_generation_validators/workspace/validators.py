"""Input validation helpers."""

import re


def validate_email(value: str) -> str:
    """Return the lower-cased email if valid, else raise ValueError.

    Rules:
    - Must contain exactly one '@'.
    - Local part (before '@') must be non-empty.
    - Domain part (after '@') must contain at least one '.'.
    - Domain part must not start or end with '.'.
    """
    value = value.strip()
    if value.count("@") != 1:
        raise ValueError(f"Email must contain exactly one '@': {value!r}")
    local, domain = value.split("@")
    if not local:
        raise ValueError(f"Email local part must not be empty: {value!r}")
    if "." not in domain:
        raise ValueError(f"Email domain must contain a '.': {value!r}")
    if domain.startswith(".") or domain.endswith("."):
        raise ValueError(f"Email domain must not start or end with '.': {value!r}")
    return value.lower()


def validate_age(value: int) -> int:
    """Return *value* if it is a valid age, else raise ValueError.

    Rules:
    - Must be an integer.
    - Must be between 0 and 150 inclusive.
    """
    if not isinstance(value, int):
        raise ValueError(f"Age must be an integer, got {type(value).__name__}")
    if value < 0 or value > 150:
        raise ValueError(f"Age must be between 0 and 150, got {value}")
    return value


def validate_username(value: str) -> str:
    """Return *value* if it is a valid username, else raise ValueError.

    Rules:
    - Must be between 3 and 20 characters long.
    - May only contain letters, digits, underscores, and hyphens.
    - Must not start or end with an underscore or hyphen.
    """
    if len(value) < 3 or len(value) > 20:
        raise ValueError(
            f"Username must be 3–20 characters long, got {len(value)}: {value!r}"
        )
    if not re.fullmatch(r"[a-zA-Z0-9_-]+", value):
        raise ValueError(
            f"Username may only contain letters, digits, '_', and '-': {value!r}"
        )
    if value[0] in "_-" or value[-1] in "_-":
        raise ValueError(
            f"Username must not start or end with '_' or '-': {value!r}"
        )
    return value
