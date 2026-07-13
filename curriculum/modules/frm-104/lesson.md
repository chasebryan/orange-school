# Probabilistic games, reductions, and concrete security bounds

Security claims are quantified comparisons between experiments. A game fixes
what is random, what an adversary sees and controls, when it wins, and which
resources it may use. A reduction explains how an adversary that separates two
games would yield an algorithm against a named assumption. Neither vocabulary
nor a green simulation supplies the missing quantifiers or proof.

This module uses a deliberately tiny finite bit game. It teaches exact
probability, game hops, and bound accounting; it does not implement
cryptography, formalize a deployed protocol, or make any claim about Orange.

## Learning objectives

- **FRM-104-01:** Specify a bounded probabilistic security game with challenger,
  adversary, randomness, interfaces, transcript, win event, baseline,
  advantage, resource bounds, and quantifier order.
- **FRM-104-02:** Construct reviewable game hops and reductions whose assumptions,
  bad events, loss terms, and concrete bounds are explicit and directionally
  valid.
- **FRM-104-03:** Distinguish proof from exact finite enumeration and seeded
  simulation, then produce boundary, relational, deliberate-failure, and
  reproducibility evidence with calibrated claims.

## Prerequisites

Pass <code>frm-101</code>, <code>mat-104</code>, and <code>cry-101</code>. You
should be able to read quantifiers and invariants, manipulate finite
probabilities, distinguish assumptions from observations, and state an
attacker-matched security goal. Examples require Python 3.11 or newer and only
the standard library. They are deterministic or explicitly seeded, offline,
and bounded.

## Lesson

### A game is a complete probability experiment

A **probabilistic game** is an algorithmic experiment between a challenger and
an adversary. A reviewable definition states all of these parts:

1. parameters and their admissible range;
2. the probability space, including every random choice and its distribution;
3. challenger state and initialization;
4. public input and any secret input;
5. every adversary interface, query restriction, and response;
6. the transcript or observation available to the adversary;
7. the adversary output and exact Boolean win event;
8. the baseline probability that the chosen advantage subtracts;
9. time, memory, query, message-length, concurrency, and success bounds; and
10. the order and domain of every quantifier.

“The attacker cannot tell” omits almost all of that contract. A typical
bit-guessing experiment samples a uniform hidden bit <code>b</code>, constructs
one of two challenge worlds, gives the adversary a declared interface, and
wins when its output <code>b'</code> equals <code>b</code>. One possible
advantage convention is

