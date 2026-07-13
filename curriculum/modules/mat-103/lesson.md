# Modular arithmetic and finite fields

Modular arithmetic replaces an integer by its congruence class. When the
modulus is prime, those classes form a field: addition, subtraction,
multiplication, and division by every nonzero value remain inside a finite set.
That distinction matters in cryptographic mathematics, where silently treating
arithmetic modulo a composite as a field can invalidate cancellation,
inversion, and proof steps.

This module computes with exact integers only. Its Python example is bounded
teaching code, not a constant-time or production cryptographic implementation.

## Learning objectives

- **MAT-103-01:** Compute and justify modular reduction, inverses,
  exponentiation, and finite-prime-field operations.
- **MAT-103-02:** Implement a bounded prime-field value type with explicit
  modulus and input invariants and tests.
- **MAT-103-03:** Use counterexamples to distinguish a prime field from
  arithmetic modulo a composite and separate tests from proof.

## Prerequisites

Pass <code>mat-102</code> and <code>prg-101</code>. You should be able to use
divisibility, greatest common divisors, Bézout identities, equivalence
relations, basic proof and counterexample techniques, and bounded Python
functions, branches, loops, errors, and tests. This lesson restates the number
theory facts on which its field claims depend.

Use Python 3.11 or newer and only the standard library. No network,
administrator access, external package, floating-point arithmetic, or
unbounded learner input is required.

## Lesson

### Congruence and canonical representatives

For a positive integer <code>n</code>, write
<code>a ≡ b (mod n)</code> exactly when <code>n</code> divides
<code>a - b</code>. This is an equivalence relation. The congruence class of
<code>a</code> contains every <code>a + kn</code> for integer
<code>k</code>.

The canonical representative is the unique integer <code>r</code> satisfying

~~~text
a = qn + r, where 0 <= r < n.
~~~

For a positive modulus, Python's integer expression <code>a % n</code> returns
that representative. For example,

~~~text
-20 = (-2)(17) + 14, so -20 mod 17 = 14.
~~~

Reduction is not rounding. It preserves a congruence class. If
<code>a ≡ a' (mod n)</code> and <code>b ≡ b' (mod n)</code>, then sums,
differences, and products remain congruent:

~~~text
(a + b) mod n
(a - b) mod n
(a * b) mod n
~~~

Modulo 17, using canonical representatives:

- <code>7 + 13 = 20 ≡ 3</code>;
- <code>7 - 13 = -6 ≡ 11</code>; and
- <code>7 * 13 = 91 ≡ 6</code>.

Reduce after each operation when tracing by hand. This keeps intermediate
values small without changing the congruence class.

### Inverses come from a gcd condition

A multiplicative inverse of <code>a</code> modulo <code>n</code> is a value
<code>x</code> satisfying <code>ax ≡ 1 (mod n)</code>. Such an inverse exists
exactly when <code>gcd(a, n) = 1</code>.

The reason is Bézout's identity. If the gcd is 1, there are integers
<code>x</code> and <code>y</code> with

~~~text
ax + ny = 1.
~~~

Reducing both sides modulo <code>n</code> leaves <code>ax ≡ 1</code>. Conversely,
if <code>ax ≡ 1</code>, then <code>ax - 1</code> is a multiple of
<code>n</code>, which gives a Bézout combination equal to 1 and forces the gcd
to be 1.

For 5 modulo 17, the Euclidean algorithm and back-substitution give:

~~~text
17 = 3(5) + 2
 5 = 2(2) + 1
 1 = 5 - 2(2)
   = 5 - 2(17 - 3(5))
   = 7(5) - 2(17).
~~~

Therefore 7 is the inverse of 5 modulo 17. Verification is a separate short
calculation: <code>5 * 7 = 35 ≡ 1 (mod 17)</code>.

Division by nonzero <code>b</code> in a field means multiplication by
<code>b</code>'s inverse. It is not integer division. Zero has no multiplicative
inverse because <code>0 * x</code> is always zero.

### Exponentiation by repeated squaring

Computing <code>a</code> multiplied by itself <code>e</code> times takes work
linear in <code>e</code>. Square-and-multiply uses the binary expansion of the
nonnegative exponent and takes work proportional to its bit length.

For <code>5^13 mod 17</code>, use <code>13 = 8 + 4 + 1</code>:

