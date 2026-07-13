"""Bounded number-theory and modular-arithmetic helpers for MAT-102."""

from .modular import (
    BezoutResult,
    LawObservations,
    analyze_residue_laws,
    congruent,
    divides,
    extended_gcd,
    gcd,
    modular_inverse,
    modular_power,
)

__all__ = [
    "BezoutResult",
    "LawObservations",
    "analyze_residue_laws",
    "congruent",
    "divides",
    "extended_gcd",
    "gcd",
    "modular_inverse",
    "modular_power",
]
