# Lab: verify the Boreal bounded counter

## Goal

Specify and independently implement a finite contract checker for a bounded
counter operation. Demonstrate assumptions, preconditions, postconditions,
partial and total loop obligations, counterexamples, and behavioral refinement
without importing or translating Aster.

## Setup

First inspect the reference model's behavior:

~~~sh
cd curriculum/modules/frm-101
python3 --version
PYTHONDONTWRITEBYTECODE=1 python3 -B examples/contract_worked.py
PYTHONDONTWRITEBYTECODE=1 python3 -B checks/lab_smoke.py
~~~

Use Python 3.11 or newer and only the standard library. Create learner work in
a fresh temporary directory. Do not import, copy, rename, or mechanically
translate Aster. Boreal uses different state, formulas, operations, and bounds.

~~~sh
workdir="$(mktemp -d)"
cd -- "$workdir"
pwd
~~~

Run with <code>PYTHONDONTWRITEBYTECODE=1</code> and <code>python3 -B</code>. No
network, package installation, administrator permission, or repository write is
required.

## Tasks

1. **Define Boreal's scope — FRM-101-01.** Model an immutable state with
   <code>stock</code> and <code>reserve</code>, exact integers from -48 through
   48. Define separate immutable integer and Boolean formula nodes for current
   fields, entry fields, literals, addition, subtraction, equality, ordering,
   conjunction, implication, and negation. Accept only exact supported nodes.
2. **Separate assumptions and obligations — FRM-101-01.** A contract contains
   an environmental assumption, caller precondition, and relational
   postcondition. Count assumed/precondition-valid cases separately from
   exclusions and reject a selection of zero. Explain who owes each predicate.
3. **Implement bounded formula validation — FRM-101-04.** Limit each formula to
   47 nodes and depth 10. Reject before visiting node 48 or descending to depth
   11. Reject cycles, host Booleans in integer positions, unsupported objects,
   unknown state fields, sort errors, and arithmetic outside -48 through 48
   with stable codes.
4. **Specify the loop — FRM-101-02.** Verify a restocking loop that increments
   <code>stock</code> by 2 while <code>stock + 1 < reserve</code>. State the exact
   parity-sensitive postcondition. Supply an invariant relating current stock,
   old stock, reserve, ordering, and parity, plus a nonnegative decreasing
   variant. Explain why <code>stock = reserve</code> is the wrong general post.
5. **Check partial correctness — FRM-101-02.** Check invariant initialization,
   preservation after every body step, and the postcondition on exit. In
   partial mode, do not silently claim termination. Refuse to certify any trace
   that reaches the explicit loop cap.
6. **Check total correctness — FRM-101-02.** Require an integer variant in total
   mode. Check nonnegativity whenever the guard is true and strict decrease
   after each step. Give separate counterexamples for a negative variant and a
   nondecreasing variant.
7. **Return structured counterexamples — FRM-101-01.** Include obligation
   phase, initial state, current state, step, and stable detail. Demonstrate
   failures for invariant initialization, invariant preservation, the exit
   postcondition, variant decrease, and a deliberately too-strong assumption.
8. **Check behavioral refinement — FRM-101-03.** Define an abstract operation
   that permits every state satisfying <code>stock <= reserve</code> and
   promises <code>stock <= reserve + 1</code>. Show the concrete operation
   accepts every abstractly permitted submitted case and its final state obeys
   both concrete and abstract postconditions. Then strengthen the concrete
   precondition by one and preserve the resulting counterexample.
9. **Make every bound independently testable — FRM-101-04.** Use a 47-node
   balanced formula and its smallest constructible 48-node extension; depth 10
   and 11; 12 and 13 submitted cases; 14 and 15 loop steps; arithmetic results
   48 and 49; and state fields 48 and 49. Construct each pair so another cap
   cannot mask it.
10. **Add an independent oracle — FRM-101-04.** For all 12 submitted valid
    cases, calculate the final stock and iteration count with a closed-form
    arithmetic function that imports no checker or transition helper. Compare
    exact tuples, not only aggregate counts. State the oracle's overlap.
11. **Prove failure sensitivity — FRM-101-04.** Mutate three expectations one
    at a time: one final stock, one invariant phase, and the exact loop endpoint.
    Preserve separate stdout, stderr, and immediate nonzero status. Restore
    each value and preserve status zero.
12. **Record evidence and non-claims.** In <code>evidence.md</code>, record the
    Python version, absolute temporary path, file hashes, exact commands,
    separate channels, and immediate statuses. Give bounded operation-count
    arguments without claiming exact Python memory or time. State that Boreal
    proves no Orange syntax, contract, verifier, refinement, safety, security,
    or conformance property.

## Verification

Run the complete learner suite from the temporary directory:

~~~sh
PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest -v \
  >passing.stdout 2>passing.stderr
status=$?
printf 'test status: %s\n' "$status"
~~~

Status zero is necessary but not sufficient. Inspect the submission and verify:

- assumptions, preconditions, and postconditions have distinct meanings and
  selection counts;
- old-state references remain fixed across every iteration;
- initialization, preservation, exit, variant lower bound, and variant decrease
  have separate checks and failure phases;
- concrete inputs are not narrower than abstract inputs;
- every exact endpoint and smallest overflow is reached independently;
- the oracle shares no formula evaluator, transition, or checker path;
- all deliberate mutations fail and all restored expectations pass;
- generated files stay beneath the temporary workspace; and
- every conclusion is limited to Boreal's submitted finite domain.

Finally rerun the reference smoke from its repository directory as separate
evidence that learner work did not change it.

## Reflection

Write six to eight sentences answering:

- Which fact belongs in Boreal's assumption rather than its precondition?
- Why does parity matter to the concrete postcondition?
- What property is preserved but insufficient to imply the postcondition?
- What extra obligation turns the partial check into the total check?
- Which case witnesses the stronger-precondition refinement failure?
- Which endpoint was hardest to isolate from another bound?
- What implementation defect can the independent oracle detect?
- Why does the result establish no property of Orange?
