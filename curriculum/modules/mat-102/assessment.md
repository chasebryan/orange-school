# Assessment: justified modular arithmetic and algebra

## Instructions

Complete the work independently in a fresh temporary directory. You may consult
the lesson and Python standard-library documentation, but not a completed lab
implementation. Show hand derivations before using code to check them.

Use Python 3.11 or newer and standard-library modules only. Do not use network or
administrator access. Submit `number-theory.md`, `structures.md`, your complete
`bounded_inverse` package and tests, `correctness.md`, and an exact test transcript
with source identity, command, stdout, stderr, and exit status.

Create the assessed tree with these supplied commands; filesystem command recall
is not part of the mathematics assessment:

```sh
workdir="$(mktemp -d)"
printf 'MAT-102 assessment workspace: %s\n' "$workdir"
cd "$workdir"
mkdir -p bounded_inverse tests evidence
touch bounded_inverse/__init__.py tests/__init__.py
```

Place the implementation in `bounded_inverse/inverse.py` and the tests in
`tests/test_inverse.py`. The lesson's minimal Python bridge defines every syntax
construct and test command needed for these files.

This assessment covers:

- **MAT-102-01:** Compute and justify gcd, extended Euclid, divisibility, and
  congruence results.
- **MAT-102-02:** Analyze closure, identity, inverse, and operation laws in
  groups, rings, and fields without overclaiming.
- **MAT-102-03:** Implement and test bounded modular algorithms while separating
  computation from proof.

## Knowledge check

1. State the quotient-remainder condition and explain why
   `gcd(a,b)=gcd(b,a mod b)` when `b>0`.
2. What equation must Bézout coefficients satisfy? Explain how that equation
   decides whether an inverse modulo `m` exists.
3. Define congruence modulo `m` from divisibility and prove one of reflexivity,
   symmetry, or transitivity directly from the definition.
4. List the axioms of a group, this course's ring convention, and a field. Give
   one example showing why closure alone establishes none of the full
   classifications.
5. Explain the difference between an algorithm result, tests of that algorithm,
   a loop-invariant correctness argument, and a theorem about an algebraic
   structure.

## Independent task

1. **Euclid, divisibility, and congruence — MAT-102-01.** In
   `number-theory.md`, compute `gcd(391,299)` with every quotient and remainder.
   Back-substitute to find `x,y` with

   ```text
   391*x + 299*y = gcd(391,299).
   ```

   Verify the equation. Then decide from definitions, with a witness or
   remainder as appropriate:

   - whether 23 divides 391 and 299;
   - whether 46 divides 391;
   - whether `391 ≡ 299 (mod 46)`;
   - the canonical residue of -391 modulo 46;
   - the inverse of 19 modulo 47; and
   - whether 12 has an inverse modulo 18.

   Each result must include its domain and convention. A calculator result
   without the divisibility or Bézout justification receives no justification
   credit.

2. **Structure analysis modulo 10 — MAT-102-02.** In `structures.md`, analyze
   the residues `{0,1,...,9}` under addition and multiplication modulo 10.
   Address separately:

   - closure of both operations;
   - associativity and commutativity of both operations;
   - additive and multiplicative identities;
   - additive inverses for every residue;
   - both distributive laws;
   - all multiplicative units and an inverse witness for each; and
   - a nonzero zero-divisor witness.

   Classify the residues under addition, the two-operation residue system, and
   the units under multiplication. Decide whether the full system is a field and
   name the exact failed axiom. You may run `analyze_residue_laws(10)` only after
   writing the analysis. Report it as exhaustive observation for the encoded
   finite modulus, not as a theorem for every `n`.

3. **Implement bounded extended Euclid and inverses — MAT-102-03.** Create a
   package `bounded_inverse` exposing:

   ```python
   def extended_gcd(a: int, b: int) -> tuple[int, int, int]:
       ...

   def inverse_mod(value: int, modulus: int) -> int | None:
       ...
   ```

   The tuple is `(gcd, x, y)` with nonnegative gcd and
   `a*x+b*y == gcd`. Support signed `a,b` and `(0,0)`. Require exact integer
   inputs with absolute value at most `10^9`. For `inverse_mod`, additionally
   require `2 <= modulus <= 1_000_000`; return the canonical inverse from 0
   through `modulus-1`, or `None` exactly when the gcd is not 1.

   Implement the iterative Euclidean updates yourself. Do not import `math.gcd`
   or copy the course example. Reject Boolean, non-integer, and out-of-bound
   values before iteration with precise exceptions.

4. **Test normal, boundary, and invalid behavior — MAT-102-03.** Use
   standard-library `unittest` to cover:

   - at least four ordinary gcd/coefficient pairs, including signed inputs;
   - `(0,0)`, `(a,0)`, and `(0,b)` boundaries;
   - the exact maximum valid input and just-outside values;
   - inverse cases for negative and positive representatives;
   - moduli 2 and 1, the maximum valid modulus, and just above it;
   - at least three non-coprime inputs that return `None`;
   - Boolean and other non-integer rejection; and
   - for every successful result, the Bézout equation or modular inverse
     equation as a test oracle.

   A table-driven differential test may compare returned gcd values with
   `math.gcd`, but the implementation itself may not call it.

5. **Separate computation from proof — MAT-102-03.** In `correctness.md`, state
   the exact algorithm preconditions and postconditions. Give an argument using
   both linear-combination invariants

   ```text
   old_r = a*old_x + b*old_y
   r     = a*x     + b*y
   ```

   together with gcd preservation and a decreasing nonnegative remainder. Show
   why loop exit yields Bézout coefficients and why `gcd(value,modulus)=1` is
   exactly the inverse condition.

   Separately list what the test run observed, its finite input table and bounds,
   and all runtime/tool assumptions. Give at least four limits of the proof
   argument and four limits of the tests. Do not claim that differential
   agreement proves both implementations correct.

## Completion criteria

Use the [rubric](rubric.md). Passing requires at least 80/100 and every critical
criterion. A complete submission includes:

- correct Euclidean steps, Bézout witness, divisibility, congruence, and inverse
  justifications for **MAT-102-01**;
- law-by-law classifications with exact sets and operations, complete units and
  a zero-divisor witness, and no generalization beyond the evidence for
  **MAT-102-02**;
- bounded Python 3.11 algorithms with normal, boundary, invalid, invariant, and
  differential tests for **MAT-102-03**; and
- separate correctness and test claims with reproducible commands, assumptions,
  scope, and limits.

A correct numeric answer without a derivation is incomplete. A green test suite
without the invariant argument is computation evidence, not proof credit.
