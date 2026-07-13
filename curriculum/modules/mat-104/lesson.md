# Discrete probability and statistical evidence

Probability begins with a model: a specified set of possible outcomes and a
rule assigning mass to them. Exact enumeration can settle a bounded finite
model. Simulation instead samples from an implemented pseudorandom process and
produces an estimate with sampling error. Neither result is stronger than its
model, implementation, and evidence record.

This module uses exact rational arithmetic for model calculations and a seeded,
bounded Python simulation for reproducibility. Python's <code>random</code>
module is not a cryptographic randomness source.

## Learning objectives

- **MAT-104-01:** Model finite sample spaces, events, conditional probability,
  and independence.
- **MAT-104-02:** Compute expectation plus exact union, collision, and tail
  bounds for bounded cases.
- **MAT-104-03:** Implement exact enumeration and a reproducible simulation,
  then state sampling, error, and pseudorandom limitations.

## Prerequisites

Pass <code>mat-101</code> and <code>prg-101</code>. You should be able to use
sets, functions, finite sums, implications, basic proof and counterexample
methods, and bounded Python functions, loops, validation, and tests. No prior
statistics package, floating-point analysis, or cryptographic-randomness API is
assumed.

Use Python 3.11 or newer and only the standard library. The exact examples use
<code>fractions.Fraction</code>; the simulation uses a private
<code>random.Random</code> instance with explicit bounds and seed. No network,
administrator access, or external package is required.

## Lesson

### Start with the experiment and sample space

A **sample space** <code>Ω</code> is the set of mutually exclusive outcomes the
model permits. An **event** is a subset of <code>Ω</code>. The event occurs when
the observed outcome belongs to that subset.

For two ordered fair binary trials, use

~~~text
Ω = {(0,0), (0,1), (1,0), (1,1)}.
~~~

Order is part of each outcome: <code>(0,1)</code> and <code>(1,0)</code> are
different. The sample space has four equally likely outcomes. Define:

~~~text
A = {outcomes whose first coordinate is 1}
B = {outcomes whose second coordinate is 1}
C = {outcomes with at least one 1}.
~~~

Then <code>A = {(1,0),(1,1)}</code>, <code>B = {(0,1),(1,1)}</code>, and
<code>C = {(0,1),(1,0),(1,1)}</code>.

In a finite **uniform** sample space,

~~~text
P(E) = |E| / |Ω|.
~~~

Thus <code>P(A)=1/2</code> and <code>P(C)=3/4</code>. Uniformity is a model
premise, not a consequence of listing outcomes. If outcomes have unequal
probabilities, assign explicit nonnegative weights summing to 1 instead; simple
counting is then invalid.

The supplied code enforces a narrower uniform-space contract: 1 through 65,536
distinct hashable outcomes. Its event builder requires a callable predicate
and requires <code>type(result) is bool</code> for every outcome. Returning 1,
a nonempty string, or another merely truthy value is rejected rather than
silently changing the event definition.

### Conditional probability changes the denominator

For <code>P(B) &gt; 0</code>, conditional probability is

~~~text
P(A | B) = P(A intersection B) / P(B).
~~~

Conditioning restricts the sample space to outcomes in <code>B</code> and
renormalizes their mass. In the two-bit example,
<code>A intersection B = {(1,1)}</code>, so

~~~text
P(A | B) = (1/4) / (1/2) = 1/2.
~~~

Conditioning on an event of probability zero is undefined in this finite
formula. The implementation rejects an empty conditioning event instead of
inventing a number.

### Independence is an equality to check

Events <code>A</code> and <code>B</code> are independent exactly when

~~~text
P(A intersection B) = P(A) P(B).
~~~

Here, both sides are <code>1/4</code>, so the two coordinate events are
independent in this model. Equivalently, when the conditional probabilities
are defined, <code>P(A|B)=P(A)</code>.

Independence is not the same as disjointness. If two positive-probability
events are disjoint, their intersection probability is 0 while the product of
their probabilities is positive, so they are dependent. Independence is also
model-specific: a different sampling mechanism can change it.

### Expectation is a weighted sum

A discrete random variable <code>X</code> is a function from outcomes to exact
numeric values. Its expectation is

~~~text
E[X] = sum over omega in Ω of X(omega) P({omega}).
~~~

Let <code>X</code> count ones in the two-bit outcome. Its values are
0, 1, 1, and 2, so

~~~text
E[X] = (0 + 1 + 1 + 2) / 4 = 1.
~~~

