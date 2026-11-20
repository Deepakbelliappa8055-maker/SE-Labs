"""Statement (line) coverage tests for bike_share_rental.py.

Deepak B - PES1UG24CS143
Goal: execute every line of the module at least once.
"""
import pytest
from bike_share_rental import ride_cost, dock_status, can_unlock


# ---------------- ride_cost ----------------
def test_standard_ride_two_blocks():
    # 45 min -> 2 blocks of 30 min at Rs 20
    assert ride_cost("standard", 45, False, False) == 40


def test_unknown_bike_type_raises():
    with pytest.raises(ValueError, match="unknown bike type"):
        ride_cost("tandem", 30, False, False)


def test_zero_minutes_raises():
    with pytest.raises(ValueError, match="invalid duration"):
        ride_cost("standard", 0, False, False)


def test_subscriber_short_ride_is_free():
    # one block, subscriber gets one block free -> 0
    assert ride_cost("electric", 20, True, False) == 0


def test_electric_peak_long_ride_surcharges():
    # 200 min -> 7 blocks * 35 = 245, +15 peak, +100 over 3 hours
    assert ride_cost("electric", 200, False, True) == 360


# ---------------- dock_status ----------------
def test_dock_available():
    assert dock_status(5, 10) == "available"


def test_dock_invalid_capacity():
    with pytest.raises(ValueError, match="invalid capacity"):
        dock_status(0, 0)


def test_dock_invalid_bike_count():
    with pytest.raises(ValueError, match="invalid bike count"):
        dock_status(12, 10)


def test_dock_empty():
    assert dock_status(0, 10) == "empty"


def test_dock_full():
    assert dock_status(10, 10) == "full"


def test_dock_few_bikes():
    assert dock_status(2, 10) == "few bikes"


def test_dock_few_slots():
    assert dock_status(8, 10) == "few slots"


# ---------------- can_unlock ----------------
def test_active_ride_blocks_unlock():
    assert can_unlock(500, True, 30) is False


def test_under_16_blocked():
    assert can_unlock(500, False, 15) is False


def test_teen_with_enough_balance():
    assert can_unlock(100, False, 17) is True


def test_adult_with_enough_balance():
    assert can_unlock(50, False, 25) is True
