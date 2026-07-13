# Assessment: independent Tally quota contract

## Instructions

Complete this assessment independently in a fresh temporary directory using
Python 3.11 or newer and only the standard library. Do not copy, import, rename,
or lightly translate Aster, Boreal, their formulas, or their tests. Tally has a
distinct transition, state relation, formula surface, and resource envelope.

Submit <code>specification.md</code>, implementation, tests,
<code>evidence.md</code>, and <code>claims.md</code>. Preserve failing evidence
before corrections. Generated evidence must remain inside the temporary
workspace. Network access, external packages, repository changes, and
administrator permissions are prohibited.

## Knowledge check

Answer before implementation:

1. State the meaning of <code>{P} C {Q}</code> under partial correctness and
   identify what it does not promise. **FRM-101-02**
2. Classify each as environmental assumption, caller precondition, or operation
   postcondition: sensor readings are integral; requested quota is nonnegative;
   returned allocation does not exceed the request. **FRM-101-01**
3. Give initialization, preservation, and exit obligations for one proposed
   invariant. **FRM-101-02**
4. Explain why observing a decreasing quantity on five runs is not a general
   termination proof. **FRM-101-02**
5. Write the implication directions that prevent a concrete refinement from
   rejecting an abstract client or returning an abstractly forbidden result.
   **FRM-101-03**
6. Explain why a counterexample disproves a universal claim but a bounded pass
   needs an explicit scope. **FRM-101-01**
7. Distinguish a formula-node cap, formula-depth cap, case cap, and execution
   cap. **FRM-101-04**
8. List four Orange properties that cannot follow from an independent Python
   teaching model. **FRM-101-04**

## Independent task

Build **Tally**, a deterministic checker for an allocation loop over immutable
state <code>(granted, requested, quantum)</code>.

1. Define exact integer state fields from 0 through 60. The environmental
   assumption states that <code>quantum</code> is 3 or 5. The caller precondition
   states <code>granted <= requested</code>. The loop adds <code>quantum</code>
   while another full quantum would not exceed <code>requested</code>.
2. Define a relational postcondition that characterizes the final remainder:
   allocation does not exceed the request and fewer than one quantum remains.
   Preserve the initial request and quantum with explicit old-state references.
   **FRM-101-01**
3. Design immutable, sort-checked expression and predicate nodes unlike the lesson or
   lab models. Validate every formula before evaluation. Limit each formula to
   55 nodes and depth 11; reject exact host-type mismatches, cycles, unsupported
   fields, malformed children, and signed expression results outside -60
   through 60 with stable codes. State fields and loop updates remain separately
   restricted to 0 through 60. **FRM-101-01**, **FRM-101-04**
4. Implement partial checking with separately observable invariant
   initialization, preservation, and exit-postcondition failures. The invariant
   must be strong enough to preserve request, quantum, ordering, and reachability
   of <code>granted</code> from its old value by whole quanta. **FRM-101-02**
5. Implement total checking with an integer variant derived from remaining
   capacity. Check its lower bound and strict decrease under the actual quantum
   step. Include a deliberately wrong variant that is negative while the guard
   is true and assert the dedicated lower-bound counterexample before any
   state-range failure. Reject total mode without a variant. **FRM-101-02**
6. Check at most 15 submitted cases and 18 loop steps per case. Reject before
   retaining case 16 or executing step 19. Reject a zero-case proof after
   assumption and precondition filtering. Return immutable results and
   counterexamples. **FRM-101-01**, **FRM-101-04**
7. Define an abstract allocator whose precondition permits all nonnegative
   requests and whose postcondition only promises
   <code>granted <= requested</code>. Check that Tally does not strengthen that
   precondition over the submitted domain and that every concrete result
   satisfies the abstract postcondition. Preserve a failing run in which the
   concrete precondition is strengthened to <code>granted < requested</code>.
   **FRM-101-03**
8. Submit positive, endpoint, and invalid tests for each formula kind and each
   obligation. Independently isolate 55 and the smallest constructible 56
   formula nodes; depths 11 and 12; 15 and 16 cases; 18 and 19 loop steps;
   signed arithmetic -60/60 and -61/61; and state fields 60 and 61.
   **FRM-101-04**
9. For at least 12 fixed valid cases spanning both quanta, compare the checker
   with a separately implemented closed-form quotient/remainder oracle. The
   oracle may share immutable input records but no validation, evaluation,
   transition, or verification helper. **FRM-101-04**
10. Preserve four deliberate-failure/restored-pass pairs: one final allocation,
    one invariant failure phase, one refinement precondition, and the 18-step
    endpoint. Record exact commands, stdout, stderr, and immediate status.
    **FRM-101-04**
11. State time and storage bounds in terms of the declared caps. Separate model
    facts, checker evidence, mathematical arguments, host assumptions, and
    residual risk. State explicitly that the work establishes no Orange
    language, contract, proof, refinement, compilation, safety, security, or
    conformance claim. **FRM-101-04**

## Completion criteria

Submit all required artifacts and earn at least 80/100 under
<code>rubric.md</code>. All critical criteria must pass. The assessment must run
offline from a fresh temporary directory on Python 3.11 or newer, and every
claimed endpoint, counterexample, refinement condition, oracle comparison, and
deliberate failure must be reproducible from the recorded commands.
