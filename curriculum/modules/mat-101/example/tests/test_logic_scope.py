"""Normal, boundary, invalid, and scope tests for logic_scope."""

from __future__ import annotations

import unittest

from example.logic_scope import check_integer_claim, implies, triangular_sum


class LogicScopeTests(unittest.TestCase):
    def test_implication_truth_cases(self) -> None:
        cases = (
            (False, False, True),
            (False, True, True),
            (True, False, False),
            (True, True, True),
        )

        for antecedent, consequent, expected in cases:
            with self.subTest(antecedent=antecedent, consequent=consequent):
                self.assertIs(implies(antecedent, consequent), expected)

    def test_implication_rejects_non_boolean_values(self) -> None:
        with self.assertRaises(TypeError):
            implies(1, True)  # type: ignore[arg-type]

    def test_finite_check_records_a_passing_scope(self) -> None:
        result = check_integer_claim(
            -20,
            20,
            lambda n: implies(n % 4 == 0, n % 2 == 0),
        )

        self.assertTrue(result.holds_on_checked_cases)
        self.assertEqual(result.checked_count, 41)
        self.assertEqual(result.last_checked, 20)
        self.assertIsNone(result.counterexample)

    def test_finite_check_returns_the_first_counterexample(self) -> None:
        result = check_integer_claim(
            0,
            10,
            lambda n: implies(n % 2 == 0, n % 4 == 0),
        )

        self.assertFalse(result.holds_on_checked_cases)
        self.assertEqual(result.counterexample, 2)
        self.assertEqual(result.last_checked, 2)
        self.assertEqual(result.checked_count, 3)

    def test_finite_check_accepts_a_single_case_boundary(self) -> None:
        result = check_integer_claim(0, 0, lambda n: n == 0)

        self.assertTrue(result.holds_on_checked_cases)
        self.assertEqual(result.checked_count, 1)

    def test_finite_check_rejects_invalid_ranges_and_predicates(self) -> None:
        with self.assertRaises(ValueError):
            check_integer_claim(2, 1, lambda n: n == n)
        with self.assertRaises(ValueError):
            check_integer_claim(0, 10_000, lambda n: n == n)
        with self.assertRaises(TypeError):
            check_integer_claim(0, 1, lambda n: n)  # type: ignore[arg-type,return-value]

    def test_triangular_sum_normal_and_boundary_cases(self) -> None:
        self.assertEqual(triangular_sum(0), 0)
        self.assertEqual(triangular_sum(1), 1)
        self.assertEqual(triangular_sum(5), 15)

    def test_triangular_sum_rejects_invalid_inputs(self) -> None:
        with self.assertRaises(TypeError):
            triangular_sum(True)
        with self.assertRaises(ValueError):
            triangular_sum(-1)
        with self.assertRaises(ValueError):
            triangular_sum(10_001)


if __name__ == "__main__":
    unittest.main()
