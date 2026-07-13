# Lab: Euclid, residue laws, and bounded modular power

## Goal

Compute and justify Euclidean and congruence results, classify a small residue
system by checking each required law, implement bounded square-and-multiply, and
report its tests separately from its correctness argument.

## Setup

From the repository root, verify the provided implementation:

```sh
cd curriculum/modules/mat-102
python3 checks/lab_smoke.py
smoke_status=$?
printf 'MAT-102 smoke status: %s\n' "$smoke_status"
```

Stop if the status is nonzero. Otherwise create a temporary workspace:

```sh
module_dir="$PWD"
workdir="$(mktemp -d)"
printf 'MAT-102 workspace: %s\n' "$workdir"
cp -R "$module_dir/example" "$workdir/example"
cd "$workdir"
mkdir -p bounded_power tests evidence
touch bounded_power/__init__.py tests/__init__.py number-theory.md algebra.md
```

All writes stay under the printed path. Use Python 3.11 or newer and only the
standard library. No network or administrator access is needed.

## Tasks

1. **Euclid and Bézout — MAT-102-01.** In `number-theory.md`, run Euclid's
   algorithm by hand for 252 and 198. Record every quotient and remainder, prove
   why each replacement preserves common divisors, and identify the gcd.

   Back-substitute to find integers `x,y` satisfying
   `252*x + 198*y = gcd(252,198)`. Verify the equality by direct substitution,
   then compare your result with `extended_gcd(252,198)`. Different valid
   coefficient pairs are possible; the equation, not matching one pair of
   spellings, is the requirement.

2. **Divisibility, congruence, and inverses — MAT-102-01.** Decide and justify
   each result from definitions:

   - whether 18 divides 252 and whether 35 divides 252;
   - whether 391 is congruent to 23 modulo 46;
   - the canonical residues of -17 modulo 5 and -17 modulo 12;
   - whether 17 has an inverse modulo 43, including Bézout coefficients and the
     canonical inverse; and
   - why 6 has no inverse modulo 9.

   Check the arithmetic with the supplied functions only after writing the
   derivation. Record whether computation confirmed or contradicted it.

   Use this exact local check so no prior Python command knowledge is assumed:

   ```sh
   python3 - <<'PY'
   from example.modular_math import congruent, divides, extended_gcd, modular_inverse

   print("extended gcd:", extended_gcd(252, 198))
   print("18 divides 252:", divides(18, 252))
   print("35 divides 252:", divides(35, 252))
   print("391 congruent to 23 modulo 46:", congruent(391, 23, 46))
   print("-17 residues:", -17 % 5, -17 % 12)
   print("inverse of 17 modulo 43:", modular_inverse(17, 43))
   print("inverse of 6 modulo 9:", modular_inverse(6, 9))
   PY
   ```

3. **Analyze operations modulo 8 — MAT-102-02.** In `algebra.md`, name the set
   and operation before every claim. For addition modulo 8, establish closure,
   associativity, identity, inverses, and commutativity. For addition and
   multiplication together, address multiplication closure, associativity,
   identity, commutativity, and both distributive laws.

   List every unit modulo 8 and one inverse for each. Give a nonzero
   zero-divisor witness. Classify:

   - all residues under addition;
   - all residues with addition and multiplication; and
   - the units under multiplication.

   State whether the full residue system is a field and identify the exact failed
   field requirement. Run `analyze_residue_laws(8)` and treat its result as
   finite computational evidence about modulus 8, not as a proof for arbitrary
   moduli.

   ```sh
   python3 - <<'PY'
   from example.modular_math import analyze_residue_laws

   print(analyze_residue_laws(8))
   PY
   ```

4. **Implement bounded modular power — MAT-102-03.** In
   `bounded_power/power.py`, implement:

   ```python
   def power_mod(base: int, exponent: int, modulus: int) -> int:
       ...
   ```

   Use repeated square-and-multiply, not `base**exponent` and not `pow` inside
   the implementation. Enforce these runtime bounds:

   - all inputs have exact type `int`, so Boolean values are rejected;
   - `abs(base) <= 10^9`;
   - `0 <= exponent <= 10_000`; and
   - `2 <= modulus <= 1_000_000`.

   Reject contract violations with a precise `TypeError` or `ValueError` before
   the loop. Reduce after every multiplication. Keep the original inputs
   available for testing and reasoning.

5. **Test the implementation — MAT-102-03.** Create
   `tests/test_bounded_power.py` with standard-library `unittest` cases for:

   - ordinary positive and negative bases;
   - exponent 0, exponent 1, base 0, and each maximum valid bound;
   - every just-outside invalid bound and Boolean/non-integer inputs;
   - comparison with three-argument `pow` over a declared finite table; and
   - the result range `0 <= result < modulus` for every successful case.

   Preserve source, Python version, commands, stdout, stderr, and status in
   `evidence/test-record.md`. A passing comparison supports the tested table only.

6. **Separate the proof obligation — MAT-102-03.** In
   `evidence/correctness-argument.md`, state:

   - preconditions and postcondition;
   - the initialization of `result`, `factor`, and `remaining`;
   - the loop invariant
     `result * factor^remaining ≡ base^exponent (mod modulus)`;
   - preservation for odd and even `remaining`;
   - a decreasing nonnegative termination measure;
   - why the invariant at loop exit gives the postcondition; and
   - assumptions about integer and remainder semantics.

   End with two lists: what the argument establishes if its steps and semantic
   assumptions are sound, and what the finite tests establish. Give at least
   three limits of each.

## Verification

Run the supplied example tests and your independent tests:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s example/tests -v
example_status=$?
printf 'example status: %s\n' "$example_status"

PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v
lab_status=$?
printf 'lab status: %s\n' "$lab_status"

test "$example_status" -eq 0
test "$lab_status" -eq 0
```

Then verify the artifacts:

- Euclid's remainder chain terminates at 18 and the Bézout equality is exact.
- Every divisibility and congruence result cites its definition.
- The modulo-8 analysis checks each group/ring/field law independently.
- A zero-divisor witness and complete unit list support the non-field decision.
- `power_mod` contains no call to `pow` and no full `base**exponent` expression.
- Tests include normal, boundary, invalid, and differential cases.
- The correctness argument and test record make different claims and list their
  assumptions and limits.

## Reflection

Answer in `evidence/correctness-argument.md`:

1. What information does extended Euclid add to an ordinary gcd computation?
2. Why does a zero divisor prevent a nonzero element from having a field inverse?
3. Which laws would remain unchecked if you inspected only an operation table's
   closure?
4. Which line of square-and-multiply corresponds to the odd-exponent part of the
   invariant?
5. If every differential test agrees with `pow`, which correctness questions
   remain open?
