#!/usr/bin/env python3
"""Smoke-check MAT-102 examples with Python's standard library."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path


MODULE_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(MODULE_ROOT))

from example.modular_math import (  # noqa: E402
    analyze_residue_laws,
    extended_gcd,
    modular_inverse,
    modular_power,
)


class Mat102SmokeTests(unittest.TestCase):
    def test_extended_euclid_witness(self) -> None:
        result = extended_gcd(252, 198)

        self.assertEqual(result.gcd, 18)
        self.assertEqual(252 * result.x + 198 * result.y, 18)

    def test_inverse_and_power_boundaries(self) -> None:
        inverse = modular_inverse(17, 43)

        self.assertEqual(inverse, 38)
        self.assertEqual((17 * inverse) % 43, 1)
        self.assertEqual(modular_power(9, 0, 5), 1)

    def test_finite_law_reports_keep_their_scope(self) -> None:
        report = analyze_residue_laws(6)

        self.assertEqual(report.modulus, 6)
        self.assertTrue(report.distributive)
        self.assertFalse(report.every_nonzero_element_has_multiplicative_inverse)
        self.assertIsNotNone(report.zero_divisor_witness)


def load_tests(
    loader: unittest.TestLoader,
    standard_tests: unittest.TestSuite,
    pattern: str | None,
) -> unittest.TestSuite:
    del pattern
    standard_tests.addTests(loader.loadTestsFromName("example.tests.test_modular_math"))
    return standard_tests


if __name__ == "__main__":
    unittest.main(verbosity=2)
