#!/usr/bin/env python3
"""Print one deterministic FRM-104 exact-game and simulation record."""

from __future__ import annotations

from fractions import Fraction

from game_model import (
    Strategy,
    collision_union_bound,
    hop_evidence,
    reduction_bound,
    simulate_result,
    worst_exact_advantage,
)


def main() -> int:
    copy_visible_bit = Strategy(False, False, True)
    evidence = hop_evidence(copy_visible_bit, 1, 8)
    sample = simulate_result(
        "real", copy_visible_bit, 1, 8, trials=4_096, seed=20260712
    )
    collision = collision_union_bound(32, 1 << 16)
    bound = reduction_bound(Fraction(1, 1_000_000), collision)

    print("model: finite expose-or-hide bit game v1")
    print("adversary: guess exposed payload; otherwise guess zero")
    print(f"real exact wins/trials: {evidence.real.wins}/{evidence.real.trials}")
    print(f"real exact advantage: {evidence.real.advantage}")
    print(f"ideal exact advantage: {evidence.ideal.advantage}")
    print(f"real-to-ideal win gap: {evidence.observed_gap}")
    print(f"declared bad-event bound: {evidence.bad_event_bound}")
    print(f"ideal worst deterministic advantage: {worst_exact_advantage('ideal', 1, 8)}")
    print(f"sample seed/trials/wins: {sample.seed}/{sample.trials}/{sample.wins}")
    print(f"sample win rate: {sample.win_rate:.6f}")
    print(f"collision union bound for q=32,N=65536: {collision}")
    print(f"conditional reduction sum: {bound.total}")
    print("claim limit: exact output proves only this enumerated finite model calculation")
    print("claim limit: seeded simulation is reproducible empirical evidence, not a proof")
    print("claim limit: this is not an Orange or cryptographic construction claim")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
