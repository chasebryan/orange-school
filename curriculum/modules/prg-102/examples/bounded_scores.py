#!/usr/bin/env python3
"""Search, count, deduplicate, and order a bounded sequence of scores."""

import sys

MIN_SCORE = 0
MAX_SCORE = 100
MAX_ITEMS = 100


def validate_scores(scores):
    """Reject empty, oversized, or out-of-range input before processing."""
    if not 1 <= len(scores) <= MAX_ITEMS:
        raise ValueError(f"supply from 1 through {MAX_ITEMS} scores")
    for score in scores:
        if not MIN_SCORE <= score <= MAX_SCORE:
            raise ValueError(f"each score must be from {MIN_SCORE} through {MAX_SCORE}")


def find_first(scores, target):
    """Return the first matching index or None using a linear search."""
    for index, score in enumerate(scores):
        if score == target:
            return index
    return None


def count_values(scores):
    """Return a mapping from each score to its occurrence count."""
    counts = {}
    for score in scores:
        counts[score] = counts.get(score, 0) + 1
    return counts


def unique_in_order(scores):
    """Return first occurrences in input order."""
    seen = set()
    result = []
    for score in scores:
        if score not in seen:
            seen.add(score)
            result.append(score)
    return result


def ordered_copy(scores):
    """Return an immutable ordered snapshot without changing the input list."""
    return tuple(sorted(scores))


def format_numbers(values):
    return ", ".join(str(value) for value in values)


def make_report(target, scores):
    validate_scores(scores)
    if not MIN_SCORE <= target <= MAX_SCORE:
        raise ValueError(f"target must be from {MIN_SCORE} through {MAX_SCORE}")

    first = find_first(scores, target)
    counts = count_values(scores)
    unique = unique_in_order(scores)
    ordered = ordered_copy(scores)
    first_text = "not found" if first is None else str(first)
    return "\n".join(
        (
            f"first target index: {first_text}",
            f"target count: {counts.get(target, 0)}",
            f"unique in input order: {format_numbers(unique)}",
            f"all scores ordered: {format_numbers(ordered)}",
        )
    )


def parse_integer(text, label):
    try:
        return int(text)
    except ValueError as error:
        raise ValueError(f"{label} must be an integer: {text!r}") from error


def main(arguments):
    if len(arguments) < 2:
        print(
            "usage: python3 bounded_scores.py TARGET SCORE [SCORE ...]",
            file=sys.stderr,
        )
        return 2

    try:
        target = parse_integer(arguments[0], "target")
        score_texts = arguments[1:]
        if not 1 <= len(score_texts) <= MAX_ITEMS:
            raise ValueError(f"supply from 1 through {MAX_ITEMS} scores")
        scores = []
        for text in score_texts:
            label = f"score {len(scores) + 1}"
            scores.append(parse_integer(text, label))
        report = make_report(target, scores)
    except ValueError as error:
        print(f"error: {error}", file=sys.stderr)
        return 2

    print(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
