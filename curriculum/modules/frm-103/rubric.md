# Rubric: Signal automation and certificate boundary

## Rubric

This is a 100-point assessment. Passing requires at least 80/100 and every
critical criterion below. A high total cannot compensate for a false status,
unchecked certificate, infeasible endpoint, or unsupported claim.

## Critical criteria

- SAT, UNSAT, and UNKNOWN have exact meanings; UNKNOWN is never strengthened,
  and every accepted SAT or UNSAT status has the matching independently checked
  certificate.
- CNF input, total models, refuted-clause leaves, exhaustive split branches,
  statuses, and counts are validated strictly with stable fail-closed
  diagnostics; the checker does not call search.
- The 31-node and depth-5 endpoints are jointly executable, budget 30 produces
  UNKNOWN, the smallest structural node overflow and depth 6 are isolated, and
  malformed or cyclic certificates cannot pass.
- At least five authentic artifacts are deliberately corrupted, each immediate
  failure is preserved, and each restored artifact independently passes.
- Trust and evidence distinguish search, checking, encoding, replay, tests,
  host assumptions, and external claim mapping; no unsupported proof, solver,
  security, host, or Orange claim is made.

## Scoring

- **FRM-103-01 — search and status semantics (20):** 6 for the complete logic
  and search contract; 6 for exact SAT/UNSAT/UNKNOWN meanings and timeout/crash
  distinctions; 5 for deterministic bounded production; and 3 for clear
  producer-versus-checker separation.
- **FRM-103-02 — certificate checking (30):** 7 for strict immutable input and
  model validation; 9 for exhaustive independent UNSAT tree replay; 8 for
  fail-closed status/payload dispatch and stable diagnostics; and 6 for forged,
  malformed, incomplete, foreign, shared, and cyclic evidence.
- **FRM-103-03 — bounds and falsifiable evidence (30):** 10 for jointly feasible
  exact input/search/certificate/depth endpoints and shown arithmetic; 6 for
  isolated node and depth overflows; 8 for boundary, relational, and
  adversarial tests; and 6 for five preserved deliberate-failure/restored-pass
  pairs with immediate statuses.
- **FRM-103-04 — trust and calibrated claims (20):** 7 for a complete trust-base
  and artifact inventory; 5 for exact commands, identities, channels, statuses,
  and deterministic replay; 4 for producer/checker common-mode analysis; and 4
  for narrow conditional claims and explicit non-proofs.

The four categories sum to 100 points. Passing requires 80/100 or higher and
every critical criterion.

## Feedback and retry

Feedback names the first unsound status, unchecked branch, masked endpoint, or
unsupported claim and maps it to an outcome ID. Preserve the original artifact,
diagnostic, channels, and immediate status before making changes.

A retry uses assessor-selected variable order, truth-value order, two new SAT
formulas, two new UNSAT formulas, and budgets 17 and 29. The assessor injects
one forged status/payload pair, one refuted-clause mutation, one repeated branch
variable, one active cycle, and one Boolean value in an integer field. The
learner must recompute witnesses, certificates, endpoint reasoning, trust
inventory, and failure/restoration evidence. Prose-only changes cannot replace
failed executable evidence.
