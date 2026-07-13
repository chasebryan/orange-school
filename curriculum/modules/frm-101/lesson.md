# Specifications, contracts, invariants, and refinement

Testing asks what a program did on selected executions. A specification says
what every execution inside a stated scope is required to do. Formal work is
useful when it makes that scope, its assumptions, the obligations, and a
failure witness precise enough for another person to check.

This module uses **Aster**, an independent finite teaching model. Aster is not
Orange syntax, an Orange verifier, or evidence that Orange implements contracts
or formal verification.

## Learning objectives

- **FRM-101-01:** Write bounded specifications with explicit assumptions,
  preconditions, postconditions, old-state references, and structured
  counterexamples.
- **FRM-101-02:** Distinguish partial from total correctness and check loop
  initialization, invariant preservation, exit reasoning, and a decreasing
  nonnegative variant.
- **FRM-101-03:** Check a finite behavioral refinement by preventing stronger
  concrete input requirements and requiring concrete results to satisfy the
  abstract postcondition.
- **FRM-101-04:** Produce reproducible executable evidence at every exact
  resource endpoint and smallest constructible overflow while stating what
  finite checking does not prove.

## Prerequisites

Pass <code>plt-102</code> and <code>mat-101</code>. You should be able to read a
small immutable abstract syntax tree, trace deterministic evaluation, use
logical predicates and quantifiers, and construct a counterexample. The model
requires Python 3.11 or newer, uses only the standard library, works offline,
and writes generated evidence only to a temporary directory.

## Lesson

### A contract separates the world from the obligation

For a command <code>C</code>, write a Hoare triple:

~~~text
{P} C {Q}
~~~

The precondition <code>P</code> is the caller's obligation. If execution begins
in a state satisfying <code>P</code>, the command owes the postcondition
<code>Q</code>. A postcondition may relate the final state to an **old** value
captured at entry. For example, a decrement operation might promise
<code>value = old(value) - 1</code>.

An **assumption** is different. It records a fact supplied by the model or
environment: perhaps the input is within a finite domain, arithmetic does not
fault, or a dependency obeys its interface. Hiding an assumption inside a
precondition makes it easy to blame the caller for a fact outside the caller's
control. Hiding it completely makes the conclusion look broader than it is.

Aster therefore stores three separate Boolean formulas:

1. an assumption selecting the modeled world;
2. a precondition selecting valid calls inside that world; and
3. a postcondition checked on the final state, with access to the initial
   state through <code>Old</code> nodes.

Cases outside the assumption or precondition are counted as excluded. Selecting
no cases is error <code>C006</code>, not a vacuous success. A professional
specification should similarly report which inputs were covered, excluded, or
left outside the model.

### Partial correctness does not promise termination

Partial correctness means: **if** a valid execution terminates, its final state
satisfies the postcondition. It does not say that termination occurs. Total
correctness adds termination.

For a loop

~~~text
while G:
    C
~~~

an invariant <code>I</code> supports the partial-correctness argument through
three obligations:

- **initialization:** <code>P</code> implies <code>I</code> before the first
  iteration;
- **preservation:** <code>I</code> and <code>G</code> before <code>C</code> imply
  <code>I</code> after <code>C</code>; and
- **exit:** <code>I</code> and not <code>G</code> imply <code>Q</code>.

An invariant is not merely a property observed after a run. It must be strong
enough to connect entry to exit and be preserved by every permitted body step.
The assertion <code>value >= goal</code> is useful for a countdown loop because
it holds initially, remains true after a guarded decrement, and combines with
<code>not goal < value</code> to establish <code>value = goal</code>.

To argue total correctness, add a **variant** into a well-founded set. Aster
uses integers and checks that the variant is nonnegative whenever the guard is
true and strictly decreases on every step. For countdown, the variant is
<code>value - goal</code>. Merely changing a variable is not enough: a loop that
increments <code>value - goal</code> violates the decrease obligation even if a
finite test harness eventually stops it at a resource cap.

Aster's partial mode omits variant obligations, but it still refuses to certify
an execution that exceeds the model's loop-step cap. Resource exhaustion is not
evidence of nontermination, and a bounded trace is not a general termination
proof.

### Counterexamples localize a failed obligation

When a checked obligation fails, Aster returns an immutable counterexample with
the phase, initial state, current state, step count, and stable detail. The
phases distinguish:

- invariant initialization;
- invariant preservation;
- variant nonnegativity;
- variant decrease;
- final postcondition;
- a stronger concrete precondition; and
- violation of a concrete or abstract postcondition during refinement.

A passing result retains the final state for every considered case. That trace
lets a separately derived oracle compare checker-produced observations rather
than manufacturing a second copy of its own expected values.

One counterexample disproves a universal claim. Passing finitely many examples
does not prove a universal claim unless those examples exhaust the declared
finite domain and the checker itself is trusted for that claim. Even then, the
result applies only to the encoded model, formulas, transition, arithmetic,
and bounds.

### Refinement preserves what clients may rely on

Suppose an abstract contract permits a set of starting states and a concrete
implementation replaces it. A simple behavioral refinement obligation is:

~~~text
abstract precondition  => concrete precondition
concrete postcondition => abstract postcondition
~~~

