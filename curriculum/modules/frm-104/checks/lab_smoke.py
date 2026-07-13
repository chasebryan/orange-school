#!/usr/bin/env python3
"""Smoke-check the bounded FRM-104 finite security-game model."""

from __future__ import annotations

from fractions import Fraction
from pathlib import Path
import subprocess
import sys
import tempfile


sys.dont_write_bytecode = True
MODULE_ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = MODULE_ROOT / "examples"
sys.path.insert(0, str(EXAMPLES))

from game_model import (  # noqa: E402
    MAX_DENOMINATOR,
    MAX_QUERY_COUNT,
    MAX_SIMULATION_TRIALS,
    MAX_SPACE_SIZE,
    Strategy,
    all_deterministic_strategies,
    collision_union_bound,
    exact_result,
    hop_evidence,
    reduction_bound,
    simulate_result,
    worst_exact_advantage,
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


def check_exact_game_and_relations() -> None:
    copy = Strategy(False, False, True)
    evidence = hop_evidence(copy, 1, 8)
    require(evidence.real.win_probability == Fraction(9, 16), "real probability changed")
    require(evidence.real.advantage == Fraction(1, 16), "real advantage changed")
    require(evidence.ideal.win_probability == Fraction(1, 2), "ideal baseline changed")
    require(evidence.ideal.advantage == 0, "ideal advantage changed")
    require(evidence.observed_gap == Fraction(1, 16), "hop gap changed")
    require(evidence.observed_gap <= evidence.bad_event_bound, "hop bound failed")

    no_bad = hop_evidence(copy, 0, MAX_DENOMINATOR)
    require(
        no_bad.real.win_probability == no_bad.ideal.win_probability
        and no_bad.real.advantage == no_bad.ideal.advantage,
        "games differ when bad event is impossible",
    )
    endpoint = hop_evidence(copy, MAX_DENOMINATOR, MAX_DENOMINATOR)
    require(endpoint.real.trials == 4 * MAX_DENOMINATOR, "exact endpoint trial count changed")
    require(endpoint.real.advantage == Fraction(1, 2), "always-exposed endpoint changed")

    for numerator in range(MAX_DENOMINATOR + 1):
        result = exact_result("real", copy, numerator, MAX_DENOMINATOR)
        require(
            result.advantage == Fraction(numerator, 2 * MAX_DENOMINATOR),
            "copy-strategy advantage relation failed",
        )
        ideal = exact_result("ideal", copy, numerator, MAX_DENOMINATOR)
        require(ideal.win_probability == Fraction(1, 2), "ideal relation failed")

    complement = Strategy(True, True, False)
    real_complement = exact_result("real", complement, 7, 16)
    require(real_complement.win_probability == Fraction(9, 32), "complement result changed")
    require(real_complement.advantage == Fraction(7, 32), "absolute advantage changed")

    strategies = all_deterministic_strategies()
    require(len(strategies) == 8 and len(set(strategies)) == 8, "strategy enumeration changed")
    require(worst_exact_advantage("ideal", 19, 64) == 0, "ideal has an impossible advantage")
    require(
        worst_exact_advantage("real", 19, 64) == Fraction(19, 128),
        "worst finite real advantage changed",
    )


def check_bounds_and_reduction() -> None:
    require(collision_union_bound(0, 1) == 0, "zero-query bound changed")
    require(collision_union_bound(1, 1) == 0, "one-query bound changed")
    require(collision_union_bound(2, 16) == Fraction(1, 16), "collision formula changed")
    require(collision_union_bound(MAX_QUERY_COUNT, 1) == 1, "capped endpoint changed")
    require(
        collision_union_bound(MAX_QUERY_COUNT, MAX_SPACE_SIZE)
        == Fraction(MAX_QUERY_COUNT * (MAX_QUERY_COUNT - 1), 2 * MAX_SPACE_SIZE),
        "query/space endpoint changed",
    )
    expect_error(
        ValueError,
        lambda: collision_union_bound(MAX_QUERY_COUNT + 1, MAX_SPACE_SIZE),
        "query one-beyond passed",
    )
    expect_error(ValueError, lambda: collision_union_bound(1, 0), "zero-size space passed")
    expect_error(
        ValueError,
        lambda: collision_union_bound(1, MAX_SPACE_SIZE + 1),
        "space one-beyond passed",
    )

    bound = reduction_bound(Fraction(1, 100), Fraction(1, 20), Fraction(1, 50))
    require(bound.total == Fraction(2, 25), "reduction terms changed")
    require(not bound.vacuous_for_bit_guessing, "useful bound called vacuous")
    loose = reduction_bound(Fraction(1, 4), Fraction(1, 4))
    require(loose.total == Fraction(1, 2), "loose sum changed")
    require(loose.vacuous_for_bit_guessing, "vacuous bit bound not marked")
    expect_error(TypeError, lambda: reduction_bound(0.1, Fraction(0)), "float bound passed")
    expect_error(
        ValueError,
        lambda: reduction_bound(Fraction(-1, 10), Fraction(0)),
        "negative bound passed",
    )


def check_simulation_and_invalid_inputs() -> None:
    copy = Strategy(False, False, True)
    first = simulate_result("real", copy, 3, 16, trials=4_096, seed=37)
    second = simulate_result("real", copy, 3, 16, trials=4_096, seed=37)
    require(first == second, "seeded simulation is not reproducible")
    require(0 <= first.wins <= first.trials, "sample wins escaped bounds")
    require(0.0 <= first.observed_advantage <= 0.5, "sample advantage escaped bounds")
    endpoint = simulate_result(
        "ideal", copy, 1, 2, trials=MAX_SIMULATION_TRIALS, seed=(1 << 64) - 1
    )
    require(endpoint.trials == MAX_SIMULATION_TRIALS, "simulation endpoint changed")

    expect_error(ValueError, lambda: exact_result("other", copy, 0, 1), "unknown game passed")
    expect_error(TypeError, lambda: exact_result("real", object(), 0, 1), "foreign strategy passed")
    expect_error(TypeError, lambda: Strategy(0, False, True), "integer strategy bit passed")
    expect_error(
        ValueError,
        lambda: copy.guess(("exposed", True)),
        "Boolean view payload was coerced",
    )
    expect_error(
        ValueError,
        lambda: copy.guess(("exposed", 1.0)),
        "floating view payload was coerced",
    )
    expect_error(ValueError, lambda: exact_result("real", copy, -1, 2), "negative numerator passed")
    expect_error(ValueError, lambda: exact_result("real", copy, 3, 2), "large numerator passed")
    expect_error(ValueError, lambda: exact_result("real", copy, 0, 0), "zero denominator passed")
    expect_error(
        ValueError,
        lambda: exact_result("real", copy, 0, MAX_DENOMINATOR + 1),
        "denominator one-beyond passed",
    )
    expect_error(TypeError, lambda: exact_result("real", copy, False, 1), "Boolean numerator passed")
    expect_error(
        ValueError,
        lambda: simulate_result("real", copy, 0, 1, trials=0, seed=1),
        "zero trials passed",
    )
    expect_error(
        ValueError,
        lambda: simulate_result(
            "real", copy, 0, 1, trials=MAX_SIMULATION_TRIALS + 1, seed=1
        ),
        "simulation one-beyond passed",
    )
    expect_error(
        TypeError,
        lambda: simulate_result("real", copy, 0, 1, trials=1, seed=True),
        "Boolean seed passed",
    )


def check_failure_sensitivity_and_worked_program() -> None:
    copy = Strategy(False, False, True)
    caught = False
    try:
        require(
            exact_result("real", copy, 1, 8).advantage == Fraction(1, 8),
            "deliberately false exact-advantage claim",
        )
    except AssertionError as error:
        caught = "deliberately false" in str(error)
    require(caught, "deliberately false exact claim did not fail")
    require(
        exact_result("real", copy, 1, 8).advantage == Fraction(1, 16),
        "restored exact claim failed",
    )

    with tempfile.TemporaryDirectory(prefix="frm-104-smoke-") as temporary:
        result = subprocess.run(
            [sys.executable, "-B", str(EXAMPLES / "worked_game.py")],
            cwd=temporary,
            text=True,
            capture_output=True,
            timeout=10,
            check=False,
        )
        require(result.returncode == 0, f"worked game failed: {result.stderr}")
        require(result.stderr == "", "worked game wrote stderr")
        require("real exact advantage: 1/16" in result.stdout, "exact result missing")
        require("seeded simulation is reproducible empirical evidence" in result.stdout, "sample limit missing")
        require("not an Orange or cryptographic construction claim" in result.stdout, "Orange limit missing")
        evidence = Path(temporary) / "worked.stdout"
        evidence.write_text(result.stdout, encoding="utf-8")
        require(evidence.read_text(encoding="utf-8") == result.stdout, "evidence replay changed")


def main() -> int:
    check_exact_game_and_relations()
    check_bounds_and_reduction()
    check_simulation_and_invalid_inputs()
    check_failure_sensitivity_and_worked_program()
    print("frm-104 lab smoke: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
