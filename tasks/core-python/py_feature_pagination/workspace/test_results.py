import pytest
from results import paginate


def test_first_page() -> None:
    assert paginate(list(range(10)), page=1, page_size=3) == [0, 1, 2]


def test_second_page() -> None:
    assert paginate(list(range(10)), page=2, page_size=3) == [3, 4, 5]


def test_last_partial_page() -> None:
    assert paginate(list(range(10)), page=4, page_size=3) == [9]


def test_beyond_last_page_returns_empty() -> None:
    assert paginate(list(range(5)), page=10, page_size=3) == []


def test_invalid_page_raises() -> None:
    with pytest.raises(ValueError):
        paginate([1, 2, 3], page=0, page_size=2)


def test_invalid_page_size_raises() -> None:
    with pytest.raises(ValueError):
        paginate([1, 2, 3], page=1, page_size=0)


def test_exact_page_boundary() -> None:
    assert paginate(list(range(6)), page=2, page_size=3) == [3, 4, 5]
