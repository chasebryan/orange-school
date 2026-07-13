# Rubric: security contract for a hostile relay

## Rubric

The assessment is worth exactly 100 points. Passing requires at least 80/100
and every critical criterion.

| Criterion | Points | Evidence required |
| --- | ---: | --- |
| Goals, attacker model, and security notions | 30 | Asset/lifetime/consequence definitions, capability and exclusion matrix, resource bounds, compromise variant, and two complete game-style notions with honest evidence limits |
| Trust boundaries and material contracts | 25 | Three precise crossings, four owned and falsifiable assumptions, and lifecycle-correct distinctions among secret keys, public identifiers, nonces, and security randomness |
| Composition and failure analysis | 20 | Traced dependencies from component premises to application claims, separate failure cases, containment/recovery actions, and residual harms |
| Bounded executable model and tests | 15 | Traceable zero-finding model, exact-bound and invalid tests, eight defect mutations, deterministic output, explicit limitation, and preserved failure sensitivity |
| Reproducibility, sources, and clarity | 10 | Environment and command record, separated stdout/stderr/status, evidence classification, readable identifiers, authoritative source trace, and no unsupported security claim |
| **Total** | **100** |  |

## Critical criteria

All four critical criteria must pass:

1. **Goal-and-game integrity:** earn at least 24/30. Every assessed notion must
   name an asset, attacker interface, challenge or forgery event, restrictions,
   exact win condition, bounds, assumptions, and evidence limitation. A vague
   “attacker cannot decrypt” claim, missing baseline for the confidentiality
   game, trivial winning query, or test presented as a quantified proof fails
   this criterion.
2. **Boundary-and-material integrity:** earn at least 20/25. Trust crossings
   must validate before release, assumptions must have owners and falsification
   signals, and key, identifier, nonce, entropy/random generation, and output
   contracts must remain distinct. Treating a public nonce as a secret key,
   random-looking output as evidence of unpredictability, or uniqueness without
   a key/concurrency/restart scope fails this criterion.
3. **Composition-and-failure integrity:** earn at least 16/20. Every application
   claim must carry its component, encoding, state, identity-binding, and
   operational premises. Nonce rollback, key exposure, parser disagreement,
   replay-state loss, error behavior, and relay deletion need distinct effects
   and responses. Claiming that a primitive automatically provides replay
   resistance, authorization, endpoint safety, or availability fails this
   criterion.
4. **Executable-evidence integrity:** earn at least 12/15. The model must be
   bounded, traceable, deterministic, zero-finding, and tested against the
   required defects, endpoints, outside-bound values, and strict types. It must
   print the evaluator limitation. A hard-coded report, missing mutation group,
   unpreserved failure-sensitivity run, or structural result described as a
   security approval fails this criterion.

A score of 80 or more cannot compensate for a failed critical criterion.

## Scoring

- **Goals, attacker, and notions (30):** 8 for asset-specific goals, leakage,
  lifetimes, and consequences; 7 for capability/resource/exclusion coverage and
  the one-instrument-compromise variant; 8 for the confidentiality experiment;
  and 7 for the integrity/freshness experiment and accurate evidence limits.
- **Trust and material (25):** 8 for three exact trust crossings and release
  order; 6 for four owned, falsifiable, linked assumptions; 8 for correct
  key/identifier/nonce/randomness lifecycles including concurrency, restart,
  and epoch change; and 3 for compromise and destruction/retention responses.
- **Composition and failure (20):** 8 for dependency tracing, 8 for the six
  required failure cases with containment and recovery, and 4 for residual
  harm and inside/outside-game classification.
- **Executable model and tests (15):** 5 for model completeness and prose/code
  traceability, 5 for defect mutations, 3 for exact and one-above bounds plus
  strict invalid inputs, and 2 for deterministic limitation-bearing evidence
  and a restored deliberate failure.
- **Reproducibility and clarity (10):** 4 for environment, directory, exact
  commands, channels, statuses, identities, and counts; 3 for accurate evidence
  categories and authoritative-source trace; and 3 for readable, internally
  consistent work without inflated claims.

Pass only with at least 80/100 and all critical criteria.

## Feedback and retry

Feedback identifies the first unsupported goal, missing attacker power,
ambiguous game rule, material-category error, broken dependency, or
failure-insensitive test; maps it to **CRY-101-01**, **CRY-101-02**, or
**CRY-101-03**; and names the evidence needed. Preserve the original submission
and append a correction record.

A retry uses an assessor-selected scenario with different assets, at least one
different trust topology, and a changed compromise event. Rewrite the affected
game and model rather than renaming fields. Rerun every affected mutation and
boundary test, including a fresh deliberate failure-sensitivity check. Revised
prose cannot replace missing executable evidence, and a clean structural report
cannot replace a missing security definition or composition argument.