The concrete operation may accept more inputs, but must not demand more from an
abstract client. It may promise more, but every concrete result must still obey
the abstract promise. This is often summarized as "weaken preconditions and
strengthen postconditions," but the actual implication directions matter more
than the slogan.

Aster's <code>verify_refinement</code> checks every supplied case permitted by
the abstract assumption and precondition. It rejects a concrete assumption or
precondition that excludes such a case, executes the concrete loop, checks its
own postcondition, then checks the abstract postcondition on the same result.
This is bounded observational evidence. It does not establish contextual
refinement for arbitrary clients, traces, concurrency, exceptions, allocation,
or unmodeled effects.

### The executable model has explicit limits

Aster formulas include bounded integer and Boolean literals, current and old
state fields, addition, subtraction, comparisons, equality, conjunction,
disjunction, and negation. A state contains <code>value</code> and
<code>goal</code>. A loop plan has a Boolean guard, a constant update from -8
through 8, an invariant, and an optional integer variant.

The checker enforces:

- at most 63 nodes **per formula** and at most 12 nodes on a formula path;
- at most 16 explicitly supplied cases;
- at most 16 loop-body steps for any case;
- exact integer state, literal, and arithmetic results from -32 through 32; and
- only exact frozen Aster nodes, with cyclic host objects rejected.

Each boundary is constructible without first hitting another boundary. A
balanced conjunction of 32 Boolean leaves has exactly 63 nodes; one outer
<code>Not</code> is the smallest 64-node overflow. A chain with 12 total nodes
passes and its 13-node extension fails. Tuples of 16 and 17 states isolate the
case cap. Countdown from 16 takes exactly 16 steps; countdown from 17 requires
the smallest overflowing seventeenth step. Arithmetic can produce 32, while
<code>32 + 1</code> is the smallest positive overflow. A state field may be 32,
while 33 is rejected.

Formula checking is O(n) time and O(d) active traversal storage for at most 63
visits and depth 12. Verification is O(c x s x n) in the deliberately direct
implementation: at most 16 cases, 16 loop steps per case, and bounded formula
evaluation. Those are operation-count claims, not exact Python byte or timing
bounds. Python interpreter behavior, allocator metadata, stack representation,
and platform timing remain outside the model.

### Executable evidence has a trust boundary

The smoke checks positive cases, invalid forms, every endpoint and smallest
overflow, an independent arithmetic oracle for countdown, and an observed
wrong-expectation failure followed by a restored pass. It is evidence that the
checked implementation behaves that way in the declared host envelope.

It is not a proof that the Python interpreter is correct, that the model
matches an external system, that an omitted state is safe, or that a
mathematical rule holds outside the finite cases. It makes no Orange claim:
not Orange syntax, semantics, contracts, verifier soundness, compiler
correctness, refinement, security, or professional release behavior.

## Worked example

The supplied [Aster model](examples/contract_model.py) checks a countdown loop:

~~~text
assumption: 0 <= goal and value <= 16
pre:        goal <= value
invariant:  goal <= value and goal = old(goal)
guard:      goal < value
body:       value := value - 1
variant:    value - goal
post:       value = goal
~~~

It checks eight initial states with values 0 through 7 and goal 0. The abstract
postcondition only requires <code>value <= goal</code>; the concrete equality
therefore refines it without excluding an abstractly permitted case.

Run from the repository root:

~~~sh
cd curriculum/modules/frm-101
PYTHONDONTWRITEBYTECODE=1 python3 -B examples/contract_worked.py
PYTHONDONTWRITEBYTECODE=1 python3 -B checks/lab_smoke.py
~~~

The final command prints <code>frm-101 lab smoke: PASS</code> and exits zero.

## Check your understanding

1. Why is an environmental assumption not interchangeable with a caller
   precondition?
2. What does partial correctness say about an execution that never terminates?
3. Which three obligations make an invariant useful for a loop proof?
4. Why must a total-correctness variant be both bounded below and decreasing?
5. If a concrete precondition rejects one abstractly valid state, which
   refinement obligation failed?
6. Why can one counterexample refute a universal claim while sixteen passing
   cases usually cannot prove one?
7. What does Aster's 63-node endpoint say—and not say—about Python memory use?
8. Name two Orange properties this independent model does not establish.

## Next step

Complete the distinct lab and independent assessment. Preserve failing evidence
before correction. After passing, continue to <code>frm-102</code> to separate
proof scripts from the small trusted kernels that check proof objects.

## Sources

- C. A. R. Hoare, “An Axiomatic Basis for Computer Programming,”
  <cite>Communications of the ACM</cite> 12(10), 1969, DOI 10.1145/363235.363259.
- Edsger W. Dijkstra, “Guarded commands, non-determinacy and formal derivation
  of programs,” EWD472, 1975.
- Barbara Liskov and Jeannette Wing, “A Behavioral Notion of Subtyping,”
  <cite>ACM Transactions on Programming Languages and Systems</cite> 16(6),
  1994, DOI 10.1145/197320.197383.
- The executable [Aster contract model](examples/contract_model.py) and
  [portable smoke](checks/lab_smoke.py), fixed in this repository.
