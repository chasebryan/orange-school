"""Executable illustrations of truth cases and explicitly finite evidence."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Final


MAX_CASES: Final = 10_000


@dataclass(frozen=True)
class FiniteCheck:
    """Result of checking an integer predicate over one finite inclusive range."""

    start: int
    requested_stop: int
    last_checked: int
    checked_count: int
    holds_on_checked_cases: bool
    counterexample: int | None


def implies(antecedent: bool, consequent: bool) -> bool:
    """Return the material implication antecedent -> consequent."""

    if type(antecedent) is not bool or type(consequent) is not bool:
        raise TypeError("implication inputs must be bool values")
    return (not antecedent) or consequent


def check_integer_claim(
    start: int,
    stop: int,
    predicate: Callable[[int], bool],
) -> FiniteCheck:
    """Check a predicate over start through stop, inclusive, within a fixed bound.

    This function returns finite computational evidence. Even when every checked
    case passes, it does not prove a claim over all integers.
    """

    if type(start) is not int or type(stop) is not int:
        raise TypeError("range endpoints must be integers")
    if not callable(predicate):
        raise TypeError("predicate must be callable")
    if start > stop:
        raise ValueError("start must be less than or equal to stop")

    case_count = stop - start + 1
    if case_count > MAX_CASES:
        raise ValueError(f"a finite check may inspect at most {MAX_CASES} cases")

    checked_count = 0
    for value in range(start, stop + 1):
        outcome = predicate(value)
        if type(outcome) is not bool:
            raise TypeError("predicate must return a bool for every checked value")
        checked_count += 1
        if not outcome:
            return FiniteCheck(
                start=start,
                requested_stop=stop,
                last_checked=value,
                checked_count=checked_count,
                holds_on_checked_cases=False,
                counterexample=value,
            )

    return FiniteCheck(
        start=start,
        requested_stop=stop,
        last_checked=stop,
        checked_count=checked_count,
        holds_on_checked_cases=True,
        counterexample=None,
    )


def triangular_sum(n: int) -> int:
    """Compute 1 + ... + n for one bounded nonnegative integer."""

    if type(n) is not int:
        raise TypeError("n must be an integer")
    if not 0 <= n <= MAX_CASES:
        raise ValueError(f"n must be from 0 through {MAX_CASES}")

    total = 0
    for value in range(1, n + 1):
        total += value
    return total
