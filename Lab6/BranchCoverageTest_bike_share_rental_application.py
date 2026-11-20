"""Branch coverage tests for bike_share_rental.py.

Deepak B - PES1UG24CS143
Goal: make every decision evaluate to both True and False, including the
boundary values (30/31 minutes, 180/181 minutes, ages 15/16/17/18,
balances just below and at the limit).
"""
import pytest
from bike_share_rental import ride_cost, dock_status, can_unlock


# ---------------- ride_cost ----------------
@pytest.mark.parametrize("bike", ["standard", "electric", "cargo"])
def test_every_known_bike_type_is_accepted(bike):
    assert ride_cost(bike, 30, False, False) > 0


def test_unknown_bike_type_raises():
    with pytest.raises(ValueError):
        ride_cost("scooter", 30, False, False)


@pytest.mark.parametrize("minutes", [0, -5])
def test_non_positive_duration_raises(minutes):
    with pytest.raises(ValueError):
        ride_cost("standard", minutes, False, False)


@pytest.mark.parametrize("minutes, expected", [(1, 20), (30, 20), (31, 40), (60, 40)])
def test_block_rounding(minutes, expected):
    assert ride_cost("standard", minutes, False, False) == expected


def test_subscriber_single_block_is_free():
    assert ride_cost("standard", 30, True, False) == 0


def test_subscriber_pays_after_free_block():
    # 90 min = 3 blocks, one free -> 2 * 35
    assert ride_cost("electric", 90, True, False) == 70


def test_peak_surcharge_for_standard():
    assert ride_cost("standard", 30, False, True) == 35


def test_no_peak_surcharge_for_cargo():
    assert ride_cost("cargo", 30, False, True) == 50


def test_off_peak_no_surcharge():
    assert ride_cost("cargo", 30, False, False) == 50


def test_exactly_180_minutes_no_long_ride_fee():
    assert ride_cost("standard", 180, False, False) == 120


def test_181_minutes_adds_long_ride_fee():
    # 7 blocks * 20 = 140, +100
    assert ride_cost("standard", 181, False, False) == 240


def test_subscriber_peak_long_ride_all_rules():
    # 200 min = 7 blocks, 1 free -> 6 * 50 = 300, cargo no peak, +100
    assert ride_cost("cargo", 200, True, True) == 400


# ---------------- dock_status ----------------
@pytest.mark.parametrize("capacity", [0, -3])
def test_invalid_capacity(capacity):
    with pytest.raises(ValueError):
        dock_status(0, capacity)


@pytest.mark.parametrize("bikes", [-1, 11])
def test_bike_count_out_of_range(bikes):
    with pytest.raises(ValueError):
        dock_status(bikes, 10)


@pytest.mark.parametrize("bikes, capacity, expected", [
    (0, 10, "empty"),
    (10, 10, "full"),
    (1, 10, "few bikes"),
    (2, 10, "few bikes"),
    (3, 10, "available"),
    (8, 10, "few slots"),
    (9, 10, "few slots"),
    (7, 10, "available"),
    (1, 1, "full"),
    (2, 3, "few bikes"),
])
def test_dock_status_outcomes(bikes, capacity, expected):
    assert dock_status(bikes, capacity) == expected


# ---------------- can_unlock ----------------
def test_active_ride_always_blocks():
    assert can_unlock(1000, True, 40) is False


def test_age_15_blocked():
    assert can_unlock(1000, False, 15) is False


@pytest.mark.parametrize("age", [16, 17])
@pytest.mark.parametrize("balance, expected", [(99, False), (100, True)])
def test_teen_needs_100(age, balance, expected):
    assert can_unlock(balance, False, age) is expected


@pytest.mark.parametrize("balance, expected", [(49, False), (50, True)])
def test_adult_needs_50(balance, expected):
    assert can_unlock(balance, False, 18) is expected
