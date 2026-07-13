# Number theory and algebra

Cryptographic specifications use integers, divisibility, congruences, inverses,
and algebraic structures precisely. This module develops those ideas without
turning a computed example into a theorem. Every algorithm has a declared input
bound, every algebraic claim names its set and operation, and every test result
keeps its scope.

## Learning objectives

- **MAT-102-01:** Compute and justify gcd, extended Euclid, divisibility, and
  congruence results.
- **MAT-102-02:** Analyze closure, identity, inverse, and operation laws in
  groups, rings, and fields without overclaiming.
- **MAT-102-03:** Implement and test bounded modular algorithms while separating
  computation from proof.

## Prerequisites

Pass `mat-101`. You should be able to state a quantified claim, use direct and
induction arguments, produce a counterexample, and distinguish a proof from a
finite test. No separate programming module is assumed. The Python example is
supported by the minimal bridge below, which teaches the exact package,
annotation, validation, loop, exception, tuple, optional-result, and `unittest`
constructs required by the lab and assessment. It uses only Python 3.11-or-newer
standard-library features.

You need integer arithmetic and the quotient/remainder operation. All commands
are local and bounded; no network, administrator access, or external package is
required.

## Lesson

### Minimal Python bridge

The lab asks you to translate a mathematical algorithm into a small Python
package, so this section supplies every Python construct that work requires.
You are not expected to infer a package design or testing convention from prior
coursework.

A file named `bounded_inverse/inverse.py` is a **module**. An empty
`bounded_inverse/__init__.py` marks the directory as a package that another file
can import. A function definition has a name, annotated inputs, an annotated
result, an indented body, and an explicit return:

```python
def bounded_remainder(value: int, modulus: int) -> int:
    if type(value) is not int or type(modulus) is not int:
        raise TypeError("value and modulus must be integers")
    if not 2 <= modulus <= 1_000_000:
        raise ValueError("modulus must be from 2 through 1,000,000")
    return value % modulus
```

The annotations describe the intended contract; the `if` statements enforce it
for unchecked runtime callers. `raise` stops the function with a precise failure.
This module rejects `bool` deliberately because Python treats `True` and `False`
as integer-like values in ordinary arithmetic. Invalid representations fail
before the algorithm starts.

The assessment uses these result annotations:

| Annotation | Meaning here |
| --- | --- |
| `int` | one integer |
| `tuple[int, int, int]` | exactly three integers, returned as `(g, x, y)` |
| `int | None` | either an integer inverse or the explicit absence `None` |

`None` means the inputs satisfy the contract but the requested inverse does not
exist. It is different from an invalid modulus, which raises `ValueError`.

Variables are names for current values. Parallel assignment evaluates the right
side first and then replaces all names together:

```python
old_remainder, remainder = remainder, old_remainder - quotient * remainder
```

This is useful for Euclid because the new remainder depends on both old values.
A `while` loop repeats while its condition is true:

```python
while remainder != 0:
    quotient = old_remainder // remainder
    old_remainder, remainder = (
        remainder,
        old_remainder - quotient * remainder,
    )
```

`//` is integer floor division, `%` is remainder, `==` tests equality, and
`!=` tests inequality. Every value assigned inside the loop must be related to
the prior values by the invariant used in the correctness argument.

The standard-library `unittest` module runs small methods whose names begin with
`test_`:

```python
import unittest

from bounded_inverse.inverse import bounded_remainder


class RemainderTests(unittest.TestCase):
    def test_normal_result(self) -> None:
        self.assertEqual(bounded_remainder(17, 5), 2)

    def test_invalid_modulus(self) -> None:
        with self.assertRaises(ValueError):
            bounded_remainder(17, 1)


if __name__ == "__main__":
    unittest.main()
```

From the directory containing `bounded_inverse` and `tests`, run all test files
with:

```sh
python3 -m unittest discover -s tests -v
```

The process exits 0 when the discovered suite passes and nonzero when a test
fails or errors. Normal cases show intended computation, boundary cases exercise
the edge of the contract, and invalid cases show rejection. The later lab gives
the exact package tree, function signatures, bounds, test categories, and
commands; the mathematical loop updates are the part you must derive.

### Divisibility and greatest common divisors

For integers `d` and `n`, say **d divides n**, written \(d\mid n\), when there
exists an integer `k` such that `n = dk`. Under this definition, 0 divides only
0. This module's executable `divides` function deliberately requires a nonzero
divisor so callers do not overlook that special mathematical case.

Basic consequences follow directly from the definition. If `d | a` and `d | b`,
then `a = dr` and `b = ds` for integers `r,s`, so

\[
d\mid (xa+yb)
\]

for every pair of integers `x,y`, because `xa+yb=d(xr+ys)`.

The **greatest common divisor** \(\gcd(a,b)\) is the unique nonnegative common
divisor `g` such that every common divisor of `a,b` also divides `g`. We use
these conventions:

