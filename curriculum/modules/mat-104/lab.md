# Lab: exact finite models and reproducible simulation

## Goal

Model a finite experiment and its events, compute exact conditional,
independence, expectation, union, collision, and tail results, then implement
bounded enumeration and a reproducible non-cryptographic simulation with an
honest error record.

## Setup

From the repository root, inspect and run the supplied examples:

~~~sh
cd curriculum/modules/mat-104
python3 --version
PYTHONDONTWRITEBYTECODE=1 python3 examples/probability_worked.py
PYTHONDONTWRITEBYTECODE=1 python3 checks/lab_smoke.py
~~~

The final command must print <code>mat-104 lab smoke: PASS</code> and exit 0.
It uses local files and Python's standard library only.

Create a separate temporary workspace:

~~~sh
workdir="$(mktemp -d)"
cd -- "$workdir"
pwd
~~~

Keep all learner-created files under the printed path. Use
<code>Fraction</code> for exact probabilities. No network, administrator
access, external package, permission change, or deletion command is required.

## Tasks

1. **Model three ordered fair binary trials.** Write all eight outcomes in
   <code>Ω = {0,1}^3</code>. Define:

   - <code>A</code>: the first coordinate is 1;
   - <code>B</code>: exactly two coordinates are 1; and
   - <code>C</code>: the third coordinate is 1.

   List each event explicitly. State why the outcomes are distinct, mutually
   exclusive, and equally likely under the model. Compute
   <code>P(A)</code>, <code>P(B)</code>, <code>P(C)</code>,
   <code>P(B|A)</code>, and every intersection needed to decide whether
   <code>A</code> is independent of <code>B</code> and of <code>C</code>.
   Use the product equality, not intuition.
2. **Compute exact values and bounds.** Let <code>X</code> be the number of ones.
   Make an eight-row table with outcome, <code>X</code>, and membership in each
   event. Derive:

   - <code>E[X]</code> from the complete sum;
   - the exact <code>P(B union C)</code> by inclusion-exclusion and its union
     bound;
   - the exact tail <code>P(X &gt;= 2)</code> and the Markov bound at 2; and
   - the exact probability of at least one collision in four draws into 16
     uniform buckets, plus the pairwise union bound.

   Reduce every fraction and state which values are exact, which are upper
   bounds, and where a bound is loose.
3. **Audit the supplied implementation.** In
   [<code>discrete_probability.py</code>](examples/discrete_probability.py),
   identify the uniform-space, event, conditioning, exact-number, enumeration,
   collision, simulation, and seed invariants. Explain why event predicates
   must be callable and return exact <code>bool</code> values, why floats are
   rejected in exact calculations, and why a local seeded generator is used.
   State the maximum enumerated outcomes and maximum simulated bucket draws.
4. **Implement a changed case.** Create <code>probability_lab.py</code> using
   only Python 3.11's standard library. It must:

   - enumerate exactly the eight ordered outcomes, build <code>A</code>,
     <code>B</code>, and <code>C</code>, and return exact
     <code>Fraction</code> results for task 1;
   - compute expectation, exact union, union bound, exact tail, and Markov bound
     from enumeration rather than hard-coded answers;
   - compute collision exact value and pair bound from bounded integer
     parameters <code>1 &lt;= m &lt;= 10,000</code> and
     <code>0 &lt;= k &lt;= 50</code>;
   - simulate that collision event with a private
     <code>random.Random(seed)</code>, 1 through 50,000 trials, and exact
     integer seed magnitude at most <code>2^63-1</code>; and
   - return the collision count and <code>Fraction(count, trials)</code>, never
     present the estimate as an exact model probability, and label the path
     non-cryptographic.

   Run 5,000 trials for four draws into 16 buckets with seed 10,403. Record the
   exact model probability, estimate, and exact absolute observed error. Rerun
   the same seed and require an identical result. Run seed 10,404 as a separate
   sample, but do not require it to differ.
5. **Test the contracts.** Create <code>test_probability_lab.py</code> with
   <code>unittest</code>. Cover the exact task-1 and task-2 results; event subset
   and zero-probability conditioning errors; non-callable and non-Boolean event
   predicates; exact rational return types; collision cases with zero draws,
   more draws than buckets, and exact parameter endpoints; same-seed replay;
   one trial and 50,000 trials; out-of-range trials, draws, buckets, and seed;
   and rejection of Boolean and float inputs where exact integers are required.
   Deliberately make one expected probability wrong, preserve the failing
   status, restore it, and preserve the passing run.
6. **Write a reproducibility and limits record.** Include Python version,
   absolute directory, source identity, model, event definitions, exact
   formulas, commands, stdout, stderr, immediate statuses, seed, trial count,
   observed count, estimate, error, and work bounds. State that:

   - enumeration is exact only for the declared finite uniform model;
   - a simulation has sampling error and can encode model or code error;
   - repeating one seed replays rather than independently resamples;
   - results may depend on the declared Python generator implementation; and
   - <code>random.Random</code> is predictable and must not be used for
     cryptographic values or adversarial security decisions.

## Verification

From the temporary workspace, run:

~~~sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v
test_status=$?
printf 'test status: %s\n' "$test_status"
~~~

Status 0 is necessary but not sufficient. Inspect the model, derivations,
source, tests, failed-run record, and limitations. Confirm that:

- the eight outcomes and event subsets match the prose definitions;
- conditional denominators and independence products are visible;
- every exact result is a reduced <code>Fraction</code> derived from the model;
- union, collision, and Markov bounds are not labeled as exact event values;
- bounds are validated before enumeration or simulation;
- the deliberate wrong expectation made the suite nonzero before restoration;
  and
- the seeded run is labeled reproducible pseudorandom simulation, not
  cryptographic randomness or proof of the exact probability.

Rerun the repository smoke check separately from the module directory.

## Reflection

Write four to six sentences:

- Which premise permitted probability to equal an outcome count ratio?
- Which pair of events was independent, and which exact equality established
  it?
- Where were the union and Markov bounds loose?
- What did exact enumeration remove that simulation retained?
- Why is a fixed seed useful for debugging but unsuitable as cryptographic
  randomness evidence?
