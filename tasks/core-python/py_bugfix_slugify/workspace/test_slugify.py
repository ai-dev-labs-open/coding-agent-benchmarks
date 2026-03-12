from slugify import slugify


def test_collapses_repeated_spaces() -> None:
    assert slugify("Hello   World") == "hello-world"


def test_trims_whitespace_edges() -> None:
    assert slugify("  Multiple Words  ") == "multiple-words"