~~~text
Adv(A) = | Pr[b' = b] - 1/2 |.
~~~

Some sources instead use twice this quantity or a difference between two
conditional probabilities. These conventions are related but not identical.
State the convention before comparing a theorem, requirement, or parameter
table. The absolute value prevents a systematically wrong guesser from being
called harmless: complementing that guess produces a systematically right
one.

A probability is taken over all declared coins: setup, challenger, oracle,
adversary, and sometimes environment coins. “Adversary randomness” can be
modeled by fixing its coins and averaging, or by including them explicitly.
For a finite model, checking every deterministic strategy can cover randomized
mixtures because their success probability is a convex combination. That
finite fact does not enumerate arbitrary efficient programs in a real
definition.

### Quantifiers determine the strength of the claim

Compare these shapes:

~~~text
for every allowed adversary A, Adv_Game(A, k, q) <= epsilon(k, q)

for this program A0 and these eight deterministic strategies,
the finite enumerator returned maximum advantage 19/128
~~~

The second is an exact result about a bounded model. It is not the first
statement. A cryptographic definition commonly quantifies over every
adversary in a resource class and every admissible security parameter. A
concrete theorem may instead state a numerical bound for adversaries with at
most <code>t</code> time, <code>q</code> queries, and <code>mu</code> processed
bytes. A claim must preserve whether a bound is asymptotic or concrete and
whether security holds for every parameter, sufficiently large parameters, or
one configured parameter.

Quantifier order matters. “For every adversary there exists a simulator” lets
the simulator depend on the adversary. “There exists one simulator for every
adversary” is usually stronger. Sampling a key after the adversary fixes its
challenge differs from allowing a challenge chosen after key-dependent
observations. Write the experiment in execution order and the claim in
quantifier order.

### Adversaries are algorithms with interfaces and budgets

An adversary is not merely a person or threat label. In the game it is an
algorithm receiving exact inputs and invoking exact interfaces. State whether
queries are adaptive, whether repetitions are allowed, and which challenge-
related query would trivially reveal the answer. Define what happens on an
invalid or over-budget query; silent omission changes the experiment.

Budgets make reductions meaningful. If a reduction invokes adversary
<code>A</code> once and performs <code>q</code> table operations, its running
time is not simply <code>t_A</code>. If it rewinds <code>A</code>, guesses one
of <code>q</code> positions, or aborts unless an event occurs, the success and
runtime losses must appear. An implementation budget measured in wall-clock
seconds is environment-specific; a theorem may use an abstract operation or
circuit bound. Do not silently substitute one for the other.

### Game hops isolate one change at a time

A **game hop** replaces Game 0 with a neighboring Game 1 and proves that the
chosen observation or win probability changes by at most a named term. A useful
hop record includes:

- the exact lines, distribution, interface, or state transition changed;
- a coupling, identical-until-bad argument, statistical distance fact, or
  reduction that justifies the comparison;
- the event whose probability bounds the difference;
- the direction and magnitude of the inequality; and
- every parameter and assumption on which the term depends.

If Games 0 and 1 are identical until event <code>Bad</code>, a standard bound
shape is

~~~text
|Pr[G0 wins] - Pr[G1 wins]| <= Pr[Bad].
~~~

The right side must be evaluated in a game where it is defined, and the proof
must justify the coupling. Similar-looking programs are not automatically
identical until bad. If the bad event changes when the games diverge, specify
which game's probability is used or provide a common coupled experiment.

For a chain <code>G0, G1, ..., Gn</code>, the triangle inequality yields a sum
of adjacent gaps. This can be correct but loose. A bound larger than the
maximum possible advantage is **vacuous**: valid but uninformative. Keep terms
as exact rational expressions as long as possible, substitute deployment
parameters once, and report a conservative rounding direction.

### Reductions connect a game gap to an assumption

A **reduction** is an algorithm <code>B</code> that uses an alleged adversary
<code>A</code> as a component. It simulates the game interface for
<code>A</code>, embeds its own challenge, translates outputs, and wins an
assumption game often enough that a successful <code>A</code> would contradict
the assumption. A complete reduction states:

1. the exact assumption game and its advantage convention;
2. how <code>B</code> initializes and answers every <code>A</code> query;
3. which distributions are exact and which are merely close;
4. when <code>B</code> aborts, guesses, rewinds, or fails to simulate;
5. how a win by <code>A</code> becomes a win by <code>B</code>;
6. the success relation, including signs and multiplicative/additive losses;
7. <code>B</code>'s time, memory, query, and data costs as functions of
   <code>A</code>'s costs; and
8. the resulting conditional theorem.

The useful direction normally has the form

~~~text
Adv_target(A) <= loss * Adv_assumption(B) + bad_terms.
~~~

An argument proving only <code>Adv_assumption(B) <= Adv_target(A)</code> does
not upper-bound the target. Nor may an empirical simulation term be inserted
where “simulation” means the mathematical algorithm that emulates an
interface. The words coincide; the evidence categories do not.

An assumption is a quantified bound, not “this problem seems difficult.” Name
the problem variant, parameter generation, adversary resources, success
metric, and bound. A proof based on that assumption is conditional. It does
not validate the primitive implementation, randomness source, protocol state,
side-channel behavior, key management, or deployment configuration.

### Concrete bounds retain every loss term

Suppose a target theorem produces

~~~text
Adv_target(A) <= Adv_primitive(B) + q(q-1)/(2N) + delta_sim.
~~~

The second term may be a collision union bound over <code>q</code> draws from
an <code>N</code>-element space. It is an upper bound, not generally the exact
collision probability. It should be capped at 1 when treated as a probability.
The third term is valid only if a mathematical simulation/reduction lemma
defines it; it is not a Monte Carlo confidence allowance unless the theorem is
explicitly statistical.

Concrete evaluation records <code>q</code>, <code>N</code>, the primitive
assumption bound at <code>B</code>'s actual resources, every reduction loss,
and the total. It also states whether the total is below the maximum advantage
under the selected convention. A small symbolic expression with unrealistic
resource conversion is not a useful deployment claim. Conversely, a loose
but honest bound identifies exactly which proof or parameter term needs work.

### Exact enumeration and simulation answer different questions

**Exact enumeration** visits every point in a declared finite sample space and
computes a rational count. It can establish the exact result of that executable
finite model, assuming the enumerator and model correspond to the written
definition. Its cost grows with the sample space; an endpoint must be bounded
before execution. It does not prove a claim over omitted parameters,
unrepresented adversaries, unbounded inputs, or real cryptographic objects.

**Simulation** samples some points. A fixed seed makes the run replayable, not
independent and not exact. A sample frequency is an estimator whose uncertainty
depends on the sampling design and number of trials. Trying more seeds until a
desired number appears invalidates a predeclared analysis. A simulation can
find counterexamples, test plumbing, compare an estimator to an exact toy
answer, or explore scale. It cannot prove that a nonzero event is impossible;
not observing it supplies only sampling evidence under a stated model.

The supplied model therefore returns <code>Fraction</code> values for exact
enumeration and <code>float</code> values named <code>win_rate</code> and
<code>observed_advantage</code> for simulation. It enforces a denominator cap
of 64, a simulation cap of 100,000, and exact input types. Those checks bound
the course program; they are not security parameters for any construction.

### Evidence must be failure-sensitive and relational

A single expected output is weak evidence. Useful checks include:

- **boundary:** the largest admitted denominator runs, and 65 is rejected;
- **relational:** at trigger probability zero the neighboring games agree;
- **algebraic:** the copy strategy has advantage <code>p/2</code> in the real
  toy game and zero in the ideal game;
- **adversarial:** malformed games, strategies, probabilities, and bound terms
  are rejected rather than coerced;
- **deliberate failure:** a false <code>1/8</code> claim for the
  <code>p=1/8</code> case fails before the correct <code>1/16</code> claim is
  restored; and
- **replay:** a seeded run reproduces byte-for-byte while remaining labeled a
  sample.

Evidence records command, working directory, Python version, source identity,
stdout, stderr, immediate status, bounds, and which claim each observation
supports. “Tests passed” is not a proof label.

## Worked example

The supplied expose-or-hide game samples a uniform secret bit, a trigger index,
and an independent fake bit. With trigger probability <code>p</code>, the real
game exposes the secret; otherwise it shows <code>(hidden, 0)</code>. The ideal
game exposes the independent fake bit on the trigger. The adversary copies an
exposed payload and guesses zero on a hidden view.

For <code>p=1/8</code>, the real adversary wins whenever the secret is zero and,
when it is one, only when exposure occurs:

~~~text
Pr[real win] = 1/2 + (1/2)(1/8) = 9/16
Adv_real      = |9/16 - 1/2| = 1/16.
~~~

In the ideal game the exposed fake is independent of the secret, so the win
probability is <code>1/2</code> and advantage is zero. The adjacent win gap is
<code>1/16</code>, within the declared bad-event upper bound
<code>Pr[trigger] = 1/8</code>. The bound is sound but loose by a factor of two
for this strategy.

Run the model from the repository root:

~~~sh
PYTHONDONTWRITEBYTECODE=1 python3 curriculum/modules/frm-104/examples/worked_game.py
PYTHONDONTWRITEBYTECODE=1 python3 curriculum/modules/frm-104/checks/lab_smoke.py
~~~

The program enumerates <code>2 * 8 * 2 = 32</code> aligned points. Its seeded
4,096-trial frequency may differ from <code>9/16</code>; that difference does
not refute the exact count and matching it would not prove the general theorem.
The exact result covers this model, these bounded parameters, and the eight
deterministic three-view strategies only.

## Check your understanding

1. Why must a game include the adversary interface and forbidden queries, not
   only the win event?
2. Under the lesson's convention, what is the maximum possible bit-guessing
   advantage? When is an upper bound vacuous?
3. Explain the difference between “a simulator in a reduction” and “a seeded
   Monte Carlo simulation.”
4. What additional obligations arise if a reduction guesses one of
   <code>q</code> queries as the challenge location?
5. Why does “identical until bad” require a coupling argument and a named game
   for <code>Pr[Bad]</code>?
6. Calculate <code>q(q-1)/(2N)</code> for <code>q=32</code> and
   <code>N=65,536</code>. Is it an exact collision probability?
7. What can exact enumeration establish that simulation cannot? What real
   security theorem can neither establish alone?
8. Identify the quantifier mismatch between eight enumerated finite strategies
   and all efficient probabilistic adversaries.

## Next step

Complete the lab by writing an independent game ledger before changing any
code. Preserve the supplied smoke result, then produce exact, relational,
boundary, and deliberately failing evidence in a fresh temporary directory.
Keep the exact model claim separate from the empirical sample and the
conditional reduction worksheet.

## Sources

- Mihir Bellare and Phillip Rogaway, *Introduction to Modern Cryptography*,
  2005 course notes, sections on games, reductions, and concrete security.
- Victor Shoup, *Sequences of Games: A Tool for Taming Complexity in Security
  Proofs*, 2004, game-sequence method and transition bounds.
- Oded Goldreich, *Foundations of Cryptography, Volume 1*, 2001, computational
  models, probabilistic algorithms, reductions, and security definitions.
- Michael Mitzenmacher and Eli Upfal, *Probability and Computing*, 2005,
  finite probability spaces, union bounds, randomized algorithms, and
  experiment interpretation.

These sources support the mathematical method. The supplied Python files are
independent course teaching artifacts and are not implementations from those
sources.
