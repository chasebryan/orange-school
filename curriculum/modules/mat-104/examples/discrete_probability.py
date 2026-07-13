#!/usr/bin/env python3
"""Exact finite probability calculations plus bounded educational simulation."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from itertools import product
import random
from typing import Callable, Hashable, Iterable


MAX_SPACE_SIZE = 65_536
MAX_BINARY_TRIALS = 16
MAX_BUCKETS = 100_000
MAX_DRAWS = 100
MAX_SIMULATION_TRIALS = 100_000
MAX_ABS_SEED = 2**63 - 1


Outcome = Hashable
Event = frozenset[Outcome]


def _require_plain_int(value: object, label: str) -> int:
    if type(value) is not int:
        raise TypeError(f"{label} must be an integer")
    return value


def _exact_number(value: object, label: str) -> Fraction:
    if type(value) is int or isinstance(value, Fraction):
        return Fraction(value)
    raise TypeError(f"{label} must be an int or Fraction")


def validate_uniform_space(space: Iterable[Outcome]) -> tuple[Outcome, ...]:
    """Return a bounded tuple of distinct, equally likely outcomes."""

    outcomes = tuple(space)
    if not 1 <= len(outcomes) <= MAX_SPACE_SIZE:
        raise ValueError(f"sample space must contain 1 through {MAX_SPACE_SIZE} outcomes")
    try:
        distinct_count = len(set(outcomes))
    except TypeError as error:
        raise TypeError("sample-space outcomes must be hashable") from error
    if distinct_count != len(outcomes):
        raise ValueError("sample-space outcomes must be distinct")
    return outcomes


def make_event(space: Iterable[Outcome], predicate: Callable[[Outcome], bool]) -> Event:
    """Return the subset of outcomes for which predicate is true."""

    outcomes = validate_uniform_space(space)
    if not callable(predicate):
        raise TypeError("event predicate must be callable")
    selected: set[Outcome] = set()
    for outcome in outcomes:
        decision = predicate(outcome)
        if type(decision) is not bool:
            raise TypeError("event predicate must return bool for every outcome")
        if decision:
            selected.add(outcome)
    return frozenset(selected)


def _validated_event(space: tuple[Outcome, ...], event: Iterable[Outcome]) -> Event:
    try:
        values = frozenset(event)
    except TypeError as error:
        raise TypeError("event outcomes must be hashable") from error
    if not values <= frozenset(space):
        raise ValueError("event must be a subset of the sample space")
    return values


def probability(space: Iterable[Outcome], event: Iterable[Outcome]) -> Fraction:
    """Return an exact probability for an event in a finite uniform space."""

    outcomes = validate_uniform_space(space)
    values = _validated_event(outcomes, event)
    return Fraction(len(values), len(outcomes))


def conditional_probability(
    space: Iterable[Outcome],
    event: Iterable[Outcome],
    given: Iterable[Outcome],
) -> Fraction:
    """Return P(event | given), rejecting a zero-probability condition."""

    outcomes = validate_uniform_space(space)
    event_values = _validated_event(outcomes, event)
    given_values = _validated_event(outcomes, given)
    if not given_values:
        raise ValueError("conditioning event must have positive probability")
    return Fraction(len(event_values & given_values), len(given_values))


def are_independent(
    space: Iterable[Outcome],
    left: Iterable[Outcome],
    right: Iterable[Outcome],
) -> bool:
    """Return whether P(left intersect right) equals P(left) times P(right)."""

    outcomes = validate_uniform_space(space)
    left_values = _validated_event(outcomes, left)
    right_values = _validated_event(outcomes, right)
    intersection = probability(outcomes, left_values & right_values)
    return intersection == probability(outcomes, left_values) * probability(
        outcomes, right_values
    )


def expectation(
    space: Iterable[Outcome],
    random_variable: Callable[[Outcome], int | Fraction],
) -> Fraction:
    """Return the exact expectation of a bounded variable on a uniform space."""

    outcomes = validate_uniform_space(space)
    total = Fraction(0)
    for outcome in outcomes:
        total += _exact_number(random_variable(outcome), "random-variable value")
    return total / len(outcomes)


def union_probability(
    space: Iterable[Outcome], events: Iterable[Iterable[Outcome]]
) -> Fraction:
    """Return the exact probability of the union of finitely many events."""

    outcomes = validate_uniform_space(space)
    union: set[Outcome] = set()
    for event in events:
        union.update(_validated_event(outcomes, event))
    return probability(outcomes, union)


def union_bound(
    space: Iterable[Outcome], events: Iterable[Iterable[Outcome]]
) -> Fraction:
    """Return min(1, sum of event probabilities), an exact rational upper bound."""

    outcomes = validate_uniform_space(space)
    total = Fraction(0)
    for event in events:
        total += probability(outcomes, event)
    return min(Fraction(1), total)


def tail_probability(
    space: Iterable[Outcome],
    random_variable: Callable[[Outcome], int | Fraction],
    threshold: int | Fraction,
) -> Fraction:
    """Return the exact probability that the variable is at least threshold."""

    outcomes = validate_uniform_space(space)
    checked_threshold = _exact_number(threshold, "threshold")
    tail = make_event(
        outcomes,
        lambda outcome: _exact_number(
            random_variable(outcome), "random-variable value"
        )
        >= checked_threshold,
    )
    return probability(outcomes, tail)


def markov_bound(
    space: Iterable[Outcome],
    random_variable: Callable[[Outcome], int | Fraction],
    threshold: int | Fraction,
) -> Fraction:
    """Return the exact Markov upper bound for a nonnegative variable."""

    outcomes = validate_uniform_space(space)
    checked_threshold = _exact_number(threshold, "threshold")
    if checked_threshold <= 0:
        raise ValueError("Markov threshold must be positive")
    values = [
        _exact_number(random_variable(outcome), "random-variable value")
        for outcome in outcomes
    ]
    if any(value < 0 for value in values):
        raise ValueError("Markov bound requires a nonnegative random variable")
    mean = sum(values, Fraction(0)) / len(values)
    return min(Fraction(1), mean / checked_threshold)


def collision_probability(bucket_count: object, draw_count: object) -> Fraction:
    """Return the exact collision probability for uniform draws with replacement."""

    buckets = _require_plain_int(bucket_count, "bucket_count")
    draws = _require_plain_int(draw_count, "draw_count")
    if not 1 <= buckets <= MAX_BUCKETS:
        raise ValueError(f"bucket_count must be from 1 through {MAX_BUCKETS}")
    if not 0 <= draws <= MAX_DRAWS:
        raise ValueError(f"draw_count must be from 0 through {MAX_DRAWS}")
    if draws > buckets:
        return Fraction(1)

    no_collision_numerator = 1
    for offset in range(draws):
        no_collision_numerator *= buckets - offset
    no_collision = Fraction(no_collision_numerator, buckets**draws)
    return 1 - no_collision


def collision_union_bound(bucket_count: object, draw_count: object) -> Fraction:
    """Return min(1, choose(draws, 2) / buckets)."""

    buckets = _require_plain_int(bucket_count, "bucket_count")
    draws = _require_plain_int(draw_count, "draw_count")
    if not 1 <= buckets <= MAX_BUCKETS:
        raise ValueError(f"bucket_count must be from 1 through {MAX_BUCKETS}")
    if not 0 <= draws <= MAX_DRAWS:
        raise ValueError(f"draw_count must be from 0 through {MAX_DRAWS}")
    pair_bound = Fraction(draws * (draws - 1), 2 * buckets)
    return min(Fraction(1), pair_bound)


def enumerate_binary_trials(trial_count: object) -> tuple[tuple[int, ...], ...]:
    """Enumerate at most 2**16 ordered binary outcomes."""

    trials = _require_plain_int(trial_count, "trial_count")
    if not 0 <= trials <= MAX_BINARY_TRIALS:
        raise ValueError(f"trial_count must be from 0 through {MAX_BINARY_TRIALS}")
    return tuple(product((0, 1), repeat=trials))


@dataclass(frozen=True, slots=True)
class SimulationResult:
    """Observed collision count and exact rational estimate for one seeded run."""

    collisions: int
    trials: int
    estimate: Fraction
    seed: int


def simulate_collisions(
    bucket_count: object,
    draw_count: object,
    trial_count: object,
    seed: object,
) -> SimulationResult:
    """Run a reproducible teaching simulation, not a cryptographic generator."""

    buckets = _require_plain_int(bucket_count, "bucket_count")
    draws = _require_plain_int(draw_count, "draw_count")
    trials = _require_plain_int(trial_count, "trial_count")
    checked_seed = _require_plain_int(seed, "seed")
    if not 1 <= buckets <= MAX_BUCKETS:
        raise ValueError(f"bucket_count must be from 1 through {MAX_BUCKETS}")
    if not 0 <= draws <= MAX_DRAWS:
        raise ValueError(f"draw_count must be from 0 through {MAX_DRAWS}")
    if not 1 <= trials <= MAX_SIMULATION_TRIALS:
        raise ValueError(
            f"trial_count must be from 1 through {MAX_SIMULATION_TRIALS}"
        )
    if not -MAX_ABS_SEED <= checked_seed <= MAX_ABS_SEED:
        raise ValueError(
            f"seed must be from {-MAX_ABS_SEED} through {MAX_ABS_SEED}"
        )

    generator = random.Random(checked_seed)
    collisions = 0
    for _ in range(trials):
        seen: set[int] = set()
        collision_seen = False
        for _ in range(draws):
            bucket = generator.randrange(buckets)
            if bucket in seen:
                collision_seen = True
            seen.add(bucket)
        if collision_seen:
            collisions += 1
    return SimulationResult(
        collisions=collisions,
        trials=trials,
        estimate=Fraction(collisions, trials),
        seed=checked_seed,
    )
