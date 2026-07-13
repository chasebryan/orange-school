# SAT, SMT, automation, and certificates

Automated reasoning separates two jobs. **Search** tries to find an answer;
**checking** validates evidence for a particular answer. Search may use complex
heuristics, parallel workers, learned clauses, or an external service. A
checker should accept only a precisely scoped witness or certificate under
explicit rules and bounds. A solver's success message is not itself proof
evidence.

This module's **Kindle** model is bounded Python 3.11 teaching courseware. It
implements deterministic search for small Boolean formulas in conjunctive
normal form (CNF) and independently checks model and refutation certificates.
It is not an Orange component, a production SAT or SMT solver, or evidence
that its own checker is sound.

## Learning objectives

- **FRM-103-01:** Distinguish automated search from independent result checking
  and interpret <code>sat</code>, <code>unsat</code>, and
  <code>unknown</code> without strengthening an unknown result.
- **FRM-103-02:** Validate bounded CNF inputs, SAT model witnesses, and UNSAT
  split-tree certificates with stable fail-closed diagnostics.
- **FRM-103-03:** Enforce explicit search and certificate bounds, then preserve
  deterministic endpoint, malformed-certificate, deliberate-failure, and
  restored-pass evidence.
- **FRM-103-04:** Inventory solver and checker trust, and state only the
  conditional claims supported by checked certificates.

## Prerequisites

Pass <code>frm-102</code> and <code>prg-102</code>. You should be able to
distinguish proof construction from kernel replay, track a certificate's
assumptions, implement bounded iteration and recursion, and test exact error
paths. The supplied courseware uses Python 3.11 or newer and only the standard
library. It runs offline and writes no generated files in the repository.

## Lesson

### A decision problem needs a complete contract

A Boolean variable has value false or true. A **literal** is either a positive
variable <code>x</code> or its negation <code>not x</code>. A **clause** is a
disjunction of literals; it is true when at least one literal is true. A CNF is
a conjunction of clauses; it is true only when every clause is true.

Kindle writes variables as positive integers. Literal <code>3</code> means
variable 3, and <code>-3</code> means its negation. For example:

~~~text
(1 or 2) and (-1 or 2)
~~~

is satisfied by <code>1=false, 2=true</code>. The course input record declares
the number of variables separately so a model has one unambiguous position for
every variable, including an unused one.

The admitted input envelope is:

- 1 through 6 declared variables;
- 1 through 32 clauses;
- 1 through 5 literals per clause; and
- exact non-Boolean integers for literals, excluding zero, whose absolute
  values do not exceed the declared variable count.

Tuples are required for the CNF and clauses. Repeated and complementary
literals retain their ordinary Boolean meaning; validation does not silently
normalize them. Unsupported host objects, Boolean values masquerading as
integers, empty clauses, out-of-range variables, and oversized structures are
rejected before search or certificate replay.

This is SAT-style reasoning because the theory is propositional Boolean
logic. SMT solvers add theory-specific meanings and checks for objects such as
integers, bit vectors, arrays, or floating-point values. The same professional
discipline still applies: state the theory, logic, encoding, options, resource
limits, and meaning of every returned status. A CNF example does not establish
that a theory solver or an encoding is correct.

### Search statuses have deliberately unequal meanings

Kindle's search producer may return exactly three lowercase statuses:

- <code>sat</code>: it found a candidate total model;
- <code>unsat</code>: it built a candidate exhaustive refutation tree; or
- <code>unknown</code>: its declared node or certificate-depth envelope ended
  before either conclusion was produced.

The first two become accepted claims only after their required certificates
check. <code>unknown</code> means neither satisfiability nor unsatisfiability was
established by that run. It does not mean “probably unsatisfiable,” “safe,” or
“no model exists.” Retrying with a different budget can be useful, but it does
not retroactively strengthen the earlier result.

