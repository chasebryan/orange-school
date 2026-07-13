# Rubric: exact prime-field value contract

## Rubric

The assessment is worth 100 points.

| Criterion | Points | Evidence required |
| --- | ---: | --- |
| Exact modular and prime-field reasoning | 30 | Correct reductions, field operations, Euclidean/Bézout inverse, quotient, square-and-multiply trace, and independent verification |
| Bounded value type and tests | 40 | Enforced type/modulus/value/exponent invariants, complete operations, explicit failures, work bounds, normal/boundary/invalid tests, failure-sensitive suite, and exhaustive <code>F_7</code> checks |
| Counterexamples and proof boundary | 20 | Valid modulo-21 witnesses, composite generalization, prime-field proof, evidence classification, and accurate limitations |
| Reproducibility and clarity | 10 | Python version, workspace, exact commands and result channels, statuses, readable source, and offline evidence record |
| **Total** | **100** |  |

## Critical criteria

All three critical criteria must pass:

1. **Arithmetic integrity:** earn at least 24/30. Every assessed result must be
   correct and supported by the requested reduction, Bézout, or exponentiation
   derivation. Calculator output without a mathematical justification, an
   invalid inverse, or division treated as integer division fails this
   criterion.
2. **Type-contract integrity:** earn at least 32/40. The implementation must
   reject composite and mixed moduli, enforce all bounds before canonicalizing,
   reject zero inversion, and pass normal, endpoint, outside-bound,
   failure-sensitivity, and exhaustive tests. Accepting a composite modulus or
   silently mixing fields fails this criterion.
3. **Proof-boundary integrity:** earn at least 16/20. Composite witnesses must
   use the claimed nonzero or unequal classes, and the general prime-field
   conclusion must follow from stated primality, gcd, and Bézout premises. A
   finite test run presented as proof for all primes fails this criterion.

A total of 80 or more cannot compensate for a failed critical criterion.

## Scoring

- **Exact reasoning (30):** 8 for reductions and four basic operations, 8 for
  Euclidean/Bézout inverse and quotient, 8 for the complete
  square-and-multiply trace, and 6 for exact independent verification and clear
  congruence notation.
- **Bounded type and tests (40):** 10 for constructor and stored invariants, 10
  for correct field operations and same-field enforcement, 7 for primality,
  inverse, and exponent algorithms with work bounds, 8 for endpoints and
  invalid inputs, and 5 for failure sensitivity and exhaustive
  <code>F_7</code> coverage.
- **Counterexamples and proof boundary (20):** 6 for valid zero-divisor,
  cancellation, nonunit, and unit witnesses; 5 for the composite
  generalization; 5 for the prime-field inverse proof; and 4 for accurate
  evidence labels and limitations.
- **Reproducibility and clarity (10):** 5 for environment, directory, commands,
  channels, and statuses; 3 for readable source, tests, and derivations; and 2
  for truthful offline and cryptographic-implementation limits.

Pass only with at least 80/100 and all critical criteria.

## Feedback and retry

Feedback names the first incorrect congruence, unenforced invariant, invalid
counterexample, or proof/test category error; maps it to an outcome ID; and
identifies the missing evidence. Preserve the original submission and append a
correction record.

A retry uses a new assessor-selected prime below the implementation bound, a
new composite with at least two distinct factors, and different endpoint
values. Rerun every affected calculation and test, including the deliberate
failure-sensitivity check. Revised prose cannot replace missing executable
evidence, and a passing test cannot replace a failed general proof.
