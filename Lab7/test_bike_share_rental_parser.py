"""Hypothesis fuzz tests for bike_share_rental_parser.py.

Deepak B - PES1UG24CS143
Each test feeds random text (and None) into one function. The function must
never raise; it should return a valid result or None.
"""
import pytest
from hypothesis import given, strategies as st
from bike_share_rental_parser import parse_ride_duration, format_station_code, parse_ride_log


@given(st.text() | st.none())
def test_parse_ride_duration_no_crash(s):
    try:
        result = parse_ride_duration(s)
    except Exception as exc:  # pylint: disable=broad-except
        pytest.fail(f"parse_ride_duration({s!r}) raised {type(exc).__name__}: {exc}")
    assert result is None or (isinstance(result, int) and result >= 0)


@given(st.text() | st.none())
def test_format_station_code_no_crash(s):
    try:
        result = format_station_code(s)
    except Exception as exc:  # pylint: disable=broad-except
        pytest.fail(f"format_station_code({s!r}) raised {type(exc).__name__}: {exc}")
    assert result is None or (isinstance(result, str) and "-" in result)


@given(st.text() | st.none())
def test_parse_ride_log_no_crash(s):
    try:
        result = parse_ride_log(s)
    except Exception as exc:  # pylint: disable=broad-except
        pytest.fail(f"parse_ride_log({s!r}) raised {type(exc).__name__}: {exc}")
    assert result is None or (isinstance(result, tuple) and len(result) == 3)