Kindle uses a deterministic search-node budget rather than wall-clock time. A
node is one call that inspects one partial assignment. The cap is 63 nodes and
is checked before the next inspection. This makes the course endpoint portable
and reproducible. Production solvers may also have wall, CPU, memory, conflict,
or theory budgets. If an operating system kills a process at a wall timeout,
the absence of a result is not an <code>unsat</code> certificate. It is not even
a solver-produced <code>unknown</code> unless a valid result artifact explicitly
says so.

### SAT evidence is a model witness

A SAT certificate assigns one exact Boolean to every declared variable. The
independent model checker:

1. validates the CNF again;
2. requires an immutable model-certificate record;
3. requires exactly one Boolean position per declared variable; and
4. reevaluates every literal, clause, and conjunction.

Acceptance supports the narrow claim that this total assignment satisfies this
bounded CNF under Kindle's encoded Boolean semantics, conditional on the
checker and its trust base. It does not prove that an original program,
protocol, circuit, or requirements document was encoded faithfully. The model
is a useful counterexample when a CNF represents the negation of a desired
property, but only after the encoding direction is justified.

### UNSAT evidence must cover every assignment

Kindle's UNSAT certificate is a tree with two forms:

~~~text
RefutedClause(index)
Split(variable, when_false, when_true)
~~~

A leaf is valid only when the indexed CNF clause is false under assignments on
that branch. A split is valid only for an in-range variable not already split
on the branch. Its false and true children cover both possible values. A valid
tree rooted at the empty assignment therefore covers every assignment, while
each leaf exhibits one refuted clause.

The checker independently traverses the supplied tree. It does not call the
search procedure, trust a producer flag, or accept a leaf without reevaluating
the referenced clause. It admits at most 63 visited certificate nodes and
certificate depth 6, checking the node cap and then depth before inspecting
the next object. Object identities on the active recursion path are rejected
as cycles. A shared immutable subtree is allowed and counted again on every
visit because each branch is a separate coverage obligation.

An accepted root supports the narrow conditional claim that every assignment
to this bounded CNF reaches a falsified clause under the encoded split-tree
rules. It is not a proof that Kindle's rules are sound, that Python implements
them correctly, or that a source-level property outside the CNF holds.

### Fail closed at the status boundary

The producer returns a <code>SearchResult</code> containing status, certificate,
and visited-node count. The result checker applies a strict correspondence:

| Status | Required payload | Accepted claim |
| --- | --- | --- |
| <code>sat</code> | complete checked model | this model satisfies this CNF |
| <code>unsat</code> | complete checked split tree | every assignment is refuted |
| <code>unknown</code> | no certificate | no satisfiability conclusion |

An unknown result carrying a certificate is malformed. A SAT status carrying
an UNSAT tree, an UNSAT status carrying a model, a misspelled status, a Boolean
node count, or a count outside 1 through 63 is rejected. If the checker raises
an exception, crashes, or is not run, the workflow has no checked SAT or UNSAT
claim. This is the **fail-closed claim boundary**.

Separation is valuable even though both course components are in one Python
file: their algorithms and entry points are distinct, and forged producer
objects can be tested directly against the checker. It is not full
independence. The producer and checker still share data definitions, CNF
validation, Python semantics, repository provenance, and possibly the same
specification mistake.

### The endpoints are jointly reachable

Resource limits must describe a feasible system rather than independent round
numbers. Kindle's maximum-search witness uses five variables. For each of the
<code>2^5 = 32</code> assignments, it contains one five-literal clause that is
false only on that assignment. Their conjunction is unsatisfiable, and no
clause becomes false before all five variables are assigned.

The complete binary search tree has:

~~~text
1 + 2 + 4 + 8 + 16 + 32 = 2^6 - 1 = 63 nodes
~~~

Thus one input simultaneously reaches the 32-clause cap, five-literal cap,
63-search-node cap, 63-certificate-node cap, and depth-6 cap without crossing a
different limit. Declaring a sixth unused variable reaches the variable cap
without changing the proof. Budget 62 produces <code>unknown</code>; budget 63
produces a checkable <code>unsat</code> certificate.

