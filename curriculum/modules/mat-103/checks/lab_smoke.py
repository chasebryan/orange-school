#!/usr/bin/env python3
"""Smoke-check bounded prime-field examples using Python 3.11+ stdlib only."""

from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path


sys.dont_write_bytecode = True
MODULE_ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = MODULE_ROOT / "examples"
sys.path.insert(0, str(EXAMPLES))

from prime_field import (  # noqa: E402
    MAX_ABS_INPUT,
    MAX_EXPONENT,
    MAX_MODULUS,
    PrimeFieldValue,
    canonical_mod,
    extended_gcd,
    inverse_mod,
    is_prime,
    modular_power,
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


def check_number_theory_operations() -> None:
    require(canonical_mod(-20, 17) == 14, "negative reduction is wrong")
    gcd, left, right = extended_gcd(5, 17)
    require(gcd == 1, "gcd(5, 17) should be one")
    require(5 * left + 17 * right == gcd, "Bezout identity is wrong")
    require(inverse_mod(5, 17) == 7, "inverse of 5 modulo 17 is wrong")
    require(modular_power(5, 13, 17) == pow(5, 13, 17), "power is wrong")
    require(modular_power(0, 0, 17) == 1, "the defined zero exponent case is wrong")
    require(is_prime(2) and is_prime(65_521), "prime boundary is wrong")
    require(not is_prime(1) and not is_prime(65_520), "composite boundary is wrong")
    expect_error(TypeError, lambda: is_prime(True), "Boolean prime candidate was accepted")
    expect_error(
        ValueError,
        lambda: is_prime(MAX_MODULUS + 1),
        "oversized prime candidate was accepted",
    )
    expect_error(
        ValueError,
        lambda: extended_gcd(MAX_MODULUS + 1, 17),
        "oversized gcd operand was accepted",
    )


def check_value_type_contract() -> None:
    reduced = PrimeFieldValue(-20, 17)
    require(reduced.value == 14, "construction did not canonicalize the value")
    require(
        PrimeFieldValue(MAX_ABS_INPUT, 2).value == 0,
        "positive raw-value endpoint is wrong",
    )
    require(
        PrimeFieldValue(-MAX_ABS_INPUT, 2).value == 0,
        "negative raw-value endpoint is wrong",
    )
    require(
        PrimeFieldValue(1, MAX_MODULUS).modulus == MAX_MODULUS,
        "prime modulus endpoint was rejected",
    )
    require((PrimeFieldValue(7, 17) + PrimeFieldValue(13, 17)).value == 3, "sum is wrong")
    require((PrimeFieldValue(7, 17) - PrimeFieldValue(13, 17)).value == 11, "difference is wrong")
    require((PrimeFieldValue(7, 17) * PrimeFieldValue(13, 17)).value == 6, "product is wrong")
    require((PrimeFieldValue(13, 17) / PrimeFieldValue(7, 17)).value == 14, "quotient is wrong")
    require((PrimeFieldValue(5, 17) ** 13).value == pow(5, 13, 17), "field power is wrong")
    require(
        modular_power(2, MAX_EXPONENT, 17) == pow(2, MAX_EXPONENT, 17),
        "exponent endpoint is wrong",
    )
    require(PrimeFieldValue(5, 17).inverse().value == 7, "field inverse is wrong")

    expect_error(ValueError, lambda: PrimeFieldValue(1, 8), "composite modulus was accepted")
    expect_error(
        ZeroDivisionError,
        lambda: PrimeFieldValue(0, 17).inverse(),
        "zero was inverted",
    )
    expect_error(
        ValueError,
        lambda: PrimeFieldValue(1, 17) + PrimeFieldValue(1, 19),
        "mixed moduli were accepted",
    )
    expect_error(TypeError, lambda: PrimeFieldValue(True, 17), "bool input was accepted")
    expect_error(
        ValueError,
        lambda: PrimeFieldValue(MAX_ABS_INPUT + 1, 17),
        "oversized value was accepted",
    )
    expect_error(
        ValueError,
        lambda: PrimeFieldValue(1, MAX_MODULUS + 1),
        "oversized modulus was accepted",
    )
    expect_error(
        ValueError,
        lambda: modular_power(2, MAX_EXPONENT + 1, 17),
        "oversized exponent was accepted",
    )
    expect_error(
        ValueError,
        lambda: modular_power(2, -1, 17),
        "negative exponent was accepted",
    )


def check_small_field_and_composite_counterexample() -> None:
    values = [PrimeFieldValue(value, 7) for value in range(7)]
    zero = PrimeFieldValue(0, 7)
    one = PrimeFieldValue(1, 7)

    for left in values:
        require(left + zero == left, "additive identity failed in F_7")
        require(left * one == left, "multiplicative identity failed in F_7")
        require(left + (-left) == zero, "additive inverse failed in F_7")
        if left != zero:
            require(left * left.inverse() == one, "nonzero inverse failed in F_7")
        for right in values:
            require(left + right in values, "addition closure failed in F_7")
            require(left * right in values, "multiplication closure failed in F_7")
            for third in values:
                require(
                    left * (right + third) == left * right + left * third,
                    "distributivity failed in F_7 enumeration",
                )

    require(2 % 8 != 0 and 4 % 8 != 0, "counterexample factors must be nonzero")
    require((2 * 4) % 8 == 0, "Z/8Z zero-divisor counterexample changed")
    require((2 * 1) % 8 == (2 * 5) % 8, "cancellation counterexample changed")
    expect_error(ValueError, lambda: inverse_mod(2, 8), "2 unexpectedly inverted modulo 8")


def check_worked_program() -> None:
    with tempfile.TemporaryDirectory(prefix="mat-103-smoke-") as temporary:
        result = subprocess.run(
            [sys.executable, "-B", str(EXAMPLES / "field_worked.py")],
            cwd=temporary,
            text=True,
            capture_output=True,
            timeout=5,
            check=False,
        )
        require(result.returncode == 0, f"worked example failed: {result.stderr}")
        require(result.stderr == "", "worked example wrote a diagnostic")
        require("canonical(-20 mod 17): 14" in result.stdout, "reduction output is missing")
        require("inverse of 5 in F_17: 7" in result.stdout, "inverse output is missing")
        require("composite zero divisor: (2 * 4) mod 8 = 0" in result.stdout, "counterexample output is missing")
        evidence = Path(temporary) / "worked.stdout"
        evidence.write_text(result.stdout, encoding="utf-8")
        require(evidence.read_text(encoding="utf-8") == result.stdout, "temporary evidence changed")


def main() -> int:
    check_number_theory_operations()
    check_value_type_contract()
    check_small_field_and_composite_counterexample()
    check_worked_program()
    print("mat-103 lab smoke: PASS")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as error:
        print(f"mat-103 lab smoke: FAIL: {error}", file=sys.stderr)
        raise SystemExit(1)
