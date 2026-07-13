#!/usr/bin/env python3
"""Smoke-check MAT-101 examples with Python's standard library."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path


MODULE_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(MODULE_ROOT))

from example.logic_scope import check_integer_claim, implies, triangular_sum  # noqa: E402


class Mat101SmokeTests(unittest.TestCase):
    def test_only_true_to_false_makes_implication_false(self) -> None:
        false_cases = [
            (antecedent, consequent)
            for antecedent in (False, True)
            for consequent in (False, True)
            if not implies(antecedent, consequent)
        ]

        self.assertEqual(false_cases, [(True, False)])

    def test_counterexample_refutes_a_universal_claim(self) -> None:
        result = check_integer_claim(
            0,
            8,
            lambda n: implies(n % 2 == 0, n % 4 == 0),
        )

        self.assertFalse(result.holds_on_checked_cases)
        self.assertEqual(result.counterexample, 2)

    def test_finite_success_records_but_does_not_expand_its_scope(self) -> None:
        result = check_integer_claim(0, 8, lambda n: triangular_sum(n) == n * (n + 1) // 2)

        self.assertTrue(result.holds_on_checked_cases)
        self.assertEqual((result.start, result.requested_stop), (0, 8))
        self.assertEqual(result.checked_count, 9)


def load_tests(
    loader: unittest.TestLoader,
    standard_tests: unittest.TestSuite,
    pattern: str | None,
) -> unittest.TestSuite:
    del pattern
    standard_tests.addTests(loader.loadTestsFromName("example.tests.test_logic_scope"))
    return standard_tests


if __name__ == "__main__":
    unittest.main(verbosity=2)
