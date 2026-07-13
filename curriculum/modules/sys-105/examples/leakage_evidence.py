#!/usr/bin/env python3
"""Bounded statistics for synthetic, public leakage-training samples."""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Iterable


MAX_SAMPLES_PER_CLASS = 4_096
MAX_TESTS = 64
MAX_ABS_SAMPLE = 1_000_000_000.0


@dataclass(frozen=True)
class WelchEvidence:
    left_count: int
    right_count: int
    left_mean: float
    right_mean: float
    mean_difference: float
    standard_error: float
    t_statistic: float


def _bounded_samples(values: Iterable[float], label: str) -> tuple[float, ...]:
    converted: list[float] = []
    for index, value in enumerate(values):
        if index == MAX_SAMPLES_PER_CLASS:
            raise ValueError(
                f"{label} must contain 2 through {MAX_SAMPLES_PER_CLASS} samples"
            )
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise TypeError(f"{label} samples must be finite numbers")
        converted_value = float(value)
        if not math.isfinite(converted_value):
            raise ValueError(f"{label} samples must be finite")
        if abs(converted_value) > MAX_ABS_SAMPLE:
            raise ValueError(
                f"{label} sample magnitude must not exceed {MAX_ABS_SAMPLE}"
            )
        converted.append(converted_value)
    if len(converted) < 2:
        raise ValueError(
            f"{label} must contain 2 through {MAX_SAMPLES_PER_CLASS} samples"
        )
    return tuple(converted)


def _mean_and_sample_variance(values: tuple[float, ...]) -> tuple[float, float]:
    mean = math.fsum(values) / len(values)
    variance = math.fsum((value - mean) ** 2 for value in values) / (len(values) - 1)
    return mean, variance


def welch_evidence(
    left: Iterable[float], right: Iterable[float]
) -> WelchEvidence:
    """Return descriptive effect and Welch t evidence without a proof claim."""

    left_values = _bounded_samples(left, "left")
    right_values = _bounded_samples(right, "right")
    left_mean, left_variance = _mean_and_sample_variance(left_values)
    right_mean, right_variance = _mean_and_sample_variance(right_values)
    standard_error = math.sqrt(
        left_variance / len(left_values) + right_variance / len(right_values)
    )
    if standard_error == 0.0:
        raise ValueError("Welch statistic is undefined when both class variances are zero")
    difference = left_mean - right_mean
    return WelchEvidence(
        left_count=len(left_values),
        right_count=len(right_values),
        left_mean=left_mean,
        right_mean=right_mean,
        mean_difference=difference,
        standard_error=standard_error,
        t_statistic=difference / standard_error,
    )


def bonferroni_per_test_alpha(family_alpha: float, test_count: int) -> float:
    """Return a bounded planning threshold; this does not validate test assumptions."""

    if isinstance(family_alpha, bool) or not isinstance(family_alpha, (int, float)):
        raise TypeError("family_alpha must be numeric")
    alpha = float(family_alpha)
    if not math.isfinite(alpha) or not 0.0 < alpha < 1.0:
        raise ValueError("family_alpha must be finite and strictly between zero and one")
    if type(test_count) is not int:
        raise TypeError("test_count must be an integer")
    if not 1 <= test_count <= MAX_TESTS:
        raise ValueError(f"test_count must be from 1 through {MAX_TESTS}")
    return alpha / test_count


def synthetic_fixture() -> dict[str, tuple[float, ...]]:
    """Return deterministic public samples with control, leak, and drift classes."""

    noise = tuple(float(value) for value in (-5, -3, -2, -1, 0, 1, 2, 3, 5) * 16)
    return {
        "control_left": tuple(1_000.0 + value for value in noise),
        "control_right": tuple(1_000.0 - value for value in noise),
        "deliberate_left": tuple(1_000.0 + value for value in noise),
        "deliberate_right": tuple(1_040.0 + value for value in noise),
        "drift_early": tuple(1_000.0 + value for value in noise),
        "drift_late": tuple(1_010.0 + value for value in noise),
    }
