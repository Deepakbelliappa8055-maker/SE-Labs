"""Bike share rental input parser (fixed after fuzzing).

Deepak B - PES1UG24CS143
Every function returns None for input it cannot understand instead of
raising, because these values are typed in by users.
"""
import re

# Plain ASCII digits only: str.isdigit() would also accept characters such
# as '²' or '٣' that int() cannot always convert.
_DURATION = re.compile(r"(\d{1,3}):([0-5]\d)", re.ASCII)
_STATION = re.compile(r"([A-Z])(\d{1,4})", re.ASCII)
_MINUTES = re.compile(r"\d{1,4}", re.ASCII)
_SUBSCRIBER = {"yes": True, "no": False}


def parse_ride_duration(text):
    """
    Converts a ride duration written as HH:MM into minutes.
    Returns None if text is not a string in HH:MM form with minutes 00-59.
    """
    if not isinstance(text, str):
        return None
    match = _DURATION.fullmatch(text.strip())
    if match is None:
        return None
    hours, minutes = int(match.group(1)), int(match.group(2))
    return hours * 60 + minutes


def format_station_code(code):
    """
    Formats a station code as ZONE-NUMBER, e.g. 'a12' -> 'A-12'.
    The zone is one letter A-Z and the number is 1-4 digits.
    Returns None for anything else.
    """
    if not isinstance(code, str):
        return None
    match = _STATION.fullmatch(code.strip().upper())
    if match is None:
        return None
    return f"{match.group(1)}-{match.group(2)}"


def parse_ride_log(line):
    """
    Parses 'bike_type,minutes,subscriber' into (bike_type, minutes, is_subscriber).
    Returns None unless there are exactly three fields, a non-empty bike type,
    whole-number minutes and a subscriber value of yes or no.
    """
    if not isinstance(line, str):
        return None
    parts = [part.strip() for part in line.split(",")]
    if len(parts) != 3:
        return None
    bike_type, minutes_text, subscriber = parts
    if not bike_type or not _MINUTES.fullmatch(minutes_text):
        return None
    is_subscriber = _SUBSCRIBER.get(subscriber.lower())
    if is_subscriber is None:
        return None
    return bike_type, int(minutes_text), is_subscriber


def main():
    print("==== Running parse_ride_duration ====")
    value = input("Enter a ride duration as HH:MM (e.g. 01:15): ")
    print("Duration in minutes:", parse_ride_duration(value))

    print("\n==== Running format_station_code ====")
    value = input("Enter a station code (e.g. a12): ")
    print("Formatted station code:", format_station_code(value))

    print("\n==== Running parse_ride_log ====")
    value = input("Enter a ride log line as type,minutes,subscriber (e.g. electric,45,yes): ")
    print("Parsed ride log:", parse_ride_log(value))


if __name__ == "__main__":
    main()
