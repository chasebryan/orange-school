"""Focused contract and regression tests for reliable_quote."""

from __future__ import annotations

import unittest

from example.reliable_quote import QuoteFailure, QuoteSuccess, calculate_quote


class QuoteTests(unittest.TestCase):
    def test_calculates_a_valid_quote(self) -> None:
        result = calculate_quote("3", "250")

        self.assertEqual(
            result,
            QuoteSuccess(quantity=3, unit_price_cents=250, total_cents=750),
        )

    def test_accepts_documented_boundaries(self) -> None:
        cases = (
            ("1", "0", 0),
            ("100", "1000000", 100_000_000),
        )

        for quantity, price, expected_total in cases:
            with self.subTest(quantity=quantity, price=price):
                result = calculate_quote(quantity, price)
                self.assertIsInstance(result, QuoteSuccess)
                self.assertEqual(result.total_cents, expected_total)

    def test_rejects_non_ascii_decimal_digits(self) -> None:
        result = calculate_quote("\u0661", "250")

        self.assertIsInstance(result, QuoteFailure)
        self.assertEqual(result.error.code, "not_ascii_decimal")
        self.assertEqual(result.error.field, "quantity")
        self.assertIn("\u0661", result.error.received)

    def test_rejects_whitespace_signs_and_empty_text(self) -> None:
        for quantity in ("", " 3", "3 ", "+3", "-3"):
            with self.subTest(quantity=quantity):
                result = calculate_quote(quantity, "250")
                self.assertIsInstance(result, QuoteFailure)
                self.assertEqual(result.error.code, "not_ascii_decimal")

    def test_rejects_values_outside_each_range(self) -> None:
        cases = (
            ("0", "250", "quantity"),
            ("101", "250", "quantity"),
            ("3", "1000001", "unit_price_cents"),
        )

        for quantity, price, expected_field in cases:
            with self.subTest(quantity=quantity, price=price):
                result = calculate_quote(quantity, price)
                self.assertIsInstance(result, QuoteFailure)
                self.assertEqual(result.error.code, "out_of_range")
                self.assertEqual(result.error.field, expected_field)

    def test_failure_preserves_context_and_withholds_a_total(self) -> None:
        result = calculate_quote("2", "twelve")

        self.assertIsInstance(result, QuoteFailure)
        self.assertEqual(result.error.field, "unit_price_cents")
        self.assertIn("twelve", result.error.received)
        self.assertFalse(hasattr(result, "total_cents"))

    def test_failure_context_is_bounded(self) -> None:
        result = calculate_quote("2", "x" * 500)

        self.assertIsInstance(result, QuoteFailure)
        self.assertLessEqual(len(result.error.received), 80)
        self.assertTrue(result.error.received.endswith("..."))

    def test_success_constructor_enforces_its_total_invariant(self) -> None:
        with self.assertRaisesRegex(ValueError, "total"):
            QuoteSuccess(quantity=2, unit_price_cents=50, total_cents=99)

    def test_runtime_type_mismatch_fails_closed(self) -> None:
        result = calculate_quote(3, "250")  # type: ignore[arg-type]

        self.assertIsInstance(result, QuoteFailure)
        self.assertEqual(result.error.code, "not_text")
        self.assertEqual(result.error.field, "quantity")
        self.assertIn("int:3", result.error.received)


if __name__ == "__main__":
    unittest.main()
