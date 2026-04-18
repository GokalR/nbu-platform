"""Tests for app.services.excel_parser — helper functions only.

We only test _as_num and _row_code_and_values since actual Excel parsing
(parse_balance, parse_pnl) would require fixture .xlsx files.
"""

import re

from app.services.excel_parser import _as_num, _row_code_and_values, CODE_RE


class TestAsNum:
    def test_converts_string_number(self):
        assert _as_num("1234") == 1234.0

    def test_converts_string_float(self):
        assert _as_num("12.34") == 12.34

    def test_returns_none_for_non_numeric(self):
        assert _as_num("abc") is None

    def test_returns_none_for_none(self):
        assert _as_num(None) is None

    def test_returns_none_for_bool(self):
        # bool is a subclass of int, but the function explicitly handles it
        assert _as_num(True) is None
        assert _as_num(False) is None

    def test_converts_int(self):
        assert _as_num(42) == 42.0

    def test_converts_float(self):
        assert _as_num(3.14) == 3.14

    def test_returns_none_for_dash(self):
        assert _as_num("-") is None
        assert _as_num("—") is None

    def test_returns_none_for_x(self):
        assert _as_num("x") is None
        assert _as_num("X") is None

    def test_returns_none_for_empty_string(self):
        assert _as_num("") is None

    def test_handles_string_with_spaces(self):
        # "1 234" is a common Uzbek/Russian number formatting
        assert _as_num("1 234") == 1234.0

    def test_handles_comma_as_decimal_separator(self):
        assert _as_num("12,34") == 12.34

    def test_handles_whitespace_padding(self):
        assert _as_num("  42  ") == 42.0


class TestCodeRe:
    def test_matches_three_digit_code(self):
        assert CODE_RE.match("010")
        assert CODE_RE.match("390")
        assert CODE_RE.match("770")

    def test_does_not_match_two_digits(self):
        assert CODE_RE.match("01") is None

    def test_does_not_match_four_digits(self):
        assert CODE_RE.match("0100") is None

    def test_does_not_match_letters(self):
        assert CODE_RE.match("abc") is None


class TestRowCodeAndValues:
    def test_extracts_code_and_values(self):
        row = (None, "Some label", "010", 1000, 2000, 3000)
        code, vals = _row_code_and_values(row)
        assert code == "010"
        assert len(vals) == 3

    def test_returns_none_when_no_code(self):
        row = (None, "Some label", "not a code", "abc")
        code, vals = _row_code_and_values(row)
        assert code is None
        assert vals == []

    def test_values_are_converted_via_as_num(self):
        row = ("010", "1234", "abc", None)
        code, vals = _row_code_and_values(row)
        assert code == "010"
        # vals should be [_as_num("1234"), _as_num("abc"), _as_num(None)]
        assert vals[0] == 1234.0
        assert vals[1] is None
        assert vals[2] is None
