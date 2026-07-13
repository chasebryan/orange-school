# Assessment: precise claims, proofs, and evidence scope

## Instructions

Complete this assessment independently in a fresh temporary directory. You may
consult the lesson and a notation reference, but not a completed lab dossier.
Use the definitions stated in the assessment and justify every algebraic step.

For the computational section, copy only the supplied `example` directory from
this module and use Python 3.11 or newer. Use no external package, network access,
or administrator command. Submit `proofs.md`, `finite-evidence.md`, the exact
command transcript, and any small Python file you create.

This assessment covers:

- **MAT-101-01:** Translate precise statements among prose, predicates,
  quantifiers, truth cases, and counterexamples.
- **MAT-101-02:** Construct direct, contrapositive, contradiction, and induction
  arguments.
- **MAT-101-03:** Distinguish proof from finite testing and enumerate assumptions
  and scope.

Unless otherwise stated, variables range over the integers. Define even, odd,
and divisibility before the first answer.

## Knowledge check

1. State the truth table for `P -> Q`. Explain why its converse is not generally
   equivalent and why its contrapositive is equivalent.
2. Translate and negate: “For every integer `x`, there exists an integer `y`
   such that `y > x`.” Do not leave a negation outside a quantifier.
3. Explain the logical difference between finding a witness for an existential
   claim and finding a counterexample to a universal claim.
4. For each proof method—direct, contrapositive, contradiction, and induction—
   state what is assumed and what must be derived.
5. Distinguish deductive proof, exhaustive checking of a declared finite domain,
   and sampling from a larger domain. Name one assumption for each.

## Independent task

Create `proofs.md` with three parts.

1. **Translation and truth analysis — MAT-101-01.** For each statement, supply a
   quantified predicate, a precise negation, a truth decision, and a witness or
   counterexample where applicable:

   A positive integer `p` is **prime** when `p > 1` and its only positive
   divisors are 1 and `p`.

   - Every integer divisible by 8 is even.
   - There exists a negative integer whose square is 16.
   - For every integer `x`, there exists an integer `y` such that `x + y = 0`.
   - Every odd positive integer is prime.
   - There exists an integer `y` greater than every integer `x`.

   For the first statement, also give the converse, inverse, and contrapositive,
   and classify each. Include the four truth cases for its implication without
   confusing a false antecedent with evidence that the consequent is true.

2. **Four complete proofs — MAT-101-02.** Write one argument for each named
   method. Every proof must name its proposition, domain, assumptions, arbitrary
   variables, justified steps, and final scope.

   - **Direct:** the sum of two integers divisible by 5 is divisible by 5.
   - **Contrapositive:** if the square of an integer is odd, the integer is odd.
   - **Contradiction:** there is no greatest integer.
   - **Induction:** for every integer `n >= 0`,
     `1 + 2 + ... + n = n(n + 1)/2`, with the `n=0` empty-sum base case.

   The induction step must begin from the hypothesis for an arbitrary `k >= 0`
   and derive the exact formula for `k+1`. Checking several values earns no proof
   credit for the unbounded conclusion.

3. **Finite evidence and claim limits — MAT-101-03.** Use
   `check_integer_claim` to check these encoded predicates over the inclusive
   range -200 through 200:

   - if an integer is divisible by 8, then it is even;
   - if an integer is even, then it is divisible by 8; and
   - if an integer's square is odd, the integer is odd.

   Preserve the source, Python version, exact command, stdout, stderr, and exit
   status in `finite-evidence.md`. For each result, record the requested range,
   checked count, first counterexample if present, narrow conclusion, and whether
   the result refutes or merely samples the corresponding universal claim.

   Then compare the finite run with your contrapositive proof. List at least five
   assumptions or scope facts for the proof and five for the computation. State
   at least three limits of each. Do not describe the finite passing cases as a
   proof over all integers.

## Completion criteria

Use the [rubric](rubric.md). Passing requires at least 80/100 and every critical
criterion. A complete submission must show:

- correct domains, predicates, quantifiers, negations, truth cases, witnesses,
  and counterexamples for **MAT-101-01**;
- valid direct, contrapositive, contradiction, and induction arguments rather
  than examples or unexplained algebra for **MAT-101-02**;
- reproducible bounded computation, precise claim language, and explicit proof
  and test assumptions/scope for **MAT-101-03**; and
- correct knowledge answers, readable notation, and no hidden dependence on
  network services or external Python packages.

One valid counterexample may refute a universal statement. A finite list of
passing cases cannot earn proof credit for an infinite domain.
