# Rubric: Tally quota contract

## Rubric

This is a 100-point assessment. A passing score is at least 80/100 and all
critical criteria below must pass. A high aggregate score cannot compensate for
a missing or false critical obligation.

## Critical criteria

- Assumptions, caller preconditions, relational postconditions, and old-state
  references are explicit and are not silently interchanged.
- Partial correctness checks invariant initialization, preservation, and the
  exit postcondition; total correctness additionally checks a nonnegative,
  strictly decreasing variant.
- Refinement rejects a stronger concrete input requirement and checks every
  concrete result against the abstract postcondition.
- Every exact resource endpoint and smallest constructible overflow is
  independently executable and asserted at the declared boundary.
- Counterexamples retain the obligation phase and concrete witness; at least
  four deliberate failures are observed before their restored passes.
- Evidence is offline and reproducible, and claims explicitly exclude Orange
  properties and unsupported proof or host guarantees.

## Scoring

- **FRM-101-01 — specifications and counterexamples (25):** 8 for distinct
  assumptions, preconditions, postconditions, and old-state relations; 7 for
  exact immutable formula/state validation; 6 for stable structured witnesses;
  and 4 for exclusion accounting and non-vacuity.
- **FRM-101-02 — partial and total correctness (30):** 8 for initialization,
  preservation, and exit reasoning; 8 for correct executable checks; 8 for a
  well-founded variant with lower-bound and decrease failures; and 6 for clear
  partial-versus-total claims.
- **FRM-101-03 — refinement (20):** 7 for the abstract/concrete contracts; 7 for
  no-stronger-precondition and abstract-postcondition checks; and 6 for a
  preserved, precise refinement counterexample.
- **FRM-101-04 — bounded evidence and calibration (25):** 8 for independently
  isolated exact endpoints and smallest overflows; 5 for an independent oracle;
  5 for four observed failure/restored-pass pairs; 4 for commands, channels,
  statuses, versions, paths, and hashes; and 3 for accurate complexity,
  trust-boundary, and Orange non-claims.

The four categories sum to 100 points. Passing requires 80/100 or higher and
every critical criterion.

## Feedback and retry

Feedback names the first failed obligation or unsupported claim and maps it to
an outcome ID. Preserve the original submission, counterexample, and command
evidence before changing it.

A retry uses assessor-selected bounds, swaps the permitted quanta to 4 and 7,
changes at least three initial states, and introduces one malformed cyclic
formula. The learner must recompute the invariant, variant, postcondition,
closed-form oracle, exact endpoints, and refinement witness. Prose-only changes
cannot replace failed executable evidence.
