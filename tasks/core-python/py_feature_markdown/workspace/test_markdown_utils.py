from markdown_utils import bullet_list, heading


def test_heading() -> None:
    assert heading("Overview", level=2) == "## Overview"


def test_bullet_list() -> None:
    assert bullet_list(["one", "two"]) == "- one\n- two"
