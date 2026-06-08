from app import _parse_float


def test_parse_float_handles_negative_integer():
    assert _parse_float("-5\u00b0F") == -5.0


def test_parse_float_handles_negative_decimal():
    assert _parse_float("wind chill -12.5 F") == -12.5


def test_parse_float_still_handles_positive_decimal():
    assert _parse_float("Pressure: 29.85 in") == 29.85
