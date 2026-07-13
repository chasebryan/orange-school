#!/usr/bin/env python3
"""Smoke-check exact probability and bounded simulation examples."""

from __future__ import annotations

from fractions import Fraction
import subprocess
import sys
import tempfile
from pathlib import Path


sys.dont_write_bytecode = True
MODULE_ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = MODULE_ROOT / "examples"
sys.path.insert(0, str(EXAMPLES))

from discrete_probability import (  # noqa: E402
    MAX_ABS_SEED,
    MAX_BINARY_TRIALS,
    MAX_BUCKETS,
    MAX_DRAWS,
    MAX_SIMULATION_TRIALS,
    are_independent,
    collision_probability,
    collision_union_bound,
    conditional_probability,
    enumerate_binary_trials,
    expectation,
    make_event,
    markov_bound,
    probability,
    simulate_collisions,
    tail_probability,
    union_bound,
    union_probability,
    validate_uniform_space,
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def expect_error(error_type: type[BaseException], action, message: str) -> None:
    try:
        action()
    except error_type:
        return
    raise AssertionError(message)


def check_space_events_and_independence() -> None:
    space = enumerate_binary_trials(3)
    first_one = make_event(space, lambda outcome: outcome[0] == 1)
    third_one = make_event(space, lambda outcome: outcome[2] == 1)
    exactly_two = make_event(space, lambda outcome: sum(outcome) == 2)

    require(len(space) == 8, "three binary trials should have eight outcomes")
    require(probability(space, first_one) == Fraction(1, 2), "event probability is wrong")
    require(
        conditional_probability(space, exactly_two, first_one) == Fraction(1, 2),
        "conditional probability is wrong",
    )
    require(are_independent(space, first_one, third_one), "coordinate events should be independent")
    require(not are_independent(space, first_one, exactly_two), "dependent events were mislabeled")
    expect_error(
        ValueError,
        lambda: conditional_probability(space, first_one, frozenset()),
        "zero-probability condition was accepted",
    )
    expect_error(
        ValueError,
        lambda: validate_uniform_space(("repeat", "repeat")),
        "duplicate outcomes were accepted",
    )
    expect_error(
        TypeError,
        lambda: make_event(space, 7),
        "non-callable event predicate was accepted",
    )
    expect_error(
        TypeError,
        lambda: make_event(space, lambda outcome: 1),
        "non-Boolean predicate result was accepted",
    )


def check_expectation_unions_and_tails() -> None:
    space = enumerate_binary_trials(3)
    exactly_two = make_event(space, lambda outcome: sum(outcome) == 2)
    third_one = make_event(space, lambda outcome: outcome[2] == 1)
    heads = lambda outcome: sum(outcome)

    require(expectation(space, heads) == Fraction(3, 2), "expectation is wrong")
    require(
        union_probability(space, [exactly_two, third_one]) == Fraction(5, 8),
        "exact union probability is wrong",
    )
    require(
        union_bound(space, [exactly_two, third_one]) == Fraction(7, 8),
        "union bound is wrong",
    )
    require(tail_probability(space, heads, 2) == Fraction(1, 2), "tail probability is wrong")
    require(markov_bound(space, heads, 2) == Fraction(3, 4), "Markov bound is wrong")
    expect_error(
        ValueError,
        lambda: markov_bound(space, lambda outcome: sum(outcome) - 2, 1),
        "negative variable was accepted for Markov",
    )


def check_collision_exactness_and_simulation() -> None:
    require(
        collision_probability(8, 3) == Fraction(11, 32),
        "exact collision probability is wrong",
    )
    require(
        collision_union_bound(8, 3) == Fraction(3, 8),
        "collision union bound is wrong",
    )
    require(collision_probability(3, 4) == 1, "pigeonhole collision should be certain")
    require(collision_probability(8, 0) == 0, "zero draws should have no collision")
    require(
        0 <= collision_probability(MAX_BUCKETS, MAX_DRAWS) <= 1,
        "collision parameter endpoints are wrong",
    )

    first = simulate_collisions(8, 3, 2_000, 20_260_712)
    repeat = simulate_collisions(8, 3, 2_000, 20_260_712)
    require(first == repeat, "same seeded simulation did not reproduce")
    require(0 <= first.estimate <= 1, "simulation estimate is not a probability")
    require(first.estimate == Fraction(first.collisions, first.trials), "estimate lost exact count")
    maximum = simulate_collisions(1, 0, MAX_SIMULATION_TRIALS, MAX_ABS_SEED)
    require(maximum.collisions == 0, "maximum-trial zero-draw boundary is wrong")
    expect_error(
        ValueError,
        lambda: simulate_collisions(8, 3, MAX_SIMULATION_TRIALS + 1, 1),
        "oversized simulation was accepted",
    )
    expect_error(
        ValueError,
        lambda: enumerate_binary_trials(MAX_BINARY_TRIALS + 1),
        "oversized enumeration was accepted",
    )
    require(
        len(enumerate_binary_trials(MAX_BINARY_TRIALS)) == 2**MAX_BINARY_TRIALS,
        "maximum enumeration boundary is wrong",
    )
    expect_error(
        TypeError,
        lambda: simulate_collisions(True, 3, 10, 1),
        "Boolean bucket count was accepted",
    )
    expect_error(
        ValueError,
        lambda: simulate_collisions(8, MAX_DRAWS + 1, 10, 1),
        "oversized draw count was accepted",
    )

    source = (EXAMPLES / "discrete_probability.py").read_text(encoding="utf-8")
    require(
        "not a cryptographic generator" in source,
        "simulation source lost its cryptographic-randomness boundary",
    )


def check_worked_program() -> None:
    with tempfile.TemporaryDirectory(prefix="mat-104-smoke-") as temporary:
        result = subprocess.run(
            [sys.executable, "-B", str(EXAMPLES / "probability_worked.py")],
            cwd=temporary,
            text=True,
            capture_output=True,
            timeout=8,
            check=False,
        )
        require(result.returncode == 0, f"worked example failed: {result.stderr}")
        require(result.stderr == "", "worked example wrote a diagnostic")
        require("P(first one): 1/2" in result.stdout, "event output is missing")
        require("E[number of ones]: 1/1" in result.stdout, "expectation output is missing")
        require(
            "collision probability, 3 draws into 8: 11/32" in result.stdout,
            "collision output is missing",
        )
        require("absolute error against exact model:" in result.stdout, "error record is missing")
        evidence = Path(temporary) / "worked.stdout"
        evidence.write_text(result.stdout, encoding="utf-8")
        require(evidence.read_text(encoding="utf-8") == result.stdout, "temporary evidence changed")


def main() -> int:
    check_space_events_and_independence()
    check_expectation_unions_and_tails()
    check_collision_exactness_and_simulation()
    check_worked_program()
    print("mat-104 lab smoke: PASS")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as error:
        print(f"mat-104 lab smoke: FAIL: {error}", file=sys.stderr)
        raise SystemExit(1)
