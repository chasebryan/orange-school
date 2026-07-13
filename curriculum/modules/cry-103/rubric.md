# Rubric: authenticated maintenance-channel boundary

## Rubric

The assessment is worth 100 points.

| Criterion | Points | Evidence required |
| --- | ---: | --- |
| Security services and attacker model | 20 | Correct primitive/service mapping, active attacker, compromise timeline, physical-command authorization boundary, non-goals, and availability tradeoffs |
| Key, PKI, randomness, and nonce boundaries | 20 | Separate validation/authenticity/authorization decisions, complete path and lifecycle checks, algorithm-specific randomness and uniqueness rules, and explicit failure ownership |
| Bounded mechanics and strict public-record evidence | 25 | Correct non-secure derivation, exact bounds and types, canonical transcript framing, all fields bound, positive/boundary/invalid tests, and preserved mutation sensitivity |
| Ratified composition and failure review | 20 | Exact published profile and implementation boundary, complete context/key/nonce/state design, fail-closed state machines, and no learner-written production cryptography |
| Post-quantum migration | 10 | Role-separated FIPS mapping, errata and KEM guidance, inventory and measurements, exact hybrid decision, rollout/retirement gates, blockers, and owners |
| Reproducibility and evidence limits | 5 | Environment, sources, commands, channels, statuses, bounds, outcome map, and accurate limits |
| **Total** | **100** |  |

## Critical criteria

All four critical criteria must pass:

1. **Service and attacker integrity:** earn at least 16/20 for security services
   and attacker model. Signatures, encryption, KEM/key agreement,
   authentication, authorization, key confirmation, replay protection, and
   forward secrecy must not be treated as interchangeable. Missing active key
   substitution or authorizing a physical command solely from cryptographic
   validity fails this criterion.
2. **Trust-boundary integrity:** earn at least 16/20 for key, PKI, randomness,
   and nonce boundaries. Mathematical/encoding validation, key authenticity,
   identity/usage policy, and command authorization must be distinct. Every
   secret-generating and nonce-generating component needs an exact requirement
   and failure result. Accepting a parsed leaf certificate as authenticated or
   inventing signature randomness fails this criterion.
3. **Executable-boundary integrity:** earn at least 20/25 for bounded mechanics
   and strict public-record evidence. Every type and work bound must be
   enforced, every record field must affect the encoded context, malformed and
   mutated inputs must fail, and the deliberate omission must be detected.
   Presenting the toy group or public hash as cryptographic security evidence
   fails this criterion.
4. **Composition and failure integrity:** earn at least 16/20 for the ratified
   composition and failure review. The design must name a complete published
   application profile and release no plaintext, keying material, partial
   command, detailed validity oracle, or weaker fallback on failure. A
   home-grown primitive, ad-hoc algorithm pairing, invented hybrid combiner, or
   unspecified nonce state fails this criterion.

A total of 80 or more cannot compensate for a failed critical criterion.

## Scoring

- **Security services and attacker model (20):** 5 for assets, roles, trust
  boundaries, and key owners; 6 for passive/active/adaptive capabilities and
  compromise timeline; 6 for correct service, non-goal, confirmation, replay,
  and forward-secrecy mapping; and 3 for physical authorization and
  availability boundaries.
- **Key, PKI, randomness, and nonce boundaries (20):** 6 for trust-anchor,
  path, identity, usage, status, time, offline, and rotation decisions; 5 for
  separate grammar, canonical, mathematical, authenticity, authorization, and
  lifecycle checks; 5 for algorithm-specific unpredictability/uniqueness,
  scope, restart, concurrency, and failure rules; and 4 for logging,
  zeroization, retry, commit, resource, and side-channel requirements.
- **Bounded mechanics and strict public-record evidence (25):** 6 for correct
  order-23 derivation and fixed-profile validation; 7 for exact fields, types,
  identities, offers, epochs, message and work bounds; 5 for domain-separated,
  counted, length-prefixed transcript hashing and complete deterministic
  context encoding; and 7 for normal, endpoint, outside-bound, invalid,
  transcript, order, downgrade, and mutation-sensitive tests.
- **Ratified composition and failure review (20):** 5 for exact sources,
  algorithms, identifiers, errata, library/module, key-authentication, and wire
  boundaries; 5 for labeled context, key separation, associated data, replay,
  nonce, and exporter decisions; 7 for complete send/receive transitions,
  commit/rollback, uniform public failure, and no fallback or partial output;
  and 3 for required interoperability, vector, malformed, state, fuzzing,
  resource, and side-channel evidence.
- **Post-quantum migration (10):** 3 for complete twelve-year inventory and
  owner map; 2 for separate FIPS 203/FIPS 204 roles, FIPS 203 errata, and SP
  800-227; 3 for quantified capacity and staged mixed-fleet/downgrade/rollback
  gates; and 2 for an exact hybrid profile or preserved blocker plus classical
  retirement condition.
- **Reproducibility and evidence limits (5):** 3 for environment, sources,
  directory, commands, channels, statuses, bounds, mutation, and final result;
  and 2 for outcome mapping and precise limits on every evidence category.

Pass only with at least 80/100 and all critical criteria.

## Feedback and retry

Feedback identifies the first service mismatch, missing attacker capability,
unjustified trust decision, unenforced bound, unbound transcript field,
secret-dependent failure, unsupported profile, or migration invention; maps it
to CRY-103-01, CRY-103-02, or CRY-103-03; and names the missing evidence.
Preserve the original submission and append a correction record.

A retry uses assessor-selected teaching scalars, a different fixed small group
whose order is supplied for verification, changed public-record bounds and
field names, a different controller trust failure, and a different published
application profile or migration constraint. Rerun every affected derivation,
normal/boundary/invalid test, transcript mutation, state-machine review, and
migration gate. Revised prose cannot replace missing executable rejection
evidence; a new passing test cannot establish production cryptographic
security; and a library name cannot replace an exact, authenticated,
standards-led profile.
