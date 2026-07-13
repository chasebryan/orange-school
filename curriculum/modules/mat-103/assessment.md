# Assessment: exact prime-field value contract

## Instructions

Complete this assessment independently with Python 3.11 or newer and only the
standard library. Work in a fresh temporary directory. Submit hand
calculations, proofs and counterexamples, source, tests, and a reproducible
command/result record. Do not copy or rename the supplied example or lab
solution.

Use exact integers throughout. State every modulus, bound, premise, and
evidence limitation. This assessment covers:

- **MAT-103-01:** Compute and justify modular reduction, inverses,
  exponentiation, and finite-prime-field operations.
- **MAT-103-02:** Implement a bounded prime-field value type with explicit
  modulus and input invariants and tests.
- **MAT-103-03:** Use counterexamples to distinguish a prime field from
  arithmetic modulo a composite and separate tests from proof.

## Knowledge check

1. Define <code>a ≡ b (mod n)</code> and canonical representative. Explain why
   addition and multiplication do not depend on which representative is chosen.
2. Prove that <code>a</code> has an inverse modulo <code>n</code> exactly when
   <code>gcd(a,n)=1</code>.
3. Describe square-and-multiply and state its work in terms of the exponent's
   bit length.
4. Prove that every nonzero class modulo a prime has an inverse. Identify the
   step that would fail for a composite modulus.
5. Explain why a nonzero zero divisor rules out a field and why finding one
   invertible class does not establish a field.
6. Distinguish calculation, unit test, exhaustive finite test, counterexample,
   and general proof.

## Independent task

1. **Exact operations — MAT-103-01.** In <code>F_31</code>, derive the
   canonical representative of <code>-94</code>; the sum
   <code>27 + 19</code>; difference <code>8 - 21</code>; product
   <code>14 * 23</code>; inverse of 14; quotient <code>23 / 14</code>; and
   <code>14^19</code>. Show division equations for reductions, the full
   Euclidean and Bézout derivation for the inverse, and every selected square in
   square-and-multiply. Verify, but do not replace, the derivations with exact
   Python expressions.
2. **Bounded value type — MAT-103-02.** Create
   <code>assessed_field.py</code> with a frozen type
   <code>PrimeFieldElement</code> whose enforced contract is:

   - exact-integer prime modulus from 2 through 10,007;
   - exact-integer raw value from <code>-10^9</code> through
     <code>10^9</code>, stored in canonical range;
   - exact-integer nonnegative exponent at most 1,000,000;
   - same-modulus addition, subtraction, multiplication, negation, inversion,
     division, and exponentiation returning new validated values; and
   - explicit errors for wrong types including Boolean, bound violations,
     composite modulus, mixed modulus, and zero inversion.

   Use bounded trial division, the extended Euclidean algorithm, and
   square-and-multiply. Document constructor and stored invariants, failure
   behavior, maximum primality work, and maximum exponent loop iterations.
3. Create <code>test_assessed_field.py</code>. Test all task-1 results; raw
   value and exponent endpoints plus one value outside each; modulus 2 and
   10,007 plus an in-range composite; Boolean, float, and mixed-modulus errors;
   zero inverse; division reconstruction; and at least eight comparisons with
   three-argument <code>pow</code>. Exhaustively test closure, identities,
   additive inverses, nonzero inverses, and distributivity over
   <code>F_7</code>. Show that a deliberate wrong expected result makes the
   suite fail, preserve that observation, restore it, and preserve the passing
   run.
4. **Counterexample and proof boundary — MAT-103-03.** In arithmetic modulo
   21, provide nonzero zero divisors, a failed-cancellation equality using two
   unequal values, a nonzero class with no inverse and its gcd, and a nonzero
   class with an inverse and verification. Generalize the zero-divisor witness
   for every composite factorization. Separately prove the prime-field inverse
   property from gcd and Bézout.
5. Write <code>evidence-map.md</code>. Classify each hand derivation, automated
   test group, exhaustive <code>F_7</code> run, modulo-21 witness, composite
   generalization, and prime-field argument. State exactly what each item
   supports and at least one limitation. Explicitly state that passing Python
   tests do not prove the field theorem, constant-time execution, production
   cryptographic safety, or Orange behavior.
6. Record Python version, absolute workspace, exact commands, stdout, stderr,
   immediate statuses, source identities, and the declared input/work bounds.
   Run entirely offline.

## Completion criteria

Use the [rubric](rubric.md). Passing requires at least 80/100 and every critical
criterion. The submission must:

- correctly derive and justify every modular and <code>F_31</code> operation for
  **MAT-103-01**;
- enforce the complete bounded prime-field type contract and pass normal,
  exact-boundary, invalid, comparison, and exhaustive tests for
  **MAT-103-02**;
- supply valid composite counterexamples and premise-complete field arguments,
  while distinguishing executable tests from proof, for **MAT-103-03**; and
- preserve reproducible evidence without claiming constant-time or production
  cryptographic behavior.

An unexplained calculator result, composite-accepting type, missing critical
boundary, or test suite presented as a general proof cannot pass.
