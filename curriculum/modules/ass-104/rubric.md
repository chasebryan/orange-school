# Rubric: Beacon release correction and response audit

## Rubric

The assessment is worth 100 points. Passing requires at least 80/100 and every
critical criterion.

| Criterion | Points | Evidence required |
| --- | ---: | --- |
| Release lifecycle and support integrity | 25 | Exact identities, compatibility directions, support window, migration, update selection, rollback floor, retirement, withdrawal, revocation, and decision table |
| Vulnerability response and communication | 30 | Bounded intake, triage and uncertainty, claim suspension, containment, advisory, update/withdrawal paths, downstream evidence ladder, and remedy-specific closure |
| Executable boundaries and recovery evidence | 25 | Independent exact-type model, feasible endpoints and one-beyond isolation, stable diagnostics, preserved failures/restoration, canonical replay, and recovery drill |
| Trust, reproducibility, and claim calibration | 20 | Source and evidence identities, commands/channels/statuses, trust inventory, external-action distinctions, limitations, and explicit non-claims |
| **Total** | **100** |  |

## Critical criteria

All four critical criteria must pass:

1. **Lifecycle-policy integrity:** earn at least 20/25. Artifact and source
   identities, supported channels and platforms, compatibility direction,
   support start/end, migration, rollback prevention, retirement, withdrawal,
   and revocation must be unambiguous and mutually consistent. Availability
   must not imply support or safety.
2. **Response integrity:** earn at least 24/30. Input is bounded before
   retention; triage preserves uncertainty; disputed claims are suspended
   before containment; containment, advisory, update or withdrawal,
   notification, and closure remain distinct; and both remedy paths enforce
   their required evidence. Skipping a transition or strengthening a
   notification reference fails this criterion.
3. **Failure-sensitive implementation:** earn at least 20/25. The independent
   state machine validates complete exact-type records, reaches all joint caps,
   isolates every one-beyond attempt, rejects invariant violations with stable
   diagnostics, preserves eight deliberate failures and restorations, renders
   canonical bytes, and completes the bounded recovery drill. An unreachable
   endpoint or rollback acceptance fails this criterion.
4. **Claim-boundary integrity:** earn at least 16/20. Evidence distinguishes
   definitions, local records, attempted external actions, verified external
   results, and unsupported claims. The trust inventory and replay artifacts
   are complete, and conclusions exclude real publication, delivery,
   revocation, vulnerability validity, update-system security, legal or
   service compliance, production readiness, and Orange claims.

A total of 80/100 or more cannot compensate for a failed critical criterion.

## Scoring

- **Release lifecycle and support integrity (25):** 6 for exact artifact,
  source, build, channel, owner, claim, and constituency identity; 6 for
  compatibility directions, platforms, dependencies, support windows, and
  response targets; 7 for migration, update selection, rollback prevention,
  and archive behavior; and 6 for retirement, withdrawal, revocation, and the
  complete policy decision table.
- **Vulnerability response and communication (30):** 6 for bounded hostile
  intake, identities, duplicates, permissions, and deadlines; 6 for
  reproduction, affected-version analysis, uncertainty, severity, escalation,
  and claim suspension; 7 for ordered containment, advisory, update, migration,
  withdrawal, and residual risk; 6 for downstream constituency and the full
  preparation-to-remediation evidence ladder; and 5 for remedy-specific
  closure and timeline quality.
- **Executable boundaries and recovery evidence (25):** 7 for independent
  immutable records, full validation, deterministic transitions, and stable
  diagnostics; 6 for jointly feasible exact endpoints and isolated
  one-beyond cases; 6 for adversarial types, illegal transitions, and eight
  preserved failure/restoration pairs; and 6 for canonical bytes, digest,
  corrupted-record rejection, rollback test, and recovery replay.
- **Trust, reproducibility, and claim calibration (20):** 7 for source,
  artifact, runtime, command, directory, stdout, stderr, status, and digest
  identities; 5 for a complete implementation and external-action trust
  inventory; 4 for classifying evidence strength without strengthening
  references into delivery or truth; and 4 for explicit limitations and
  Orange non-claims.

The categories sum to 100 points. Passing requires 80/100 or higher and all
critical minima.

## Feedback and retry

Feedback names the first ambiguous release identity, support promise,
compatibility direction, missing report bound, unsupported severity inference,
unsuspended claim, skipped transition, incomplete advisory, missing downstream,
rollback path, infeasible endpoint, unstable diagnostic, absent immediate
status, noncanonical record, incomplete recovery step, or overstated claim and
maps it to **ASS-104-01**, **ASS-104-02**, **ASS-104-03**, or **ASS-104-04**.
Preserve the original artifact and evidence before appending a correction.

A retry changes the starting revision and support window, assigns a different
compatibility direction, injects one duplicate report and one upstream
dependency advisory, requires a two-stage migration, changes one downstream
mid-incident, selects the opposite update-or-withdrawal remedy, and supplies a
different malformed record and rollback attempt. Recompute the policy,
transition path, advisory, downstream ledger, endpoints, canonical record,
recovery drill, and claim audit. Rewording an unsupported claim or copying the
first evidence package is not a successful retry.
