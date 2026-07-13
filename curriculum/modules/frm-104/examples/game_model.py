#!/usr/bin/env python3
"""Bounded finite security-game model for FRM-104.

This teaching model demonstrates definitions and finite calculations.  It is
not a cryptographic primitive, a proof assistant, an Orange model, or evidence
that a deployed construction satisfies a security definition.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
import random
from typing import Literal


MAX_DENOMINATOR = 64
MAX_SIMULATION_TRIALS = 100_000
MAX_QUERY_COUNT = 4_096
MAX_SPACE_SIZE = 1 << 32
GameName = Literal["real", "ideal"]


@dataclass(frozen=True, slots=True)
class Strategy:
    """A deterministic adversary over the model's three possible views."""

    hidden_guess: bool
    exposed_zero_guess: bool
    exposed_one_guess: bool

    def __post_init__(self) -> None:
        for value in (
            self.hidden_guess,
            self.exposed_zero_guess,
            self.exposed_one_guess,
        ):
            if type(value) is not bool:
                raise TypeError("every strategy guess must be an exact bool")

    def guess(self, view: tuple[str, int]) -> bool:
        if (
            type(view) is not tuple
            or len(view) != 2
            or type(view[0]) is not str
            or type(view[1]) is not int
        ):
            raise ValueError("view is outside the declared game interface")
        if view == ("hidden", 0):
            return self.hidden_guess
        if view == ("exposed", 0):
            return self.exposed_zero_guess
        if view == ("exposed", 1):
            return self.exposed_one_guess
        raise ValueError("view is outside the declared game interface")


@dataclass(frozen=True, slots=True)
class ExactResult:
    game: GameName
    wins: int
    trials: int
    win_probability: Fraction
    advantage: Fraction


@dataclass(frozen=True, slots=True)
class SimulationResult:
    game: GameName
    wins: int
    trials: int
    seed: int
    win_rate: float
    observed_advantage: float


@dataclass(frozen=True, slots=True)
class HopEvidence:
    real: ExactResult
    ideal: ExactResult
    observed_gap: Fraction
    bad_event_bound: Fraction


@dataclass(frozen=True, slots=True)
class ReductionBound:
    primitive_term: Fraction
    bad_event_term: Fraction
    simulation_term: Fraction
    total: Fraction
    vacuous_for_bit_guessing: bool


def _plain_int(value: object, label: str) -> int:
    if type(value) is not int:
        raise TypeError(f"{label} must be an exact int")
    return value


def _validate_probability(numerator: object, denominator: object) -> tuple[int, int]:
    numerator = _plain_int(numerator, "trigger numerator")
    denominator = _plain_int(denominator, "trigger denominator")
    if not 1 <= denominator <= MAX_DENOMINATOR:
        raise ValueError(f"trigger denominator must be in 1..{MAX_DENOMINATOR}")
    if not 0 <= numerator <= denominator:
        raise ValueError("trigger numerator must be in 0..denominator")
    return numerator, denominator


def _validate_game(game: object) -> GameName:
    if game not in ("real", "ideal") or type(game) is not str:
        raise ValueError("game must be exactly 'real' or 'ideal'")
    return game


def _view(game: GameName, secret: bool, triggered: bool, fake: bool) -> tuple[str, int]:
    if not triggered:
        return ("hidden", 0)
    payload = secret if game == "real" else fake
    return ("exposed", int(payload))


def exact_result(
    game: GameName,
    strategy: Strategy,
    trigger_numerator: int,
    trigger_denominator: int,
) -> ExactResult:
    """Enumerate the complete aligned finite sample space using exact rationals.

    The sample space is (secret bit, trigger index, ideal fake bit).  The real
    game deliberately enumerates the unused fake bit too, so real and ideal
    probabilities have the same denominator and are directly reviewable.
    """

    game = _validate_game(game)
    if type(strategy) is not Strategy:
        raise TypeError("strategy must be an exact Strategy")
    numerator, denominator = _validate_probability(
        trigger_numerator, trigger_denominator
    )
    wins = 0
    trials = 0
    for secret in (False, True):
        for trigger_index in range(denominator):
            triggered = trigger_index < numerator
            for fake in (False, True):
                guess = strategy.guess(_view(game, secret, triggered, fake))
                wins += int(guess is secret)
                trials += 1
    probability = Fraction(wins, trials)
    return ExactResult(game, wins, trials, probability, abs(probability - Fraction(1, 2)))


