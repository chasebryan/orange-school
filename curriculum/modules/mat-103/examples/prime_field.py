#!/usr/bin/env python3
"""Bounded prime-field arithmetic with explicit construction invariants."""

from __future__ import annotations

from dataclasses import dataclass


MAX_MODULUS = 65_521
MAX_ABS_INPUT = 10**12
MAX_EXPONENT = 1_000_000


def _require_plain_int(value: object, label: str) -> int:
    """Return an exact int while rejecting bool and non-integer inputs."""

    if type(value) is not int:
        raise TypeError(f"{label} must be an integer")
    return value


def _require_bounded_integer(value: object, label: str) -> int:
    """Return an exact integer inside the example's declared input envelope."""

    integer = _require_plain_int(value, label)
    if not -MAX_ABS_INPUT <= integer <= MAX_ABS_INPUT:
        raise ValueError(
            f"{label} must be from {-MAX_ABS_INPUT} through {MAX_ABS_INPUT}"
        )
    return integer


def is_prime(candidate: object) -> bool:
    """Return whether a bounded positive integer is prime by trial division."""

    value = _require_plain_int(candidate, "candidate")
    if not 0 <= value <= MAX_MODULUS:
        raise ValueError(f"candidate must be from 0 through {MAX_MODULUS}")
    if value < 2:
        return False
    if value == 2:
        return True
    if value % 2 == 0:
        return False

    divisor = 3
    while divisor * divisor <= value:
        if value % divisor == 0:
            return False
        divisor += 2
    return True


def validate_modulus(modulus: object, *, prime_required: bool) -> int:
    """Validate the shared bounded modulus contract."""

    value = _require_plain_int(modulus, "modulus")
    if not 2 <= value <= MAX_MODULUS:
        raise ValueError(f"modulus must be from 2 through {MAX_MODULUS}")
    if prime_required and not is_prime(value):
        raise ValueError("prime-field modulus must be prime")
    return value


def canonical_mod(value: object, modulus: object) -> int:
    """Return the canonical representative in 0 through modulus minus one."""

    integer = _require_bounded_integer(value, "value")
    checked_modulus = validate_modulus(modulus, prime_required=False)
    return integer % checked_modulus


def extended_gcd(left: object, right: object) -> tuple[int, int, int]:
    """Return gcd, x, y satisfying left*x + right*y == gcd."""

    checked_left = _require_plain_int(left, "left")
    checked_right = _require_plain_int(right, "right")
    if not 0 <= checked_left <= MAX_MODULUS:
        raise ValueError(f"left must be from 0 through {MAX_MODULUS}")
    if not 1 <= checked_right <= MAX_MODULUS:
        raise ValueError(f"right must be from 1 through {MAX_MODULUS}")

    old_remainder, remainder = checked_left, checked_right
    old_x, x = 1, 0
    old_y, y = 0, 1
    while remainder != 0:
        quotient = old_remainder // remainder
        old_remainder, remainder = (
            remainder,
            old_remainder - quotient * remainder,
        )
        old_x, x = x, old_x - quotient * x
        old_y, y = y, old_y - quotient * y
    return old_remainder, old_x, old_y


def inverse_mod(value: object, modulus: object) -> int:
    """Return an inverse for a unit modulo a bounded, not necessarily prime, modulus."""

    checked_modulus = validate_modulus(modulus, prime_required=False)
    representative = canonical_mod(value, checked_modulus)
    gcd, coefficient, _ = extended_gcd(representative, checked_modulus)
    if gcd != 1:
        raise ValueError(
            f"{representative} has no inverse modulo {checked_modulus}; gcd is {gcd}"
        )
    return coefficient % checked_modulus


def modular_power(base: object, exponent: object, modulus: object) -> int:
    """Compute a bounded nonnegative power with square-and-multiply."""

    checked_base = canonical_mod(base, modulus)
    checked_modulus = validate_modulus(modulus, prime_required=False)
    checked_exponent = _require_plain_int(exponent, "exponent")
    if not 0 <= checked_exponent <= MAX_EXPONENT:
        raise ValueError(f"exponent must be from 0 through {MAX_EXPONENT}")

    result = 1 % checked_modulus
    factor = checked_base
    remaining = checked_exponent
    while remaining > 0:
        if remaining % 2 == 1:
            result = (result * factor) % checked_modulus
        factor = (factor * factor) % checked_modulus
        remaining //= 2
    return result


@dataclass(frozen=True, slots=True)
class PrimeFieldValue:
    """One canonical value in the prime field F_modulus."""

    value: int
    modulus: int

    def __post_init__(self) -> None:
        raw_value = _require_bounded_integer(self.value, "value")
        checked_modulus = validate_modulus(self.modulus, prime_required=True)
        object.__setattr__(self, "value", raw_value % checked_modulus)
        object.__setattr__(self, "modulus", checked_modulus)

    def _same_field(self, other: object) -> PrimeFieldValue:
        if not isinstance(other, PrimeFieldValue):
            raise TypeError("field operations require another PrimeFieldValue")
        if self.modulus != other.modulus:
            raise ValueError("field operands must have the same modulus")
        return other

    def __add__(self, other: object) -> PrimeFieldValue:
        checked = self._same_field(other)
        return PrimeFieldValue(self.value + checked.value, self.modulus)

    def __sub__(self, other: object) -> PrimeFieldValue:
        checked = self._same_field(other)
        return PrimeFieldValue(self.value - checked.value, self.modulus)

    def __mul__(self, other: object) -> PrimeFieldValue:
        checked = self._same_field(other)
        return PrimeFieldValue(self.value * checked.value, self.modulus)

    def __neg__(self) -> PrimeFieldValue:
        return PrimeFieldValue(-self.value, self.modulus)

    def inverse(self) -> PrimeFieldValue:
        if self.value == 0:
            raise ZeroDivisionError("zero has no multiplicative inverse")
        return PrimeFieldValue(inverse_mod(self.value, self.modulus), self.modulus)

    def __truediv__(self, other: object) -> PrimeFieldValue:
        checked = self._same_field(other)
        return self * checked.inverse()

    def __pow__(self, exponent: object) -> PrimeFieldValue:
        return PrimeFieldValue(
            modular_power(self.value, exponent, self.modulus),
            self.modulus,
        )