~~~text
5^1 mod 17 = 5
5^2 mod 17 = 8
5^4 mod 17 = 13
5^8 mod 17 = 16
5^13 mod 17 = (16)(13)(5) mod 17 = 3.
~~~

The running algorithm starts with result 1, repeatedly tests whether the
remaining exponent is odd, multiplies by the current factor when it is, squares
the factor, and halves the exponent with integer division. The example defines
<code>a^0</code> as the multiplicative identity, including the program's
explicit <code>0^0 = 1</code> convention. A different interface must document
any different convention.

Python's three-argument <code>pow(a, e, n)</code> performs modular
exponentiation without first constructing the enormous integer
<code>a**e</code>. The supplied example implements square-and-multiply directly
so its state can be inspected, then tests it against <code>pow</code>.

For prime <code>p</code> and nonzero <code>a mod p</code>, Fermat's little
theorem gives <code>a^(p-1) ≡ 1 (mod p)</code>, hence
<code>a^(p-2)</code> is an inverse. This theorem supports the formula only after
the prime and nonzero premises are established. The example uses the extended
Euclidean algorithm so a failed gcd is explicit.

### Why a prime modulus gives a field

The prime field <code>F_p</code> consists of the <code>p</code> congruence
classes represented by <code>0, 1, ..., p-1</code>, with addition and
multiplication reduced modulo prime <code>p</code>. It is closed under those
operations. The integer laws descend to the congruence classes, providing
associativity, commutativity, distributivity, and additive identities and
inverses.

The remaining field requirement is division by every nonzero value. If
<code>p</code> is prime and <code>1 <= a < p</code>, the only positive common
divisor of <code>a</code> and <code>p</code> is 1. Therefore Bézout gives an
inverse for every nonzero class.

This module concerns prime fields <code>F_p</code>. Finite fields of size
<code>p^k</code> for <code>k &gt; 1</code> require a different construction;
ordinary integer arithmetic modulo <code>p^k</code> is generally not that
field.

### A composite modulus supplies a counterexample

If <code>n</code> is composite, write <code>n = ab</code> with
<code>1 &lt; a,b &lt; n</code>. Both classes are nonzero, but
<code>ab ≡ 0 (mod n)</code>. They are **zero divisors**. A field cannot contain
nonzero zero divisors: if <code>a</code> had an inverse, multiplying
<code>ab = 0</code> by it would imply <code>b = 0</code>, a contradiction.

Modulo 8 gives concrete witnesses:

~~~text
2 is nonzero, 4 is nonzero, but 2 * 4 ≡ 0.
2 * 1 ≡ 2 * 5, but 1 is not congruent to 5.
gcd(2, 8) = 2, so 2 has no inverse.
~~~

The second line disproves unrestricted multiplicative cancellation. Some
classes modulo a composite can still be units: 3 is its own inverse modulo 8.
One successful inverse therefore does not prove that the whole structure is a
field.

A single valid counterexample disproves a universal claim such as “every
nonzero class modulo every positive integer has an inverse.” Testing many
values without finding a counterexample does not prove that claim.

### Encode the invariants in a value type

The [bounded prime-field example](examples/prime_field.py) uses a frozen data
class whose stored invariant is:

~~~text
modulus is a proven prime in 2..65,521
raw input is an exact int in -10^12..10^12
stored value is the canonical representative in 0..modulus-1
~~~

Python's <code>bool</code> is a subclass of <code>int</code>, so the example uses
<code>type(value) is int</code> when it promises an exact integer input. It
rejects a composite or oversized modulus before construction and rejects an
oversized raw value before reduction. Otherwise, reducing first would erase
evidence that the declared input bound had been violated.

<code>@dataclass(frozen=True, slots=True)</code> generates initialization,
comparison, and representation behavior and prevents ordinary mutation after
construction. <code>__post_init__</code> validates the inputs, then uses
<code>object.__setattr__</code> only to store the canonical value during
construction.

Operator methods check that both operands are instances of the type and have
the same modulus. Addition, subtraction, multiplication, negation, inversion,
division, and bounded nonnegative exponentiation return new validated values.
Mixing <code>F_17</code> and <code>F_19</code> is an error rather than an
implicit conversion.

The implementation also declares these work limits:

