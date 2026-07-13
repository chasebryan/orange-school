#!/usr/bin/env python3
"""Smoke-check the executable PRG-103 example using only the standard library."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path
from typing import get_type_hints


MODULE_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(MODULE_ROOT))

from example.reliable_quote import (  # noqa: E402
    QuoteFailure,
    QuoteSuccess,
    calculate_quote,
)


class LabSmokeTests(unittest.TestCase):
    def test_public_function_has_input_and_output_annotations(self) -> None:
        annotations = get_type_hints(calculate_quote)

        self.assertIs(annotations["quantity_text"], str)
        self.assertIs(annotations["unit_price_cents_text"], str)
        self.assertIn("return", annotations)

    def test_success_obeys_the_documented_total_invariant(self) -> None:
        result = calculate_quote("4", "125")

        self.assertIsInstance(result, QuoteSuccess)
        self.assertEqual(result.total_cents, result.quantity * result.unit_price_cents)

    def test_invalid_input_fails_closed_with_context(self) -> None:
        result = calculate_quote("4", "12.5")

        self.assertIsInstance(result, QuoteFailure)
        self.assertEqual(result.error.code, "not_ascii_decimal")
        self.assertEqual(result.error.field, "unit_price_cents")
        self.assertIn("12.5", result.error.received)
        self.assertFalse(hasattr(result, "total_cents"))

    def test_unicode_digit_regression_is_rejected(self) -> None:
        result = calculate_quote("\u0661", "125")

        self.assertIsInstance(result, QuoteFailure)
        self.assertEqual(result.error.code, "not_ascii_decimal")


def load_tests(
    loader: unittest.TestLoader,
    standard_tests: unittest.TestSuite,
    pattern: str | None,
) -> unittest.TestSuite:
    """Combine smoke checks with the complete example regression suite."""

    del pattern
    standard_tests.addTests(loader.loadTestsFromName("example.tests.test_quote"))
    return standard_tests


if __name__ == "__main__":
    unittest.main(verbosity=2)
