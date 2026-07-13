# Assessment: exact dice model and collision evidence

## Instructions

Complete this assessment independently with Python 3.11 or newer and only the
standard library. Work in a fresh temporary directory. Submit the finite model,
hand derivations, source, tests, failed-run evidence, seeded simulation record,
and reproducible command/result record. Do not copy or rename the module
examples or lab solution.

Use exact <code>Fraction</code> values for model probabilities. Clearly label
every bound and empirical estimate. This assessment covers:

- **MAT-104-01:** Model finite sample spaces, events, conditional probability,
  and independence.
- **MAT-104-02:** Compute expectation plus exact union, collision, and tail
  bounds for bounded cases.
- **MAT-104-03:** Implement exact enumeration and a reproducible simulation,
  then state sampling, error, and pseudorandom limitations.

## Knowledge check

1. Define sample space, outcome, event, uniform finite model, and random
   variable. Explain when <code>|E|/|Ω|</code> is valid.
2. Define conditional probability and independence. Prove that two disjoint
   events with positive probability cannot be independent.
3. Define expectation and explain why it need not be a possible single outcome.
4. Derive inclusion-exclusion for two events and state the finite union bound.
5. Derive the exact no-collision product and pairwise union bound for
   <code>k</code> draws into <code>m</code> uniform buckets.
6. State and prove Markov's inequality, including its premises.
7. Distinguish exact enumeration, a Monte Carlo estimate, observed absolute
   error, sampling uncertainty, and model error.
8. Explain why a fixed Python <code>random.Random</code> seed helps reproduction
   but cannot provide cryptographic unpredictability or an independent rerun.

## Independent task

1. **Finite model — MAT-104-01.** Model two ordered fair six-sided dice as all
   36 ordered pairs. Define <code>A</code> as “sum at least 10,” <code>B</code>
   as “first die is even,” and <code>C</code> as “the dice match.” List each
   event or provide a complete auditable comprehension and count. Compute
   <code>P(A)</code>, <code>P(B)</code>, <code>P(C)</code>,
   <code>P(A|B)</code>, and all intersections and products needed to decide
   independence for <code>(A,C)</code> and <code>(B,C)</code>. Justify the
   uniform and ordered-outcome premises.
2. **Expectation and exact bounds — MAT-104-02.** Let <code>X</code> be the dice
   sum. Derive <code>E[X]</code> from the 36 outcomes. Compute the exact
   <code>P(A union C)</code> and union bound; exact tail
   <code>P(X &gt;= 10)</code> and Markov bound at 10; and exact collision
   probability for five draws into 24 buckets plus the pairwise union bound.
   Show the formulas, reduce every fraction, verify each upper bound is at least
   its exact probability, and explain any looseness.
3. **Exact enumeration — MAT-104-03.** Create
   <code>dice_probability.py</code> that constructs the 36 outcomes and events
   from definitions, validates distinct uniform outcomes and exact Boolean
   event predicates, and computes every task-1 and task-2 dice result with
   <code>Fraction</code>. Do not hard-code final probabilities. Reject an event
   outside the space and conditioning on an empty event.
4. In the same source, implement bounded collision exact value, pair bound, and
   simulation. Enforce exact-integer bucket count 1 through 100,000, draw count
   0 through 100, trial count 1 through 100,000, and seed magnitude at most
   <code>2^63-1</code>. Use a private <code>random.Random(seed)</code>. Run
   10,000 trials for five draws into 24 buckets with seed 1,042,026; preserve
   the count, rational estimate, and exact absolute error against the exact
   formula. Repeat the same seed and require an identical result. Record a
   second seed as a separate sample without assuming it must differ.
5. Create <code>test_dice_probability.py</code>. Cover every exact assessed
   value, conditional error, both independence outcomes, event validation,
   union and tail bound inequalities, collision zero/certain/normal cases,
   every parameter endpoint and one outside each, Boolean and float rejection,
   same-seed reproduction, and exact result types. Deliberately corrupt one
   expected result, preserve the nonzero test run, restore it, and preserve the
   passing run.
6. Write <code>evidence-and-limits.md</code>. Record Python version, absolute
   workspace, source identity, exact commands and result channels, statuses,
   formulas, seed, trial count, observations, and work bounds. State what exact
   enumeration establishes for the declared model and what remains uncertain.
   Explicitly distinguish sampling error, model error, implementation error,
   reproducibility, independence, and pseudorandomness. State that Python
   <code>random</code> output is not suitable for keys, nonces, tokens,
   challenges, or other cryptographic decisions.

## Completion criteria

Use the [rubric](rubric.md). Passing requires at least 80/100 and every critical
criterion. The submission must:

- correctly model the ordered dice space, events, conditional probability, and
  both independence decisions for **MAT-104-01**;
- derive exact expectation, union, collision, and tail values and valid upper
  bounds for **MAT-104-02**;
- implement bounded exact enumeration, validation, failure-sensitive tests,
  and reproducible simulation with complete limitations for **MAT-104-03**;
  and
- never present a pseudorandom estimate as an exact probability or
  cryptographic randomness source.

Rounded float answers, an unvalidated sample space, a bound labeled as an exact
value, or a fixed seed presented as independent or secure cannot pass.
