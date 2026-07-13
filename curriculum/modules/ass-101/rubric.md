# Rubric: Northstar update dossier

## Rubric

This assessment is worth 100 points. Passing requires at least 80/100 and every
critical criterion. A high total cannot compensate for a false, unscoped, or
non-reproducible assurance conclusion.

## Critical criteria

- Every claim identifies its exact subject, version, scope, exclusions,
  assumptions, direct evidence, dependencies, and TCB; statuses are derived.
- Evidence identity is canonical, recomputed, independently checked, and
  changes when any included semantic field or result changes.
- Dependency closure detects unknown references, cycles, depth overflow, and
  missing inherited assumption or TCB inventory.
- Individually supported component claims do not support the integration claim
  without direct evidence that bears on their interaction.
- All exact endpoints and smallest overflows are independently isolated, and at
  least five deliberate failures are observed before restored passes.
- The report is offline-replayable, fail closed, and explicitly excludes
  unsupported proof, external-system, and Orange conclusions.

## Scoring

- **ASS-101-01 — scoped claim records (25):** 8 for exact subject, version,
  proposition, and scope; 6 for meaningful exclusions; 6 for owned,
  falsifiable assumptions; and 5 for immutable strict record validation.
- **ASS-101-02 — evidence and canonical identity (25):** 7 for accurate evidence
  classification and non-proofs; 8 for canonical content identity and an
  independent byte oracle; 5 for artifact, producer, method, assumption, fact,
  and TCB traceability; and 5 for tamper and adversarial cases.
- **ASS-101-03 — closure, TCB, and composition (25):** 8 for correct deterministic
  dependency traversal; 6 for cycle, unknown, and depth diagnostics; 6 for
  complete inherited assumption and TCB inventories; and 5 for direct
  integration evidence and a preserved non-composition failure.
- **ASS-101-04 — fail-closed reporting (25):** 7 for exact status derivation; 6
  for every isolated endpoint and smallest overflow; 6 for five recorded
  failure/restored-pass pairs and deterministic replay; and 6 for calibrated
  complexity, trust-boundary, non-proof, residual-risk, and Orange non-claim
  reporting.

The four categories total 100 points. A passing score is 80/100 or higher and
all critical criteria must pass.

## Feedback and retry

Feedback names the first invalid inference or unreproduced record, preserves its
exact evidence and status, and maps it to an outcome ID. The learner must not
overwrite the failing bundle before review.

A retry uses an assessor-supplied artifact digest and profile, changes the
evidence schema name, reduces at least two collection caps, swaps one
dependency edge, adds one false assumption and one syntactically valid identity
substitution, and requires a new direct integration method. The learner must
recompute identities, endpoints, closure, inventories, statuses, hashes, and
the final dossier. Prose edits cannot replace failed executable evidence.
