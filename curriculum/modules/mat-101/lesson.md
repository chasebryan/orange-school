# Logic and proof techniques

Programming turns statements into behavior. Before a statement can guide code or
support an assurance claim, its domain, assumptions, quantifiers, and conclusion
must be precise. This module builds that precision from the beginning and shows
why running examples is valuable evidence but not automatically a proof.

## Learning objectives

- **MAT-101-01:** Translate precise statements among prose, predicates,
  quantifiers, truth cases, and counterexamples.
- **MAT-101-02:** Construct direct, contrapositive, contradiction, and induction
  arguments.
- **MAT-101-03:** Distinguish proof from finite testing and enumerate assumptions
  and scope.

## Prerequisites

Pass `ori-001`. No previous proof course or programming module is assumed.
You need integer arithmetic, careful reading, paper or a text editor, and a
course-provided Python 3.11-or-newer interpreter for the executable illustration.
Every Python command is supplied and explained; writing Python from memory is
not assessed in this module.

All examples are local, deterministic, and bounded. They require no network,
administrator access, external package, or destructive command.

## Lesson

### Statements, domains, and predicates

A **proposition** is a statement that is either true or false once its terms and
domain are fixed. “7 is odd” is a proposition. “Choose a number” is a command,
not a proposition. “This program is fast” is too vague until “fast,” the input
set, the machine, and the measurement rule are defined.

A **predicate** is a statement with one or more variables. For integers, define

\[
E(n) :\iff \text{there exists an integer } k \text{ such that } n=2k.
\]

`E(n)` means “`n` is even.” It becomes a proposition after a value is supplied
or a quantifier binds `n`. The **domain** matters: `n/2` is an integer for every
even integer, but not for every integer.

Useful connectives are:

| Notation | Reading | True when |
| --- | --- | --- |
| `not P`, \(\neg P\) | not P | P is false |
| `P and Q`, \(P\land Q\) | P and Q | both are true |
| `P or Q`, \(P\lor Q\) | P or Q, inclusively | at least one is true |
| `P -> Q`, \(P\Rightarrow Q\) | if P, then Q | every case except true P with false Q |
| `P iff Q`, \(P\Leftrightarrow Q\) | P if and only if Q | P and Q have the same truth value |

The truth cases for implication are worth learning explicitly:

| P | Q | \(P\Rightarrow Q\) |
| --- | --- | --- |
| false | false | true |
| false | true | true |
| true | false | false |
| true | true | true |

An implication promises that no case has a true antecedent `P` and false
consequent `Q`. When `P` is false, that promise has not been broken. This is
called **vacuous truth**; it does not establish that `Q` is independently true.

The **converse** of `P -> Q` is `Q -> P`. A statement and its converse need not
agree. “If an integer is a multiple of 4, then it is even” is true. Its converse,
“if an integer is even, then it is a multiple of 4,” is false; 2 is a
counterexample.

The **contrapositive** of `P -> Q` is `not Q -> not P`. It is logically
equivalent to the original implication. The **inverse**, `not P -> not Q`, is not
equivalent in general.

### Quantifiers and their negations

The universal quantifier `for every`, \(\forall\), makes a claim about all
members of a domain:

\[
\forall n\in\mathbb Z,\quad 4\mid n \Rightarrow 2\mid n.
\]

Here \(a\mid b\) means “`a` divides `b`”: there is an integer `k` with
`b = a*k`.

A positive integer `p` is **prime** when `p > 1` and its only positive divisors
are 1 and `p`. This definition makes 2 prime and makes 1 non-prime.

The existential quantifier `there exists`, \(\exists\), asks for at least one
witness:

\[
\exists n\in\mathbb Z,\quad n^2=49.
\]

The values 7 and -7 are witnesses. Quantifier order changes meaning:

- \(\forall x\,\exists y,\ y>x\): for each integer `x`, some larger integer may
  be chosen. This is true.
- \(\exists y\,\forall x,\ y>x\): one integer is larger than every integer.
  This is false.

Negation swaps the quantifier and negates the predicate:

\[
\neg(\forall x\,P(x)) \Leftrightarrow \exists x\,\neg P(x),
\]

\[
\neg(\exists x\,P(x)) \Leftrightarrow \forall x\,\neg P(x).
\]

Therefore one counterexample refutes a universal claim. Many passing examples do
not prove one unless the checked set is the complete stated finite domain and
the checker itself is included among the assumptions.

### Anatomy of an argument

A reviewable argument identifies:

1. the exact proposition;
2. the domain and definitions;
3. assumptions and previously established results;
4. a sequence of justified steps; and
5. the conclusion and its scope.

Examples and diagrams may suggest an argument. They do not replace the justified
steps. Likewise, naming a proof technique does not perform the proof.

### Direct proof

Start from the assumptions and derive the conclusion. To prove “the product of
two odd integers is odd,” let `a = 2r + 1` and `b = 2s + 1` for integers `r` and
`s`. Then

\[
ab=(2r+1)(2s+1)=2(2rs+r+s)+1.
\]

The value in parentheses is an integer, so `ab` has the required odd form.

### Proof by contrapositive

To prove `P -> Q`, prove the equivalent `not Q -> not P`. Consider:

> For every integer `n`, if \(n^2\) is even, then `n` is even.