def hop_evidence(
    strategy: Strategy, trigger_numerator: int, trigger_denominator: int
) -> HopEvidence:
    numerator, denominator = _validate_probability(
        trigger_numerator, trigger_denominator
    )
    real = exact_result("real", strategy, numerator, denominator)
    ideal = exact_result("ideal", strategy, numerator, denominator)
    gap = abs(real.win_probability - ideal.win_probability)
    bad = Fraction(numerator, denominator)
    if gap > bad:
        raise AssertionError("finite hop violates its declared bad-event bound")
    return HopEvidence(real, ideal, gap, bad)


def all_deterministic_strategies() -> tuple[Strategy, ...]:
    return tuple(
        Strategy(hidden, exposed_zero, exposed_one)
        for hidden in (False, True)
        for exposed_zero in (False, True)
        for exposed_one in (False, True)
    )


def worst_exact_advantage(
    game: GameName, trigger_numerator: int, trigger_denominator: int
) -> Fraction:
    return max(
        exact_result(game, strategy, trigger_numerator, trigger_denominator).advantage
        for strategy in all_deterministic_strategies()
    )


def simulate_result(
    game: GameName,
    strategy: Strategy,
    trigger_numerator: int,
    trigger_denominator: int,
    *,
    trials: int,
    seed: int,
) -> SimulationResult:
    """Run a reproducible sample; the return value is not an exact probability."""

    game = _validate_game(game)
    if type(strategy) is not Strategy:
        raise TypeError("strategy must be an exact Strategy")
    numerator, denominator = _validate_probability(
        trigger_numerator, trigger_denominator
    )
    trials = _plain_int(trials, "simulation trials")
    seed = _plain_int(seed, "simulation seed")
    if not 1 <= trials <= MAX_SIMULATION_TRIALS:
        raise ValueError(f"simulation trials must be in 1..{MAX_SIMULATION_TRIALS}")
    if not 0 <= seed <= (1 << 64) - 1:
        raise ValueError("simulation seed must be an unsigned 64-bit integer")
    generator = random.Random(seed)
    wins = 0
    for _ in range(trials):
        secret = bool(generator.randrange(2))
        triggered = generator.randrange(denominator) < numerator
        fake = bool(generator.randrange(2))
        guess = strategy.guess(_view(game, secret, triggered, fake))
        wins += int(guess is secret)
    win_rate = wins / trials
    return SimulationResult(
        game, wins, trials, seed, win_rate, abs(win_rate - 0.5)
    )


def collision_union_bound(queries: int, space_size: int) -> Fraction:
    """Return min(1, q(q-1)/(2N)); a union bound, not an exact collision rate."""

    queries = _plain_int(queries, "query count")
    space_size = _plain_int(space_size, "space size")
    if not 0 <= queries <= MAX_QUERY_COUNT:
        raise ValueError(f"query count must be in 0..{MAX_QUERY_COUNT}")
    if not 1 <= space_size <= MAX_SPACE_SIZE:
        raise ValueError(f"space size must be in 1..{MAX_SPACE_SIZE}")
    raw = Fraction(queries * (queries - 1), 2 * space_size)
    return min(Fraction(1), raw)


def reduction_bound(
    primitive_term: Fraction,
    bad_event_term: Fraction,
    simulation_term: Fraction = Fraction(0),
) -> ReductionBound:
    """Add named reduction terms without pretending they are interchangeable proof.

    ``simulation_term`` means a term justified by a mathematical simulation or
    reduction lemma.  It never means empirical Monte Carlo error.
    """

    terms = (primitive_term, bad_event_term, simulation_term)
    if any(type(term) is not Fraction for term in terms):
        raise TypeError("every reduction term must be fractions.Fraction")
    if any(term < 0 or term > 1 for term in terms):
        raise ValueError("every reduction term must be in the closed interval [0, 1]")
    total = sum(terms, Fraction(0))
    return ReductionBound(
        primitive_term,
        bad_event_term,
        simulation_term,
        total,
        total >= Fraction(1, 2),
    )