- \(\gcd(a,b)=\gcd(|a|,|b|)\);
- \(\gcd(a,0)=|a|\); and
- \(\gcd(0,0)=0\).

The quotient-remainder theorem says that for integer `a` and positive `b`, there
are unique integers `q,r` with

\[
a=qb+r,\qquad 0\le r<b.
\]

Any common divisor of `a` and `b` also divides `r = a-qb`; conversely, a common
divisor of `b` and `r` divides `a`. Therefore

\[
\gcd(a,b)=\gcd(b,a\bmod b).
\]

Repeatedly applying this equality is **Euclid's algorithm**. For 252 and 198:

```text
252 = 1*198 + 54
198 = 3*54  + 36
54  = 1*36  + 18
36  = 2*18  + 0
```

The last nonzero remainder is 18, so `gcd(252,198)=18`. Each remainder is
smaller than the previous positive divisor, so the process terminates.

### Extended Euclid and Bézout coefficients

The extended algorithm tracks coefficients expressing each remainder as a
linear combination of the original inputs. Back-substitute:

```text
18 = 54 - 36
   = 54 - (198 - 3*54)
   = 4*54 - 198
   = 4*(252 - 198) - 198
   = 4*252 - 5*198
```

Thus the algorithm returns `g=18`, `x=4`, `y=-5` and the checkable witness

\[
252x+198y=18.
\]

Bézout's identity states that for integers `a,b`, some integers `x,y` satisfy
`ax+by=gcd(a,b)`. Multiplying the returned coefficients is a useful check of one
run. Proving the algorithm always returns valid coefficients additionally needs
a loop invariant and termination argument.

### Congruence and residue classes

For a positive modulus `m`, integers `a` and `b` are **congruent modulo m**,
written

\[
a\equiv b\pmod m,
\]

when `m | (a-b)`. Equivalently, they have the same canonical remainder from
`0` through `m-1`. For example, `17 ≡ 2 (mod 5)` and `-1 ≡ 4 (mod 5)`.
The mathematical definition permits `m=1`; this module's executable functions
require `m>=2` because their exercises use nontrivial residue systems.

Congruence is an equivalence relation:

- reflexive: `a ≡ a`;
- symmetric: if `a ≡ b`, then `b ≡ a`;
- transitive: if `a ≡ b` and `b ≡ c`, then `a ≡ c`.

It respects addition and multiplication. If `a ≡ b (mod m)` and
`c ≡ d (mod m)`, then

\[
a+c\equiv b+d\pmod m,
\qquad ac\equiv bd\pmod m.
\]

The residue system \(\mathbb Z/m\mathbb Z\) contains the classes represented by
`0,1,...,m-1`, with operations reduced modulo `m`.

### Modular inverses

An integer `x` is a multiplicative inverse of `a` modulo `m` when

\[
ax\equiv1\pmod m.
\]

Such an inverse exists exactly when `gcd(a,m)=1`. If extended Euclid gives
`ax+my=1`, reducing the equality modulo `m` leaves `ax ≡ 1`. For 17 and 43:

\[
1=-5(17)+2(43),
\]

so `-5`, whose canonical residue is 38, is the inverse of 17 modulo 43. Indeed,
`17*38 % 43 == 1`. For 6 modulo 9, the gcd is 3, so no inverse exists. The
example returns `None` rather than inventing one.

### Sets, operations, and laws

An algebraic property is meaningless until both the set and operation are named.
For a set `S` and binary operation `*`:

- **closure:** `a*b` belongs to `S` whenever `a,b` do;
- **associativity:** `(a*b)*c = a*(b*c)`;
- **identity:** some `e` satisfies `e*a = a*e = a` for every `a`;
- **inverse:** relative to identity `e`, an element `b` satisfies
  `a*b = b*a = e`; and
- **commutativity:** `a*b = b*a`.

A **group** has closure, associativity, an identity, and an inverse for every
element. It is **abelian** when the operation is also commutative.

In this course, a **ring** has two operations:

- addition forms an abelian group;
- multiplication is associative and has identity `1`; and
- multiplication distributes over addition on both sides.

Multiplication need not be commutative in every ring, though the residue rings in
this module are commutative. A **field** is a commutative ring with `0 != 1` in
which every nonzero element has a multiplicative inverse.

Do not infer missing laws:

- closure alone does not supply an identity or inverses;
- an identity for addition is not an identity for multiplication;
- a ring does not require every element to have a multiplicative inverse; and
- seeing inverses for several nonzero elements does not establish a field.

For addition modulo 6, all residues have inverses and 0 is the identity, so the
residues form an abelian group under addition. With addition and multiplication,
they form a commutative ring. They do not form a field: `2*3 ≡ 0 (mod 6)`, so 2
and 3 are nonzero zero divisors, and 2 has no multiplicative inverse. The units
`{1,5}` do form a group under multiplication modulo 6.

Modulo 5, every nonzero residue `{1,2,3,4}` has an inverse. Together with the
ring laws, this makes \(\mathbb Z/5\mathbb Z\) a field. A finite operation table
can exhaust the residues for this exact modulus. A theorem about every prime
modulus still needs a general argument.