Expectation is an average in the model, not a prediction that the next outcome
will equal 1. Linearity gives <code>E[X+Y]=E[X]+E[Y]</code> even when the
variables are dependent, provided the finite expectations exist.

The example accepts only <code>int</code> and <code>Fraction</code> values for
exact model calculations. It rejects floats so a rounded binary approximation
cannot masquerade as an exact probability.

### Exact unions and the union bound

For two events,

~~~text
P(A union B) = P(A) + P(B) - P(A intersection B).
~~~

The subtraction prevents double-counting. For any finite event collection,
the union bound gives

~~~text
P(union of E_i) <= sum of P(E_i).
~~~

Probability is at most 1, so the code reports
<code>min(1, sum P(E_i))</code>. For the two coordinate events, the exact union
probability is <code>3/4</code>, while the union bound is 1. An upper bound can
be correct and loose.

One proof uses indicator variables: the indicator of the union is at most the
sum of the individual indicators for every outcome. Taking expectations
preserves that inequality.

### Collision probability: exact value and pair bound

Draw <code>k</code> times independently and uniformly with replacement from
<code>m</code> buckets. If <code>k <= m</code>, the probability of no collision
is

~~~text
m(m-1)(m-2)...(m-k+1) / m^k.
~~~

Therefore

~~~text
P(at least one collision)
  = 1 - m(m-1)...(m-k+1) / m^k.
~~~

For three draws into eight buckets, this is

~~~text
1 - (8*7*6)/8^3 = 11/32.
~~~

There are <code>choose(k,2)</code> pairs of draw positions. Each pair matches
with probability <code>1/m</code>. Applying the union bound gives

~~~text
P(collision) <= choose(k,2)/m.
~~~

For the same example, the bound is <code>3/8</code>, which is greater than
<code>11/32</code>. If <code>k &gt; m</code>, a collision is certain by the
pigeonhole principle. The code computes all values as reduced fractions.

### Exact tails and Markov's bound

A tail event has the form <code>{X >= t}</code>. A bounded finite sample space
can enumerate it exactly. For the two-bit count,

~~~text
P(X >= 2) = 1/4.
~~~

For every nonnegative random variable and positive threshold,
Markov's inequality gives

~~~text
P(X >= t) <= E[X] / t.
~~~

The proof is pointwise: <code>X</code> is at least <code>t</code> on the tail,
so <code>E[X] >= t P(X>=t)</code>. For <code>E[X]=1</code> and
<code>t=2</code>, the bound is <code>1/2</code>. Again, the exact tail
probability <code>1/4</code> is below a valid but loose bound.

The nonnegative and positive-threshold premises are essential. The example
rejects negative variable values and thresholds at or below zero for the
Markov calculation.

### Enumeration is exact for the declared finite model

The [probability library](examples/discrete_probability.py) constructs ordered
binary spaces with <code>itertools.product</code>. It permits at most 16 binary
trials, or 65,536 outcomes. Enumeration work and storage grow as
<code>2^n</code>; the bound is checked before constructing the tuple.

Exact enumeration removes Monte Carlo sampling error for that finite model. It
does not prove that the model matches a physical process, that the event was
specified correctly, or that the implementation is defect-free. Tests compare
known cases and rejected inputs; mathematical derivations justify the formulas.

### Simulation produces a sample estimate

For an event with modeled probability <code>p</code>, simulate
<code>N</code> trials and observe <code>C</code> occurrences. The empirical
estimate is <code>C/N</code>. It is a random variable across independently
sampled runs, not the exact <code>p</code>.

When the exact model value is known, the observed absolute error
<code>|C/N-p|</code> can be computed exactly after the run. That one observed
error is not a guarantee for another seed, larger model, or real system.
Increasing <code>N</code> generally reduces sampling variability, but it does
not correct a biased generator, wrong model, incorrect event, or software bug.

The example bounds bucket count, draws per trial, number of simulation trials,
and seed. It constructs <code>random.Random(seed)</code> locally rather than
changing Python's module-global generator. Record at least:

- Python version and source revision;
- model parameters and trial count;
- exact seed and generator API;
- event definition;
- count, rational estimate, and any exact-model comparison; and
- sampling, model, implementation, and portability limits.

The same seed, code, parameters, and declared Python environment reproduce the
same local pseudorandom run. Repeating the same seed does not provide an
independent sample; it replays the same stream. A different seed can produce a
different estimate but does not by itself validate the model.

