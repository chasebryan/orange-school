#!/usr/bin/env python3
"""Print exact finite probabilities and one bounded reproducible simulation."""

from fractions import Fraction

from discrete_probability import (
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
)


def show(value: Fraction) -> str:
    return f"{value.numerator}/{value.denominator}"


def main() -> int:
    space = enumerate_binary_trials(2)
    first_one = make_event(space, lambda outcome: outcome[0] == 1)
    second_one = make_event(space, lambda outcome: outcome[1] == 1)
    at_least_one = make_event(space, lambda outcome: sum(outcome) >= 1)
    heads = lambda outcome: sum(outcome)

    print(f"P(first one): {show(probability(space, first_one))}")
    print(
        "P(first one | second one): "
        f"{show(conditional_probability(space, first_one, second_one))}"
    )
    print(f"first and second independent: {are_independent(space, first_one, second_one)}")
    print(f"E[number of ones]: {show(expectation(space, heads))}")
    print(
        f"P(first or second one): {show(union_probability(space, [first_one, second_one]))}"
    )
    print(f"union bound: {show(union_bound(space, [first_one, second_one]))}")
    print(f"P(number of ones >= 2): {show(tail_probability(space, heads, 2))}")
    print(f"Markov bound at 2: {show(markov_bound(space, heads, 2))}")
    print(f"P(at least one one): {show(probability(space, at_least_one))}")

    exact_collision = collision_probability(8, 3)
    collision_bound = collision_union_bound(8, 3)
    print(f"collision probability, 3 draws into 8: {show(exact_collision)}")
    print(f"collision union bound: {show(collision_bound)}")

    simulation = simulate_collisions(8, 3, 2_000, 20_260_712)
    error = abs(simulation.estimate - exact_collision)
    print(
        "seeded simulation: "
        f"{simulation.collisions}/{simulation.trials} = {show(simulation.estimate)}"
    )
    print(f"absolute error against exact model: {show(error)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
