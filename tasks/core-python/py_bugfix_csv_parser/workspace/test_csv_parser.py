from csv_parser import parse_row


def test_simple_row() -> None:
    assert parse_row("a,b,c") == ["a", "b", "c"]


def test_quoted_field_with_comma() -> None:
    assert parse_row('"hello, world",foo,bar') == ["hello, world", "foo", "bar"]


def test_multiple_quoted_fields() -> None:
    assert parse_row('"one,two","three,four"') == ["one,two", "three,four"]


def test_unquoted_fields_unchanged() -> None:
    assert parse_row("alpha,beta,gamma") == ["alpha", "beta", "gamma"]


def test_empty_field() -> None:
    assert parse_row("a,,c") == ["a", "", "c"]
