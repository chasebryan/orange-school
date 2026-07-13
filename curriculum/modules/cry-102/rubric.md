# Rubric: fail-closed symmetric-protocol review

## Rubric

The assessment is worth exactly 100 points.

| Criterion | Outcomes | Points | Evidence required |
| --- | --- | ---: | --- |
| Service and value distinctions | CRY-102-01 | 20 | Correct claims map, primitive contracts, value semantics, wrong-substitution analysis, and knowledge answers |
| Nonce, AEAD, composition, and failure analysis | CRY-102-02 | 30 | Durable nonce/replay state, canonical AAD, distinct domains and keys, complete unsafe-design audit, and fail-before-plaintext pseudocode |
| Bounded executable mechanics | CRY-102-03 | 20 | SHA-256, HMAC-SHA-256, and PBKDF2-HMAC-SHA-256 wrappers; public vectors; endpoint, invalid, tamper, and deliberate-failure tests; honest limits |
| Manifest, approval boundary, and handoff | CRY-102-04 | 20 | Metadata-only schema, deterministic linter and mutations, primary-source map, profile/library distinctions, and owner/stop-condition handoff |
| Reproducibility and clarity | All | 10 | Fresh workspace, exact environment and commands, stdout/stderr/statuses, source identities, public-data record, readable artifacts, and evidence limitations |
| **Total** |  | **100** |  |

## Critical criteria

All four critical criteria must pass:

1. **Service-boundary integrity:** earn at least 16/20 for service and value
   distinctions. Hash, MAC, password KDF, general KDF, symmetric encryption,
   and AEAD must have correct and non-interchangeable claims. Calling an
   unkeyed digest authentic, a nonce secret, HKDF a password hasher, or a MAC a
   signature among key holders fails this criterion.
2. **Authenticated-opening and state integrity:** earn at least 24/30 for nonce,
   AEAD, composition, and failure analysis. The design must prevent same-key
   nonce reuse across concurrency and rollback, bind canonical versioned AAD,
   keep keys and domains purpose-separated, release no plaintext before tag
   success, reject legacy fallback, and handle replay in authenticated durable
   state. Any missing one of these requirements fails this criterion.
3. **Executable-evidence integrity:** earn at least 16/20 for bounded mechanics.
   Every required normal, exact-endpoint, invalid, modification, and deliberate
   failure test must run; HMAC verification must use `compare_digest`; inputs
   must be public and bounded; and no cipher, mode, AEAD, or HKDF may be
   implemented. Printing sensitive inputs or presenting the lab PBKDF2 interval
   as a production profile fails this criterion.
4. **Decision-provenance integrity:** earn at least 16/20 for manifest,
   approval boundary, and handoff. The linter must reject every required unsafe
   mutation and embedded-secret field; the submission must distinguish a
   standard, fictional scenario profile, production authority, library
   evidence, and operations; and every unresolved deployment decision must have
   an owner and stop condition. Treating a recognized name or linter pass as
   production approval fails this criterion.

A total of 80/100 or more cannot compensate for a failed critical criterion.

## Scoring

- **Service and value distinctions (20):** 8 points for complete claim and
  attacker mapping, 6 for accurate input/output/value semantics, 4 for
  wrong-substitution explanations, and 2 for precise limitations.
- **Nonce, AEAD, composition, and failure analysis (30):** 8 points for the
  concurrent durable nonce state and capacity, 6 for canonical AAD and replay
  state, 8 for finding and correcting every unsafe composition defect, 5 for
  domain/key separation, and 3 for safe error and evidence handling.
- **Bounded executable mechanics (20):** 6 points for exact contracts and API
  use, 6 for public vectors and normal/endpoint coverage, 5 for invalid/tamper
  and deliberate-failure sensitivity, and 3 for accurate non-production and
  side-channel limitations.
- **Manifest, approval boundary, and handoff (20):** 6 points for a complete
  metadata-only schema, 6 for deterministic validation of every required
  mutation, 4 for primary-source and authority/profile/library separation, and
  4 for assigned handoff evidence and stop conditions.
- **Reproducibility and clarity (10):** 5 points for exact environment,
  workspace, commands, channels, statuses, and restoration record; 3 for
  readable traceable artifacts; and 2 for public-data provenance and truthful
  evidence limits.

Award no points twice for the same evidence. A test result can support code
behavior but cannot replace the state-machine argument, approval record, or
production handoff. A prose claim cannot replace a required executable failure.

Pass only with at least 80% and all critical criteria.

## Feedback and retry

Feedback names the first incorrect service mapping, unsafe state transition,
unenforced validator field, missing boundary, exposed value, or overclaimed
evidence; maps it to an outcome ID; and identifies the smallest missing
artifact or rerun. Preserve the original submission and append a correction
record rather than rewriting the failed evidence.

A retry uses a new assessor-provided scenario profile, different domain and key
labels, different message and work bounds, a different RFC public HMAC vector,
and new nonce-writer/capacity constraints. The learner must rerun all affected
normal, endpoint, invalid, mutation, deliberate-failure, and restoration cases.
A revised explanation cannot replace an absent failure test, and a passing
linter cannot replace unsafe authenticated-opening or replay behavior.
