"""Bounded algorithms and finite algebra-law observations for MAT-102."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final


MAX_ABS_INPUT: Final = 10**12
MAX_EXPONENT: Final = 1_000_000
MAX_LAW_MODULUS: Final = 31


@dataclass(frozen=True)
class BezoutResult:
    """A nonnegative gcd and coefficients satisfying a*x + b*y = gcd."""

    gcd: int
    x: int
    y: int


@dataclass(frozen=True)
class LawObservations:
    """Exhaustive computational observations for one small residue system."""

    modulus: int
    addition_closed: bool
    multiplication_closed: bool
    addition_associative: bool
    multiplication_associative: bool
    addition_commutative: bool
    multiplication_commutative: bool
    distributive: bool
    additive_identity: int | None
    multiplicative_identity: int | None
    every_element_has_additive_inverse: bool
    every_nonzero_element_has_multiplicative_inverse: bool
    units: tuple[int, ...]
    zero_divisor_witness: tuple[int, int] | None


def _require_bounded_int(name: str, value: object) -> int:
    if type(value) is not int:
        raise TypeError(f"{name} must be an integer")
    if abs(value) > MAX_ABS_INPUT:
        raise ValueError(f"absolute {name} must not exceed {MAX_ABS_INPUT}")
    return value


def _require_modulus(modulus: object) -> int:
    value = _require_bounded_int("modulus", modulus)
    if value < 2:
        raise ValueError("modulus must be at least 2")
    return value


def gcd(a: int, b: int) -> int:
    """Return the nonnegative greatest common divisor of two bounded integers."""

    left = abs(_require_bounded_int("a", a))
    right = abs(_require_bounded_int("b", b))
    while right != 0:
        left, right = right, left % right
    return left


def extended_gcd(a: int, b: int) -> BezoutResult:
    """Return gcd(a, b) and Bezout coefficients for bounded integers."""

    checked_a = _require_bounded_int("a", a)
    checked_b = _require_bounded_int("b", b)
    old_remainder, remainder = abs(checked_a), abs(checked_b)
    old_x, x = 1, 0
    old_y, y = 0, 1

    while remainder != 0:
        quotient = old_remainder // remainder
        old_remainder, remainder = remainder, old_remainder - quotient * remainder
        old_x, x = x, old_x - quotient * x
        old_y, y = y, old_y - quotient * y

    coefficient_x = old_x if checked_a >= 0 else -old_x
    coefficient_y = old_y if checked_b >= 0 else -old_y
    return BezoutResult(old_remainder, coefficient_x, coefficient_y)


def divides(divisor: int, value: int) -> bool:
    """Return whether a nonzero bounded divisor divides a bounded integer."""

    checked_divisor = _require_bounded_int("divisor", divisor)
    checked_value = _require_bounded_int("value", value)
    if checked_divisor == 0:
        raise ValueError("this function requires a nonzero divisor")
    return checked_value % checked_divisor == 0


def congruent(a: int, b: int, modulus: int) -> bool:
    """Return whether a and b are congruent modulo a positive modulus."""

    checked_a = _require_bounded_int("a", a)
    checked_b = _require_bounded_int("b", b)
    checked_modulus = _require_modulus(modulus)
    return (checked_a - checked_b) % checked_modulus == 0


def modular_inverse(value: int, modulus: int) -> int | None:
    """Return the canonical inverse or None when no inverse exists."""

    checked_value = _require_bounded_int("value", value)
    checked_modulus = _require_modulus(modulus)
    result = extended_gcd(checked_value, checked_modulus)
    if result.gcd != 1:
        return None
    return result.x % checked_modulus


def modular_power(base: int, exponent: int, modulus: int) -> int:
    """Compute base**exponent modulo modulus by bounded square-and-multiply."""

    checked_base = _require_bounded_int("base", base)
    checked_exponent = _require_bounded_int("exponent", exponent)
    checked_modulus = _require_modulus(modulus)
    if not 0 <= checked_exponent <= MAX_EXPONENT:
        raise ValueError(f"exponent must be from 0 through {MAX_EXPONENT}")

    result = 1 % checked_modulus
    factor = checked_base % checked_modulus
    remaining = checked_exponent
    while remaining > 0:
        if remaining % 2 == 1:
            result = (result * factor) % checked_modulus
        factor = (factor * factor) % checked_modulus
        remaining //= 2
    return result


def analyze_residue_laws(modulus: int) -> LawObservations:
    """Exhaustively observe selected laws for residues modulo one small modulus.

    The result is evidence about this implementation and this finite modulus. It
    is not a proof of a theorem about every modulus or of Python's correctness.
    """

    checked_modulus = _require_modulus(modulus)
    if checked_modulus > MAX_LAW_MODULUS:
        raise ValueError(f"law analysis supports moduli through {MAX_LAW_MODULUS}")
    residues = tuple(range(checked_modulus))

    def add(a: int, b: int) -> int:
        return (a + b) % checked_modulus

    def multiply(a: int, b: int) -> int:
        return (a * b) % checked_modulus

    addition_closed = all(add(a, b) in residues for a in residues for b in residues)
    multiplication_closed = all(
        multiply(a, b) in residues for a in residues for b in residues
    )
    addition_associative = all(
        add(add(a, b), c) == add(a, add(b, c))
        for a in residues
        for b in residues
        for c in residues
    )
    multiplication_associative = all(
        multiply(multiply(a, b), c) == multiply(a, multiply(b, c))
        for a in residues
        for b in residues
        for c in residues
    )
    addition_commutative = all(
        add(a, b) == add(b, a)
        for a in residues
        for b in residues
    )
    multiplication_commutative = all(
        multiply(a, b) == multiply(b, a)
        for a in residues
        for b in residues
    )
    distributive = all(
        multiply(a, add(b, c)) == add(multiply(a, b), multiply(a, c))
        for a in residues
        for b in residues
        for c in residues
    ) and all(
        multiply(add(a, b), c) == add(multiply(a, c), multiply(b, c))
        for a in residues
        for b in residues
        for c in residues
    )

    additive_identities = tuple(
        candidate
        for candidate in residues
        if all(
            add(candidate, value) == value and add(value, candidate) == value
            for value in residues
        )
    )
    multiplicative_identities = tuple(
        candidate
        for candidate in residues
        if all(
            multiply(candidate, value) == value
            and multiply(value, candidate) == value
            for value in residues
        )
    )
    every_additive_inverse = all(
        any(add(value, candidate) == 0 for candidate in residues)
        for value in residues
    )
    units = tuple(value for value in residues if gcd(value, checked_modulus) == 1)
    every_nonzero_inverse = len(units) == checked_modulus - 1

    zero_divisor_witness = next(
        (
            (a, b)
            for a in residues[1:]
            for b in residues[1:]
            if multiply(a, b) == 0
        ),
        None,
    )

    return LawObservations(
        modulus=checked_modulus,
        addition_closed=addition_closed,
        multiplication_closed=multiplication_closed,
        addition_associative=addition_associative,
        multiplication_associative=multiplication_associative,
        addition_commutative=addition_commutative,
        multiplication_commutative=multiplication_commutative,
        distributive=distributive,
        additive_identity=additive_identities[0] if additive_identities else None,
        multiplicative_identity=(
            multiplicative_identities[0] if multiplicative_identities else None
        ),
        every_element_has_additive_inverse=every_additive_inverse,
        every_nonzero_element_has_multiplicative_inverse=every_nonzero_inverse,
        units=units,
        zero_divisor_witness=zero_divisor_witness,
    )
