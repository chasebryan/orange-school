#!/usr/bin/env python3
"""Classify one bounded Celsius temperature supplied on the command line."""

import sys

MIN_CELSIUS = -100
MAX_CELSIUS = 100


def classify_temperature(celsius):
    """Return a stable label after checking the supported input range."""
    if not MIN_CELSIUS <= celsius <= MAX_CELSIUS:
        raise ValueError(
            f"temperature must be from {MIN_CELSIUS} through {MAX_CELSIUS}"
        )

    if celsius <= 0:
        return "freezing"
    if celsius < 20:
        return "cool"
    if celsius <= 29:
        return "comfortable"
    return "hot"


def main(arguments):
    if len(arguments) != 1:
        print(
            "usage: python3 temperature_advice.py CELSIUS",
            file=sys.stderr,
        )
        return 2

    try:
        celsius = int(arguments[0])
        label = classify_temperature(celsius)
    except ValueError as error:
        print(f"error: {error}", file=sys.stderr)
        return 2

    print(f"{celsius} C: {label}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
