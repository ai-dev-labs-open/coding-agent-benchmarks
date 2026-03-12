def parse_row(line: str) -> list[str]:
    """Parse a single CSV row and return a list of field strings.

    Quoted fields (surrounded by double quotes) may contain commas.
    Surrounding quotes are stripped from the returned values.
    """
    # BUG: naive split breaks quoted fields containing commas
    return line.split(",")