A full binary tree has an odd number of nodes. Replacing its final leaf with a
split adds two nodes, so 65 is the smallest structurally representable count
beyond 63. The smoke suite places that split on variable 6 and observes the
node-count diagnostic before the new children are visited. A separate narrow
tree uses only 11 nodes at depth 6; a valid variable-6 split then attempts depth
7 and isolates the depth diagnostic without approaching 63 nodes.

Kindle will not split past five decision levels. If the sixth variable remains
necessary, it returns <code>unknown</code>. That limitation is intentional: a
sound incomplete procedure may decline to decide an admitted input. It may not
claim <code>unsat</code> merely because its certificate format ran out of room.

### Evidence strength follows the trust boundary

The trust inventory for a checked result includes at least:

1. the exact CNF and its encoding from the original problem;
2. the checker source actually executed and its Boolean semantics;
3. Python 3.11 record, integer, tuple, recursion, and equality behavior;
4. artifact selection, source identities, commands, channels, and statuses;
5. the operating system, runtime, and hardware insofar as faults alter the
   execution or evidence; and
6. the human argument connecting a checked bounded claim to any larger claim.

The search producer need not be trusted for an accepted model or tree when the
checker fully replays the evidence, although it remains relevant to
availability and reproducibility. A malicious producer can waste time or emit
malformed data; the checker must reject it. The checker, input encoding, and
claim mapping remain trusted.

Tests show that named cases behave as observed. Mutation shows that exercised
checks detect specific corruptions. Replay shows deterministic behavior for
the same artifacts. None proves checker soundness, completeness beyond the
bounds, absence of all defects, host correctness, constant-time behavior,
solver security, encoding fidelity, or any Orange property.

## Worked example

The [automation model](examples/automation_model.py) searches one satisfiable
CNF and checks its model, searches <code>(1) and (-1)</code> and checks its
three-node refutation, then reruns the contradiction with budget 1. The last
run returns <code>unknown</code> with no logical conclusion.

Run the narrative example and the full smoke evidence:

~~~sh
cd curriculum/modules/frm-103
PYTHONDONTWRITEBYTECODE=1 python3 -B examples/worked_automation.py
PYTHONDONTWRITEBYTECODE=1 python3 -B checks/lab_smoke.py
~~~

The final command prints <code>frm-103 lab smoke: PASS</code> and exits zero.
The smoke suite executes normal, endpoint, one-beyond, malformed, cyclic,
forged-status, deliberate-failure, and restored-pass cases in an offline
temporary-workspace-safe run.

## Check your understanding

1. Why is a solver's <code>sat</code> string weaker than a checked total model?
2. What exactly may be concluded from <code>unknown</code>?
3. How does a split tree cover all assignments without listing a complete
   assignment at every leaf?
4. Why must a refuted-clause leaf be reevaluated by the checker?
5. What is the difference between a deterministic node budget and an external
   wall-clock kill?
6. Why is 65, not 64, the smallest binary-tree overflow beyond 63 nodes?
7. Which trusted step connects a CNF theorem to a claim about a program?
8. Why does putting search and checking in separate functions reduce risk but
   not provide implementation independence?

## Next step

Complete the lab by implementing the distinct **Lantern** contract with your
own result and certificate structures. Then complete the independent **Signal**
assessment from a fresh workspace. Preserve malformed and forged results, the
exact failure diagnostic and immediate status, the restored pass, input and
source identities, and narrowly worded claims. After passing, continue to
<code>frm-104</code> to reason about randomized experiments, probability, game
hops, and reductions.

## Sources

- [Kindle bounded automation model](examples/automation_model.py) — normative
  executable semantics, search producer, and independent checker.
- [Worked SAT, UNSAT, and UNKNOWN run](examples/worked_automation.py) — concise
  narrative evidence.
- [Portable smoke suite](checks/lab_smoke.py) — endpoint, adversarial,
  deliberate-failure, and recovery evidence.
- [FRM-102 proof-kernel lesson](../frm-102/lesson.md) — prerequisite treatment
  of construction, replay, axioms, and checker trust.