- modulus at most 65,521, with trial division through its square root;
- raw value magnitude at most <code>10^12</code>; and
- exponent from 0 through 1,000,000.

These are teaching-envelope bounds, not cryptographic parameter guidance.
Python integers and branches are not promised constant-time. Do not infer
side-channel resistance, safe key handling, protocol suitability, or Orange
runtime behavior from this host-language example.

### Tests and proofs answer different questions

The smoke check exhaustively enumerates arithmetic over <code>F_7</code>,
including every distributive triple. That is strong executable evidence about
the code paths and finite inputs tested. It is not a proof for every prime, and
it does not prove that the primality checker or Python runtime is defect-free.

The general field claim uses a proof: prime <code>p</code> makes every nonzero
class coprime to <code>p</code>, and Bézout supplies the inverse. The composite
claim uses a factorization witness. Tests should be traced to those
specifications, while proofs should state every premise. Neither should be
renamed as the other.

## Worked example

Run the supplied example and its independent smoke check from the module
directory:

~~~sh
cd curriculum/modules/mat-103
PYTHONDONTWRITEBYTECODE=1 python3 examples/field_worked.py
PYTHONDONTWRITEBYTECODE=1 python3 checks/lab_smoke.py
~~~

The worked program reduces <code>-20</code>, performs operations in
<code>F_17</code>, verifies the inverse of 5, computes <code>5^13</code>, and
prints the modulo-8 zero-divisor and inverse failure. The smoke check adds
normal, exact-boundary, invalid, mixed-modulus, zero-division, exhaustive
<code>F_7</code>, and subprocess checks. It must print
<code>mat-103 lab smoke: PASS</code> and exit 0.

The check supports only the bounded example contract. The number-theoretic
proof remains separate evidence for the general statement.

## Check your understanding

1. Give the canonical representative of <code>-20</code> modulo 17 and justify
   it with the division equation.
2. State the necessary and sufficient gcd condition for an inverse modulo
   <code>n</code>.
3. Why does primality of <code>p</code> give an inverse for every nonzero class
   in <code>F_p</code>?
4. Why do <code>2 * 4 ≡ 0 (mod 8)</code> and
   <code>2 * 1 ≡ 2 * 5 (mod 8)</code> refute field behavior?
5. What does exhaustive testing over <code>F_7</code> establish, and what does
   it not prove?
6. Why must the value type reject an oversized raw input before reducing it?

**Answers:** (1) 14 because <code>-20 = (-2)(17) + 14</code>; (2) an inverse
exists exactly when <code>gcd(a,n)=1</code>; (3) a nonzero representative below
prime <code>p</code> shares no positive divisor except 1 with <code>p</code>, so
Bézout gives an inverse; (4) they show nonzero zero divisors and failed
cancellation; (5) it checks the implementation on all enumerated values and
triples for that one field, not all primes, all implementations, or the general
theorem; (6) reduction could turn an out-of-envelope integer into a small
apparently valid stored value and conceal the contract violation.

## Next step

Complete the [lab](lab.md), including the hand derivations, changed bounded
value type, tests, prime-field proof, and composite counterexamples. Then take
the [independent assessment](assessment.md). Passing requires at least 80/100
and every critical criterion in the [rubric](rubric.md).

## Sources

- University of Dublin, [Finite Fields course notes, The Prime
  Fields](https://www.maths.tcd.ie/pub/Maths/Courseware/FiniteFields/GF.pdf),
  congruence classes, prime fields, inverses, and zero divisors.
- Alfred Menezes, Paul van Oorschot, and Scott Vanstone, [Handbook of Applied
  Cryptography, Chapter 2](https://cacr.uwaterloo.ca/hac/about/chap2.pdf),
  integer and finite-field arithmetic, Euclidean algorithms, and modular
  exponentiation.
- Python Software Foundation, [Python 3.11 expression
  reference](https://docs.python.org/3.11/reference/expressions.html) and
  [built-in functions](https://docs.python.org/3.11/library/functions.html),
  integer remainder and three-argument <code>pow</code> behavior.
- Python Software Foundation, [Python 3.11 <code>dataclasses</code>
  documentation](https://docs.python.org/3.11/library/dataclasses.html), frozen
  and slotted data classes.
- [Assessment system](../../../docs/assessment-system.md), executable evidence,
  critical criteria, and module pass policy.
