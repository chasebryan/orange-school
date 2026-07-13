# Lab: classify the school and build your path

## Goal

Create a small status-and-evidence worksheet, then use it to choose the first
assessment on your personal path. This is guided practice; your independent
assessment will use different cases.

## Setup

Open the [curriculum catalog](../../catalog.json) and
[current status page](../../../docs/current-status.md) in a browser or text
editor. Make a blank document or use paper. Do not edit the catalog.

Copy these worksheet labels:

| Item | Classification | Exact evidence or reason | Claim boundary |
| --- | --- | --- | --- |
| 1 |  |  |  |

Also make an assessment ledger:

| Module | Prerequisites passed? | Assessment result | Evidence location |
| --- | --- | --- | --- |
| <code>ori-001</code> | Yes; it has none | Pending | This lab is not pass evidence |

## Tasks

1. **Read status without guessing.** Find one catalog module marked
   <code>released</code>, one marked <code>planned</code>, and one marked
   <code>blocked</code>. Add each module ID, title, exact status, and the
   appropriate learner action to your worksheet.
2. **Classify evidence.** Add these four cards to the worksheet:
   - “The checker exited 0 for file A with tool revision R.”
   - “Conclusion Q follows from premises P1 and P2 using the listed rules.”
   - “This argument relies on the operating system reporting file contents
     faithfully.”
   - “A later Orange edition should add package signing.”
   Label each as test, proof, assumption, or proposal. For every card, write one
   thing it does not establish.
3. **Repair an overclaim.** Rewrite “The checker accepted one file, so all
   Orange programs are correct.” Include the procedure, input, observed result,
   revision placeholder, narrow conclusion, and at least two exclusions.
4. **Build your ledger.** In catalog order, add released modules whose
   prerequisites form a path from <code>ori-001</code>. Mark prior assessments
   passed only if you have a real score record. Use “not passed,” “not
   attempted,” or “pending” otherwise.
5. **Choose the start.** Circle the earliest row without passing assessment
   evidence. Write “My path begins at ___ because ___.” Continue with later
   released modules in prerequisite order, and record where a planned or
   blocked prerequisite makes completion unavailable.

## Verification

Check your worksheet against this list:

- Each status came from the catalog rather than from the module title.
- Released means available material; planned means incomplete material;
  blocked means release is forbidden by an unresolved dependency.
- The command observation is a test, the derivation is a proof, the relied-on
  statement is an assumption, and the future design request is a proposal.
- Your repaired claim does not turn acceptance of one file into correctness,
  compilation, execution, verification, or a claim about every file.
- Every “passed” ledger row names assessment evidence.
- The first path step is the earliest row without pass evidence, and every
  later step respects prerequisites.

If any check fails, correct the worksheet and note what changed.

## Reflection

In three to five sentences, answer:

- Which label were you most tempted to strengthen, and why?
- What evidence would be needed before your earliest unpassed module could be
  marked passed?
- How will you record a planned or blocked boundary without treating it as your
  own failure?
