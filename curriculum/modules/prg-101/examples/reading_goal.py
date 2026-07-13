#!/usr/bin/env python3
"""Report progress toward a daily reading goal from explicit CLI inputs."""

import sys

MAX_DAYS = 31
MAX_PAGES_PER_DAY = 10_000


def parse_integer(text, label):
    """Return text as an integer or raise a learner-readable ValueError."""
    try:
        return int(text)
    except ValueError as error:
        raise ValueError(f"{label} must be an integer: {text!r}") from error


def analyze_readings(goal, readings):
    """Return total pages and number of days that met goal."""
    if not 1 <= goal <= MAX_PAGES_PER_DAY:
        raise ValueError(f"goal must be from 1 through {MAX_PAGES_PER_DAY}")
    if not 1 <= len(readings) <= MAX_DAYS:
        raise ValueError(f"supply from 1 through {MAX_DAYS} daily readings")

    total_pages = 0
    days_meeting_goal = 0
    for pages in readings:
        if not 0 <= pages <= MAX_PAGES_PER_DAY:
            raise ValueError(
                f"each daily reading must be from 0 through {MAX_PAGES_PER_DAY}"
            )
        total_pages = total_pages + pages
        if pages >= goal:
            days_meeting_goal = days_meeting_goal + 1

    return total_pages, days_meeting_goal


def format_report(goal, readings):
    """Return the complete report as text."""
    total_pages, days_meeting_goal = analyze_readings(goal, readings)
    every_day_met = days_meeting_goal == len(readings)
    every_day_text = "yes" if every_day_met else "no"
    return "\n".join(
        (
            f"days: {len(readings)}",
            f"total pages: {total_pages}",
            f"days meeting goal: {days_meeting_goal}",
            f"goal met every day: {every_day_text}",
        )
    )


def main(arguments):
    """Translate command-line text into validated program input and output."""
    if len(arguments) < 2:
        print(
            "usage: python3 reading_goal.py GOAL READING [READING ...]",
            file=sys.stderr,
        )
        return 2

    try:
        goal = parse_integer(arguments[0], "goal")
        reading_texts = arguments[1:]
        if not 1 <= len(reading_texts) <= MAX_DAYS:
            raise ValueError(f"supply from 1 through {MAX_DAYS} daily readings")
        readings = []
        for text in reading_texts:
            label = f"reading {len(readings) + 1}"
            readings.append(parse_integer(text, label))
        report = format_report(goal, readings)
    except ValueError as error:
        print(f"error: {error}", file=sys.stderr)
        return 2

    print(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