### Bounded modular exponentiation

Computing `base**exponent` first can create an enormous integer. Repeated
square-and-multiply reduces after every multiplication:

```python
result = 1 % modulus
factor = base % modulus
remaining = exponent
while remaining > 0:
    if remaining % 2 == 1:
        result = (result * factor) % modulus
    factor = (factor * factor) % modulus
    remaining //= 2
```

The key loop invariant is

\[
result\cdot factor^{remaining}
\equiv base^{exponent}\pmod{modulus}.
\]

When `remaining = 2q+1` is odd, the **combined** loop transition sets
`result' = result*factor`, `factor' = factor^2`, and `remaining' = q`. Therefore
`result'*(factor')^remaining' = result*factor^(2q+1)`, preserving the invariant.
When `remaining = 2q` is even, `result` is unchanged while the squared factor and
halved remainder preserve the same product. Because the nonnegative integer
`remaining` strictly decreases when positive, the loop terminates. At
`remaining=0`, the invariant gives the desired result.

The provided function rejects negative exponents, moduli below 2, non-integers,
absolute inputs above `10^12`, and exponents above 1,000,000. These are an
educational resource contract, not number-theoretic limits.

### Keep computation and proof separate

For one result, check equations such as:

- `a*x + b*y == gcd(a,b)` for extended Euclid;
- `(a*inverse) % m == 1` for a modular inverse; and
- the custom modular power equals Python's three-argument `pow` on test cases.

These are valuable normal, boundary, invalid, and differential tests. They can
find a counterexample to a claimed implementation property. Passing them does
not prove the loop invariant, Python's correctness, or a theorem for untested
inputs.

Likewise, `analyze_residue_laws(6)` exhaustively computes selected laws for the
six represented residues. The report is finite computational evidence about the
encoded operations. A mathematical classification should cite the definitions
and arguments as well as the observation.

## Worked example

Run the local check from the repository root:

```sh
cd curriculum/modules/mat-102
python3 checks/lab_smoke.py
```

The smoke check verifies the Bézout witness for 252 and 198, the inverse of 17
modulo 43, the exponent-zero boundary, and a scoped law report for modulus 6. It
then runs the complete example suite.

Inspect `example/modular_math/modular.py`. For each function, locate:

1. its accepted input contract and bound;
2. the loop or finite enumeration;
3. the returned witness or observation; and
4. the test that checks a normal, boundary, or invalid case.

The test `test_law_observations_distinguish_mod_five_and_mod_six` does not merely
ask for one Boolean. It checks identities, additive inverses, units, and a
zero-divisor witness so the classification remains reviewable.

## Check your understanding

1. Why does replacing `(a,b)` with `(b, a mod b)` preserve the gcd?
2. What equation must extended Euclid's returned coefficients satisfy?
3. Is `29 ≡ 5 (mod 12)`? Justify from divisibility.
4. When does `a` have a multiplicative inverse modulo `m`?
5. Name the group axioms and the additional property of an abelian group.
6. Why is \(\mathbb Z/6\mathbb Z\) a ring but not a field?
7. What loop invariant supports square-and-multiply?
8. What does a passing comparison with Python's `pow` establish?

**Answers:** (1) common divisors of `a,b` are exactly common divisors of
`b,a-qb`; (2) `a*x+b*y=gcd(a,b)`; (3) yes, because 12 divides 24; (4) exactly
when `gcd(a,m)=1`; (5) closure, associativity, identity, inverses, plus
commutativity; (6) its residue operations satisfy the ring laws, but nonzero 2
and 3 multiply to zero and not every nonzero residue has an inverse; (7)
`result*factor^remaining ≡ base^exponent (mod modulus)`; (8) agreement for the
tested inputs under both implementations and execution assumptions, not a
general proof.

## Next step

Complete the [lab](lab.md), then the [independent assessment](assessment.md).
Passing requires at least 80/100 and every critical criterion in the
[rubric](rubric.md).

Later cryptography modules use these structures for finite-field arithmetic,
group operations, exponentiation, and precise algorithm assumptions.

## Sources

- Victor Shoup, [A Computational Introduction to Number Theory and
  Algebra](https://shoup.net/ntb/), divisibility, Euclid, congruences, groups,
  rings, fields, and algorithms.
- Eric Lehman, F. Thomson Leighton, and Albert R. Meyer, [Mathematics for
  Computer Science](https://courses.csail.mit.edu/6.042/spring18/mcs.pdf), number
  theory, modular arithmetic, and proof obligations.
- Python Software Foundation, [Built-in
  Functions](https://docs.python.org/3/library/functions.html#pow),
  three-argument modular `pow` used as a differential test oracle.
- Python Software Foundation, [unittest — Unit testing
  framework](https://docs.python.org/3/library/unittest.html), local test runner
  used by the module check.
- [Assessment system](../../../docs/assessment-system.md), module evidence and
  pass policy.
