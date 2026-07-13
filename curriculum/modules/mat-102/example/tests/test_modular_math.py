"""Normal, boundary, invalid, and invariant tests for modular_math."""

from __future__ import annotations

import unittest

from example.modular_math import (
    analyze_residue_laws,
    congruent,
    divides,
    extended_gcd,
    gcd,
    modular_inverse,
    modular_power,
)


class ModularMathTests(unittest.TestCase):
    def test_gcd_normal_sign_and_zero_cases(self) -> None:
        cases = (
            (48, 18, 6),
            (-48, 18, 6),
            (0, 9, 9),
            (9, 0, 9),
            (0, 0, 0),
        )

        for a, b, expected in cases:
            with self.subTest(a=a, b=b):
                self.assertEqual(gcd(a, b), expected)

    def test_gcd_rejects_invalid_or_unbounded_inputs(self) -> None:
        with self.assertRaises(TypeError):
            gcd(True, 2)
        with self.assertRaises(ValueError):
            gcd(10**12 + 1, 2)

    def test_extended_gcd_returns_a_bezout_witness(self) -> None:
        for a, b in ((240, 46), (-48, 18), (0, 9), (0, 0)):
            with self.subTest(a=a, b=b):
                result = extended_gcd(a, b)
                self.assertEqual(result.gcd, gcd(a, b))
                self.assertEqual(a * result.x + b * result.y, result.gcd)

    def test_divisibility_normal_boundary_and_invalid_cases(self) -> None:
        self.assertTrue(divides(7, 0))
        self.assertTrue(divides(-3, 12))
        self.assertFalse(divides(5, 12))
        with self.assertRaises(ValueError):
            divides(0, 0)

    def test_congruence_handles_negative_values_and_rejects_bad_moduli(self) -> None:
        self.assertTrue(congruent(17, 2, 5))
        self.assertTrue(congruent(-1, 4, 5))
        self.assertFalse(congruent(17, 3, 5))
        for modulus in (1, 0, -5):
            with self.subTest(modulus=modulus):
                with self.assertRaises(ValueError):
                    congruent(1, 1, modulus)

    def test_modular_inverse_exists_or_is_explicitly_absent(self) -> None:
        self.assertEqual(modular_inverse(3, 11), 4)
        self.assertEqual(modular_inverse(-3, 11), 7)
        self.assertEqual(modular_inverse(1, 2), 1)
        self.assertIsNone(modular_inverse(6, 9))
        with self.assertRaises(TypeError):
            modular_inverse(True, 11)
        with self.assertRaises(ValueError):
            modular_inverse(3, 1)

    def test_modular_power_normal_boundary_and_invalid_cases(self) -> None:
        self.assertEqual(modular_power(7, 13, 11), pow(7, 13, 11))
        self.assertEqual(modular_power(-2, 5, 7), pow(-2, 5, 7))
        self.assertEqual(modular_power(9, 0, 5), 1)
        with self.assertRaises(ValueError):
            modular_power(2, -1, 5)
        with self.assertRaises(ValueError):
            modular_power(2, 1_000_001, 5)
        with self.assertRaises(ValueError):
            modular_power(2, 3, 1)
        with self.assertRaises(TypeError):
            modular_power(2, True, 5)

    def test_law_observations_distinguish_mod_five_and_mod_six(self) -> None:
        mod_five = analyze_residue_laws(5)
        mod_six = analyze_residue_laws(6)

        for report in (mod_five, mod_six):
            self.assertTrue(report.addition_closed)
            self.assertTrue(report.multiplication_closed)
            self.assertTrue(report.addition_associative)
            self.assertTrue(report.multiplication_associative)
            self.assertTrue(report.addition_commutative)
            self.assertTrue(report.multiplication_commutative)
            self.assertTrue(report.distributive)
            self.assertEqual(report.additive_identity, 0)
            self.assertEqual(report.multiplicative_identity, 1)
            self.assertTrue(report.every_element_has_additive_inverse)

        self.assertTrue(mod_five.every_nonzero_element_has_multiplicative_inverse)
        self.assertEqual(mod_five.units, (1, 2, 3, 4))
        self.assertIsNone(mod_five.zero_divisor_witness)
        self.assertFalse(mod_six.every_nonzero_element_has_multiplicative_inverse)
        self.assertEqual(mod_six.units, (1, 5))
        self.assertIsNotNone(mod_six.zero_divisor_witness)

    def test_law_analysis_is_bounded(self) -> None:
        with self.assertRaises(ValueError):
            analyze_residue_laws(1)
        with self.assertRaises(ValueError):
            analyze_residue_laws(32)


if __name__ == "__main__":
    unittest.main()
