# Assessment: independent Signal automation audit

## Instructions

Complete this assessment independently in a fresh temporary directory using
Python 3.11 or newer and only the standard library. Do not import, copy, rename,
or lightly translate Kindle or a Lantern solution. Submit the logic contract,
input format, producer, independent checker, tests, worked candidates,
<code>trust.md</code>, and <code>evidence.md</code>. Everything must run offline;
generated files remain beneath the temporary workspace.

The assessment covers:

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

Signal uses its own representation and code. It admits at most five numbered
Boolean variables, 16 clauses, four literals per clause, 31 producer visits,
31 certificate nodes, and certificate depth 5. It uses a zero-based model tuple
but one-based variable names in written formulas. State and test that mapping.

## Knowledge check

1. Define a literal, clause, CNF, partial assignment, total model, candidate,
   certificate, producer, checker, decision procedure, and incomplete
   procedure without using them interchangeably.
2. Give the exact logical meaning of SAT, UNSAT, and UNKNOWN. Why are timeout,
   crash, and missing output not automatically UNKNOWN?
3. Explain how a total model certifies SAT and how one false clause at every
   leaf of a complete split tree certifies UNSAT.
4. Why must a checker reevaluate leaves and model clauses instead of trusting a
   producer's annotations?
5. Contrast SAT with SMT. Which extra contract must be stated for integer or
   bit-vector constraints?
6. Explain fail-closed status/payload dispatch. What should happen if checking
   raises, crashes, or exceeds its own resource envelope?
7. Give the node count of a complete decision tree for four variables and the
   smallest larger full-binary-tree node count.
8. Inventory the trusted components between a checked CNF result and a claim
   about source code. Which one is not exercised by CNF replay?

## Independent task

1. **Logic and status contract — FRM-103-01.** Write
   <code>signal-contract.md</code>. Define Signal's CNF grammar, declared
   variables, tuple order, clause evaluation, input caps, search order, counted
   work, and exact status meanings. State the check performed before every next
   input retention, search visit, certificate visit, and descent.
2. **Strict input validation — FRM-103-02.** Build immutable input structures.
   Reject Boolean literals, zero, out-of-range variables, foreign iterables,
   empty and oversized clauses, missing clauses, and every cap plus one with
   stable structured diagnostics. Do not silently truncate, deduplicate,
   normalize, or consume an unbounded iterable.
3. **Candidate producer — FRM-103-01 and FRM-103-03.** Implement deterministic
   bounded search with one visit per inspected partial assignment. Choose the
   lowest unassigned variable and false before true. Stop with UNKNOWN before a
   32nd visit or a certificate deeper than 5. Return no certificate with
   UNKNOWN. Record visited nodes without using wall time as a logical result.
4. **Independent SAT checking — FRM-103-02.** Use a distinct entry point that
   validates input again and checks every Boolean in a five-position-or-shorter
   model tuple against every clause. It must not invoke search or accept a
   partial model. Preserve the satisfying tuple as a reviewable witness.
5. **Independent UNSAT checking — FRM-103-02.** Design your own immutable leaf
   and branch records. Require a valid falsified-clause reference at every leaf,
   both Boolean branches at every internal node, an in-range variable not
   repeated on its path, no active recursion cycle, at most 31 visits, and
   depth at most 5. The checker must reconstruct branch assignments itself.
6. **Status boundary — FRM-103-01 and FRM-103-04.** Implement one fail-closed
   dispatcher. Directly test genuine and forged SAT, UNSAT, and UNKNOWN result
   records, payload swaps, an UNKNOWN payload, missing payloads, an unsupported
   status, and false or out-of-range node counts. A producer exception or
   checker rejection supplies no accepted decision.
7. **Joint boundary proof — FRM-103-03.** Generate the 16 clauses that each
   exclude one assignment to variables 1 through 4. Declare variable 5 but
   leave it unused. Demonstrate exactly 31 search visits and 31 certificate
   visits at depth 5. Demonstrate UNKNOWN at budget 30 and checked UNSAT at 31.
   Construct the smallest full-binary-tree overflow while isolating the node
   diagnostic, then use a narrow certificate to isolate depth 6.
8. **Malformed and adversarial evidence — FRM-103-03.** Test every validator
   diagnostic plus foreign certificate objects, Boolean clause indexes, a leaf
   not falsified on its branch, missing children, out-of-range and repeated
   split variables, a cycle created by bypassing immutability, shared-subtree
   recounting, incomplete and non-Boolean models, and every exact endpoint and
   next attempt. Assert exact code/message pairs.
9. **Deliberate failure and restoration — FRM-103-03.** Preserve at least five
   authentic checks. Independently corrupt a status, model bit, leaf index,
   split variable, and budget. For each, preserve separate stdout/stderr and the
   immediate nonzero status, restore only that item, rerun, and preserve the
   immediate zero status. Explain which checker obligation detected the fault.
10. **Trust and non-proofs — FRM-103-04.** Inventory exact source and input
    identities, the CNF encoding, Python semantics, checker, artifact loader,
    commands, runtime, operating system, hardware, and external claim mapping.
    Separate producer availability from certificate correctness. Explain
    shared implementation/specification risk. Explicitly reject solver and
    checker soundness proofs, completeness outside caps, encoding fidelity,
    constant-time or security claims, external-solver validation, and every
    Orange semantic, compiler, or professional-readiness claim.
11. **Evidence record.** Preserve Python version, absolute workspace, SHA-256
    identities, commands, separate channels, immediate statuses, deterministic
    replay, endpoint arithmetic, candidate and checked statuses, certificate
    sizes/depths, all failure/restoration pairs, and one narrow conditional
    sentence for each accepted SAT and UNSAT result.

## Completion criteria

Use the [rubric](rubric.md). Passing requires at least 80/100 and every critical
criterion. A passing submission must:

- satisfy **FRM-103-01** with exact, non-interchangeable status semantics and a
  real producer/checker separation;
- satisfy **FRM-103-02** with strict input handling, complete model replay,
  exhaustive split-tree replay, stable diagnostics, and fail-closed dispatch;
- satisfy **FRM-103-03** with jointly feasible exact and next endpoints,
  adversarial objects, and preserved deliberate failures and restorations;
- satisfy **FRM-103-04** with an accurate trust inventory and conclusions no
  stronger than the checked bounded CNF evidence; and
- run offline under Python 3.11 or newer without an external solver or Orange
  dependency.

UNKNOWN called UNSAT, a status trusted without its certificate, a partial model,
an unchecked leaf, a missing Boolean branch, an unreachable endpoint, a
certificate check that calls search, an unrecorded failure status, or a claim
about an external encoding, production solver, security property, or Orange
cannot pass.
