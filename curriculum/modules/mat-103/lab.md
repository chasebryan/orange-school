# Lab: bounded arithmetic in a prime field

## Goal

Derive exact operations in a prime field, implement a changed bounded value
type, test its invariants and arithmetic, and use explicit composite-modulus
counterexamples while keeping executable tests separate from mathematical
proof.

## Setup

From the repository root, inspect and run the supplied examples:

~~~sh
cd curriculum/modules/mat-103
python3 --version
PYTHONDONTWRITEBYTECODE=1 python3 examples/field_worked.py
PYTHONDONTWRITEBYTECODE=1 python3 checks/lab_smoke.py
~~~

The final command must print <code>mat-103 lab smoke: PASS</code> and exit 0.
It uses only local files and Python's standard library.

Create a separate workspace for learner work:

~~~sh
workdir="$(mktemp -d)"
cd -- "$workdir"
pwd
~~~

Keep every new file under the printed path. Use exact integers, not floats. No
network, administrator access, external package, permission change, or deletion
command is required.

## Tasks

1. **Derive operations in <code>F_29</code>.** Before running Python, write a
   calculation record for:

   - the canonical reduction of <code>-73</code>;
   - <code>24 + 17</code>, <code>7 - 20</code>, and
     <code>12 * 19</code>;
   - the inverse of 12, including every Euclidean division and a Bézout
     back-substitution; and
   - <code>12^13</code> by square-and-multiply, showing the binary exponent and
     each reduced square and selected product.

   Verify the inverse with one multiplication. Verify the exponent result with
   <code>pow(12, 13, 29)</code>, but do not replace the derivation with that
   function call.
2. **Audit the supplied value type.** In
   [<code>prime_field.py</code>](examples/prime_field.py), identify the exact
   modulus, raw-value, canonical-value, same-field, zero-division, and exponent
   invariants. For each, name the constructor or operation that enforces it and
   one test in the smoke check that would fail if enforcement disappeared.
   Explain why the implementation rejects <code>bool</code>, a composite
   modulus, mixed moduli, and an oversized value.
3. **Implement a changed bounded type.** Create <code>lab_field.py</code> using
   only Python 3.11's standard library. Implement a frozen value type named
   <code>FieldElement</code> with this independent contract:

   - modulus is an exact integer, prime, and from 2 through 997;
   - raw value is an exact integer from <code>-10^6</code> through
     <code>10^6</code> and is stored canonically;
   - exponent is an exact integer from 0 through 10,000;
   - addition, subtraction, multiplication, negation, inversion, division, and
     exponentiation return new <code>FieldElement</code> values;
   - binary field operations reject another type or a different modulus; and
   - construction rejects a composite, inverse rejects zero, and all declared
     bounds fail explicitly.

   Implement primality by bounded trial division, inversion with the extended
   Euclidean algorithm, and exponentiation with square-and-multiply. State the
   maximum trial divisor and exponent-loop iterations implied by the bounds.
4. **Test the implementation.** Create <code>test_lab_field.py</code> with
   <code>unittest</code>. Cover every hand result from task 1, negative and
   oversized construction, moduli 2 and 997, composite 999 or another in-range
   composite, zero inverse, mismatched moduli, non-integer and Boolean inputs,
   exponents 0 and 10,000, and an exponent of 10,001. Exhaustively enumerate
   closure, identities, additive inverses, nonzero multiplicative inverses, and
   distributivity for <code>F_5</code>. Compare bounded modular powers with
   Python's three-argument <code>pow</code> on at least five cases.
5. **Build composite counterexamples.** For arithmetic modulo 15, show:

   - two nonzero zero divisors whose product is zero;
   - two unequal values that cannot be canceled from an equality after
     multiplication by 3;
   - the gcd reason 3 has no inverse; and
   - one nonzero class that does have an inverse.

   Generalize the zero-divisor argument from a factorization
   <code>n = ab</code>. Then prove that every nonzero class modulo prime
   <code>p</code> has an inverse. List the premises used in each proof.
6. **Separate evidence types.** Create <code>evidence-map.md</code> with rows
   for the <code>F_29</code> calculation, unit tests, exhaustive
   <code>F_5</code> enumeration, modulo-15 witnesses, general composite
   argument, and prime-field inverse proof. Label each as calculation, test,
   counterexample, or proof; state exactly what it establishes and at least one
   limitation.

## Verification

From the temporary workspace, run:

~~~sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v
test_status=$?
printf 'test status: %s\n' "$test_status"
~~~

Status 0 is necessary but not sufficient. Inspect the submitted derivations,
source, tests, and evidence map. Confirm that:

- every <code>F_29</code> result has a visible modular justification;
- the class validates before canonicalizing and never mixes moduli;
- normal, boundary, invalid, and exhaustive <code>F_5</code> cases run;
- composite witnesses use nonzero, unequal values where claimed;
- the prime-field proof depends explicitly on primality, gcd, and Bézout; and
- no test result is described as a proof for every prime or implementation.

Rerun the unchanged module smoke check from the module directory to distinguish
repository example evidence from temporary learner evidence.

## Reflection

Write four to six sentences:

- Which invariant would be lost if raw values were reduced before the bound
  check?
- Where does the prime premise enter the inverse proof?
- Why can one invertible value modulo 15 coexist with a failure to be a field?
- What did exhaustive <code>F_5</code> testing reveal, and what general claim
  still required proof?
