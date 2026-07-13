# Rubric: justified modular arithmetic and algebra

## Rubric

The assessment is worth 100 points.

| Criterion | Points | Evidence required |
| --- | ---: | --- |
| Euclid, Bézout, divisibility, and congruence | 30 | Correct remainder chain, coefficients and witness equation, divisibility witnesses, residues, congruence, and inverse decisions |
| Group, ring, and field analysis | 25 | Named sets/operations, law-by-law analysis, identities, inverses, units, zero divisor, classifications, and scoped computational comparison |
| Bounded algorithms and tests | 30 | Independent iterative implementation, exact bounds, normal/boundary/invalid tests, invariant oracles, and reproducible green suite |
| Computation-versus-proof discipline | 15 | Correctness argument, termination, separate test claims, assumptions, scope, and limits without overclaiming |
| **Total** | **100** |  |

## Critical criteria

All three critical criteria must pass:

1. **Number-theory justification — MAT-102-01:** earn at least 24/30. The gcd
   must follow a valid Euclidean remainder chain, returned coefficients must
   satisfy the exact Bézout equation, and every divisibility, congruence, and
   inverse decision must cite a witness, remainder, or gcd condition. Unexplained
   calculator output fails this criterion.
2. **Algebraic law control — MAT-102-02:** earn at least 20/25. Every
   classification must name its set and operation and address all required laws.
   The unit list and zero-divisor witness must be correct. Calling the full
   residue ring a field, or generalizing a modulus-10 computation to all moduli,
   fails this criterion.
3. **Bounded implementation with honest evidence — MAT-102-03:** earn at least
   24/30 on algorithms/tests and 12/15 on proof discipline. Inputs and resource
   bounds must fail closed; every successful coefficient/inverse result must have
   its equation tested; normal, boundary, and invalid cases must pass; and the
   invariant/termination argument must remain distinct from finite execution.
   Calling differential tests a proof fails this criterion.

Use of unrecorded external computation, network services, copied implementation,
or a forbidden library gcd inside the submitted algorithm fails the applicable
critical criterion regardless of total points.

## Scoring

- **Euclid, Bézout, divisibility, and congruence (30):** 8 for the complete
  Euclidean chain and gcd; 7 for back-substitution and the exact witness equation;
  6 for divisibility decisions; 5 for congruence and canonical residue; and 4
  for both inverse decisions with gcd justification.
- **Group, ring, and field analysis (25):** 5 for closure and associativity, 5
  for identities and additive inverses, 5 for commutativity and distributivity,
  5 for units/inverse witnesses and zero divisor, and 5 for correct scoped
  classifications and computational comparison.
- **Bounded algorithms and tests (30):** 10 for correct iterative coefficient
  updates and signed/zero behavior, 6 for canonical inverse-or-`None` behavior,
  5 for exact validation and bounds, 6 for complete normal/boundary/invalid
  tests, and 3 for reproducible execution evidence.
- **Computation-versus-proof discipline (15):** 6 for linear-combination and gcd
  invariants, 3 for termination and postcondition, 3 for separate proof/test
  assumption inventories, and 3 for at least four accurate limits of each.

Pass the module only with at least 80/100 and all critical criteria.

## Feedback and retry

Feedback identifies the first incorrect equation, failed algebraic law, code
boundary, or overclaimed evidence statement and maps it to the affected outcome.
Preserve the initial derivation and test output; annotate corrections so the
reasoning change remains reviewable.

For a retry, the assessor supplies different Euclidean inputs, modulus, and
algorithm bounds. The learner recomputes affected witnesses, repeats every
law-dependent classification, adds a focused regression test for each code
defect, and reruns the complete suite. All critical criteria and the 80/100
threshold apply to the new evidence.