Its contrapositive says: if `n` is odd, then \(n^2\) is odd. Write
`n = 2k + 1`. Then

\[
n^2=(2k+1)^2=2(2k^2+2k)+1,
\]

which is odd. The contrapositive, and therefore the original statement, holds.

### Proof by contradiction

Assume the target statement is false and derive an impossibility. To prove that
no integer is both even and odd, suppose some integer `n` is both. Then
`n = 2a` and `n = 2b + 1` for integers `a` and `b`. Equating them gives

\[
2(a-b)=1.
\]

The left side is divisible by 2 while 1 is not, a contradiction. Therefore the
assumed integer does not exist.

A contradiction must follow from the stated assumptions and valid steps. Mere
surprise or a failed computer run is not a mathematical contradiction.

### Proof by induction

Induction proves a statement `P(n)` for every integer at or above a starting
point. It requires:

1. a **base case**;
2. an **induction hypothesis** assuming `P(k)` for an arbitrary eligible `k`;
3. an **inductive step** deriving `P(k+1)` from that hypothesis; and
4. a conclusion naming the covered range.

Prove that the sum of the first `n` odd positive integers is \(n^2\) for every
integer `n >= 0`. For `n=0`, the empty sum is 0, which equals \(0^2\). Assume the
sum of the first `k` odd numbers is \(k^2\). The next odd number is `2k+1`, so

\[
k^2+(2k+1)=(k+1)^2.
\]

The result follows for every nonnegative integer. Checking `n=0,1,2,3` could
help discover the pattern, but the base and inductive step establish the
unbounded claim.

### Proof, exhaustive finite checking, and sampling

Keep these evidence forms distinct:

- A **deductive proof** derives the claim from definitions, assumptions, and
  accepted rules for the entire stated domain.
- An **exhaustive finite check** evaluates every member of a specified finite
  domain. Its conclusion is limited to that domain and assumes the checker and
  execution behaved as modeled.
- A **sample test** evaluates some cases. One failure can refute a universal
  claim, but success supports only the sampled cases.

Every result should list its assumptions and scope. For a proof, that includes
definitions, domain, axioms, and imported lemmas. For a program run, it includes
the implementation, exact input range, interpreter, and observed result.

## Worked example

The included Python helper records an inclusive finite range and either the
first counterexample or the exact count of passing cases. From the repository
root, run:

```sh
cd curriculum/modules/mat-101
python3 checks/lab_smoke.py
```

The checker uses material implication for this false universal claim:

\[
\forall n\in\mathbb Z,\quad 2\mid n \Rightarrow 4\mid n.
\]

The finite run from 0 through 8 finds `n=2`, which is enough to refute the
universal claim. For the true converse over the same finite range, every checked
case passes, but the run reports only 0 through 8. A direct proof covers all
integers: if `4` divides `n`, then `n=4k=2(2k)`, so `2` divides `n`.

The helper also computes triangular sums. Tests compare

\[
1+2+\cdots+n=\frac{n(n+1)}2
\]

for finitely many `n`. Those tests can expose a defect in the implementation. An
induction proof is needed for the statement over every nonnegative integer.

Inspect `example/logic_scope/checks.py`. The `MAX_CASES` bound, inclusive range,
early counterexample, and result fields prevent a passing run from silently
claiming an infinite scope.

## Check your understanding

1. Is “`x + 1`” a proposition? What would make it one?
2. When is `P -> Q` false?
3. Negate “every integer has a larger integer.”
4. Give a counterexample to “every prime number is odd.”
5. State the contrapositive of “if a number is divisible by 6, it is divisible
   by 3.”
6. Name the four required parts of an induction argument.
7. A program checks a predicate for integers -1,000 through 1,000 and all pass.
   What may be concluded without another argument?

**Answers:** (1) no; place it in a truth-valued relation such as `x + 1 = 3`,
then bind or quantify `x`; (2) only when P is true and Q is false; (3) there
exists an integer with no larger integer; (4) 2; (5) if an
integer is not divisible by 3, then it is not divisible by 6; (6) base case,
induction hypothesis for arbitrary `k`, step from `k` to `k+1`, and a conclusion
naming the starting point and range; (7) the predicate passed those 2,001
checked cases under the program and execution assumptions.

## Next step

Complete the [lab](lab.md), then the [independent assessment](assessment.md).
Passing requires at least 80/100 and every critical criterion in the
[rubric](rubric.md).

`mat-102` uses these proof and scope habits for divisibility, Euclid's algorithm,
congruences, modular arithmetic, groups, rings, and fields.

## Sources

- Richard Hammack, [Book of Proof, third
  edition](https://richardhammack.github.io/BookOfProof/), statements,
  quantifiers, direct proof, contrapositive, contradiction, and induction.
- Eric Lehman, F. Thomson Leighton, and Albert R. Meyer, [Mathematics for
  Computer Science](https://courses.csail.mit.edu/6.042/spring18/mcs.pdf), logic,
  proof methods, and induction.
- Python Software Foundation, [Built-in
  Types](https://docs.python.org/3/library/stdtypes.html), Boolean operations and
  integer behavior used by the executable illustration.
- Python Software Foundation, [unittest — Unit testing
  framework](https://docs.python.org/3/library/unittest.html), local test runner
  used by the module check.
- [Assessment system](../../../docs/assessment-system.md), module evidence and
  pass policy.
