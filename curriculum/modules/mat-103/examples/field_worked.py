#!/usr/bin/env python3
"""Print one exact prime-field computation and one composite counterexample."""

from prime_field import PrimeFieldValue, canonical_mod, inverse_mod, modular_power


def main() -> int:
    modulus = 17
    five = PrimeFieldValue(5, modulus)
    seven = PrimeFieldValue(7, modulus)
    thirteen = PrimeFieldValue(13, modulus)

    print(f"canonical(-20 mod 17): {canonical_mod(-20, modulus)}")
    print(f"7 + 13 in F_17: {(seven + thirteen).value}")
    print(f"7 * 13 in F_17: {(seven * thirteen).value}")
    print(f"inverse of 5 in F_17: {five.inverse().value}")
    print(f"5 * inverse(5) in F_17: {(five * five.inverse()).value}")
    print(f"5^13 in F_17: {modular_power(5, 13, modulus)}")
    print(f"13 / 7 in F_17: {(thirteen / seven).value}")

    print(f"composite zero divisor: (2 * 4) mod 8 = {(2 * 4) % 8}")
    try:
        inverse_mod(2, 8)
    except ValueError as error:
        print(f"composite inverse failure: {error}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