### Python random is not cryptographic randomness

Python's <code>random</code> module uses the deterministic Mersenne Twister and
its documentation excludes it from cryptographic use. A published seed makes
this lesson's sequence intentionally replayable and therefore predictable.
Do not use this simulation path for keys, nonces, salts, challenges, tokens, or
adversarial security decisions.

Python's <code>secrets</code> module is intended for security-sensitive tokens,
but selecting a security API does not by itself establish entropy quality,
protocol correctness, uniform mapping, side-channel safety, or compliance with
a cryptographic standard. Professional cryptographic randomness work must use
the ratified design, supported platform source, and applicable validation
requirements. This module makes no such claim.

## Worked example

Run the exact model, bounded simulation, and smoke check from the module
directory:

~~~sh
cd curriculum/modules/mat-104
PYTHONDONTWRITEBYTECODE=1 python3 examples/probability_worked.py
PYTHONDONTWRITEBYTECODE=1 python3 checks/lab_smoke.py
~~~

The worked program prints the two-bit event and conditional probabilities,
independence result, expectation, exact union and bound, exact tail and Markov
bound, exact collision probability and pair bound, then one seeded collision
estimate and its exact observed error. The estimate can be read only with its
seed, trial count, Python environment, and limitations.

The smoke check covers normal, boundary, and invalid spaces and events;
conditional and independence cases; exact expectations, unions, tails, and
collisions; bounded enumeration; repeatability with the same seed; explicit
simulation bounds; the non-cryptographic source boundary; and a subprocess
run. It must print <code>mat-104 lab smoke: PASS</code> and exit 0.

## Check your understanding

1. Why must <code>(0,1)</code> and <code>(1,0)</code> both appear in the
   two-trial sample space?
2. When is counting outcomes sufficient to compute probability?
3. Define conditional probability and state its denominator premise.
4. Why are two disjoint positive-probability events not independent?
5. Distinguish an exact union probability from the union bound.
6. Derive the no-collision product for three draws into eight buckets.
7. What premises does Markov's inequality require?
8. Why does replaying a seeded <code>random.Random</code> simulation neither
   supply an independent sample nor provide cryptographic randomness?

**Answers:** (1) ordered trials distinguish which position produced each
value; (2) when the finite listed outcomes are mutually exclusive and equally
likely; (3) <code>P(A|B)=P(A intersection B)/P(B)</code> with
<code>P(B)&gt;0</code>; (4) their intersection has probability 0 while the
product is positive; (5) the exact value accounts for overlaps, while the sum
bound can overcount; (6) successive no-match probabilities are
<code>1, 7/8, 6/8</code>, giving <code>(8*7*6)/8^3</code>; (7) a nonnegative
variable and positive threshold; (8) the same seed replays one deterministic
pseudorandom stream, and that predictable generator is not designed to resist
an adversary.

## Next step

Complete the [lab](lab.md), including hand-modeled events, exact fractions,
changed enumeration code, failure-sensitive tests, and reproducible simulation
record. Then take the [independent assessment](assessment.md). Passing requires
at least 80/100 and every critical criterion in the [rubric](rubric.md).

## Sources

- National Institute of Standards and Technology, [Engineering Statistics
  Handbook, Probability](https://www.itl.nist.gov/div898/handbook/eda/section3/eda36.htm),
  probability models, expectation, conditional probability, and independence.
- Michael Mitzenmacher and Eli Upfal, [Probability and Computing, selected
  chapter notes](https://www.cambridge.org/core/books/probability-and-computing/),
  indicator variables, union bounds, Markov bounds, and collision reasoning.
- Python Software Foundation, [Python 3.11 <code>fractions</code>
  documentation](https://docs.python.org/3.11/library/fractions.html) and
  [<code>itertools</code> documentation](https://docs.python.org/3.11/library/itertools.html),
  exact rational values and Cartesian-product enumeration.
- Python Software Foundation, [Python 3.11 <code>random</code>
  documentation](https://docs.python.org/3.11/library/random.html) and
  [<code>secrets</code> documentation](https://docs.python.org/3.11/library/secrets.html),
  deterministic simulation and the security-use boundary.
- NIST Computer Security Resource Center, [Random Bit Generation
  project](https://csrc.nist.gov/Projects/random-bit-generation), entropy
  sources, deterministic generators, and cryptographic validation context.
- [Assessment system](../../../docs/assessment-system.md), executable evidence,
  critical criteria, and module pass policy.
