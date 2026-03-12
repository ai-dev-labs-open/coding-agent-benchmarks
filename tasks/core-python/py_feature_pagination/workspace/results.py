"""Utilities for working with result sets."""

from typing import TypeVar

T = TypeVar("T")


def sort_results(items: list[T], key=None, reverse: bool = False) -> list[T]:
    """Return a sorted copy of *items*."""
    return sorted(items, key=key, reverse=reverse)
