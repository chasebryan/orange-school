# Assessment: security contract for a hostile relay

## Instructions

Complete this assessment independently with Python 3.11 or newer and only the
standard library. Work in a fresh temporary directory. Submit the written
security contract, diagrams or tables, executable model, tests, failure audit,
and a reproducible evidence record. Do not copy or rename the worked
sealed-export model or the offline-recovery lab model.

Do not implement cryptography or select an algorithm. Treat any policy-approved
cryptographic component as a conditional dependency whose exact interface and
preconditions still must be stated. Passing the structural evaluator is not a
security proof or deployment approval.

The assessment covers:

- **CRY-101-01:** State an asset-specific cryptographic goal, an attacker model,
  and a security-game-style notion with explicit capabilities, resources,
  exclusions, success event, and evidence limits.
- **CRY-101-02:** Distinguish keys, nonces, and security randomness while
  documenting assumptions, trust boundaries, lifetimes, scopes, and failure
  responses.
- **CRY-101-03:** Analyze how cryptographic claims compose with encoding,
  state, key management, and application behavior, then use a bounded
  evaluator without mistaking structural completeness for security.

Use this independently assessed scenario:

> Remote laboratory instruments send embargoed measurement batches through a
> relay operated by another organization. The collector releases a batch to a
> research database only after validation. The relay attacker may observe,
> delay, drop, duplicate, reorder, alter, inject, and roll back stored traffic,
> and may choose actions after seeing prior responses. Instrument, collector,
> platform key service, and their administrators are initially uncompromised.
> Instrument replacement, collector restart, simultaneous instruments, and
> key-epoch change are normal lifecycle events. The assessment must state what
> changes if one instrument is later compromised.

## Knowledge check

1. Distinguish an asset, mechanism, security goal, security notion, assumption,
   and trust boundary. Give one sentence that incorrectly mixes two of them and
   repair it.
2. Compare confidentiality, integrity, authenticity, freshness, and
   availability. Give one pair that does not imply the other in each direction.
3. List the setup, interfaces, challenge, win event, baseline, advantage,
   quantifiers, resource bounds, and assumptions of a game-style definition.
   Explain why tests cannot prove the resulting quantified claim.
4. Explain how passive, active, adaptive, storage, endpoint-compromise, and
   side-channel capabilities change the supported claim.
5. Distinguish a secret key, public key, key identifier, nonce, entropy source,
   deterministic random-bit generator state, and generated random output.
6. Explain why “unique under one key,” “unpredictable,” and “secret” are
   different properties. Give a value that plausibly needs each combination
   you use.
7. Name five premises needed to carry an authenticated-encryption claim into
   an application record-acceptance claim. Identify at least three properties
   authenticated encryption alone does not provide.
8. State what a clean run of the supplied structural evaluator establishes and
   at least six matters it does not establish.

## Independent task

1. **Asset and goal contract — CRY-101-01.** Create
   <code>security-contract.md</code>. Define at least three assets, including
   embargoed batch contents, batch acceptance state, and a key capability.
   State owner, location and lifetime, required properties, declared leakage,
   unacceptable outcomes, and recovery objective. Address confidentiality,
   integrity, authenticity, freshness, and availability separately; do not
   claim the relay can be prevented from dropping all traffic.
2. **Attacker model — CRY-101-01.** Define observation and mutation interfaces,
   adaptive choices, storage control, visible errors and timing, concurrency,
   time/memory/query bounds, and initial exclusions. Add a capability matrix
   mapping each power to targeted assets and requirements. Then extend the
   model with compromise of one instrument. State whether past batches, future
   batches from that instrument, and batches from other instruments remain in
   scope, and identify the assumptions needed for each answer. Unsupported
   forward- or backward-security claims fail this task.
3. **Security notions — CRY-101-01.** Write two game-style definitions. The
   first tests confidentiality of equal-length measurement batches and must
   include declared metadata leakage, challenge restrictions, one-half
   baseline, advantage, and resource bounds. The second treats acceptance of a
   new unauthorized or replayed batch as a win; define prior authorization,
   “new,” epoch, instrument identity, and all permitted oracle or service
   interactions. For each notion list what it omits and distinguish a proposed
   requirement from proof, test evidence, and deployment evidence.
4. **Trust, assumptions, and material — CRY-101-02.** Document at least three
   trust boundaries from instrument encoding through relay storage to collector
   release. Each boundary needs source and destination zones, exact data,
   canonical representation, validation order, release point, failure action,
   and diagnostics. Declare at least four owned, falsifiable assumptions and
   link every one to dependents. Make a separate lifecycle table for secret
   per-instrument keys, public identifiers, nonces, and security randomness.
   For every row state source, purpose, secrecy, authenticity,
   unpredictability, uniqueness scope, concurrency rule, persistence, epoch
   transition, compromise response, and destruction or retention behavior.
5. **Bounded executable model — CRY-101-03.** Create
   <code>assessed_model.py</code> by importing the supplied
   <code>security_requirements</code> module through an explicit
   <code>PYTHONPATH</code>. Encode at least three assets, five attacker
   capabilities, four assumptions, three trust boundaries, one secret-key
   declaration, one nonce declaration, one randomness declaration, six
   goal-specific requirements, and three composition dependencies. The model
   must remain within every declared bound, render deterministically, have zero
   findings, print the evaluator limitation, and exit nonzero if incomplete.
   Prose and code identifiers must trace in both directions.
6. **Failure-sensitive tests — CRY-101-03.** Create
   <code>test_assessed_model.py</code> with <code>unittest</code>. Test the clean
   model and at least eight independent defects: duplicate ID, uncovered goal,
   undeclared attacker capability, unknown assumption, unused trust boundary,
   missing secret-key property, missing nonce uniqueness, and contradictory
   secret/public properties. Add exact-bound tests for 16 assets and
   400-character text, one-above-bound tests, strict enum/type tests, and a
   non-model evaluator call. Demonstrate failure sensitivity with one
   deliberately wrong expectation, preserve that failed result, restore it,
   and preserve a passing run.
7. **Composition and failure audit — CRY-101-03.** Create
   <code>composition-audit.md</code>. Trace at least these dependencies:
   policy-approved component behavior, key authorization, random-bit service,
   nonce allocation across concurrent instruments and restart, canonical
   encoding, identity-to-key binding, replay state, release ordering, and
   operator recovery. For each, identify the dependent game or application
   claim, detection signal, containment action, recovery action, and residual
   confidentiality, integrity, freshness, or availability harm. Analyze nonce
   rollback, key exposure, parser disagreement, replay-state loss, verbose
   error divergence, and relay deletion as separate failures.
8. **Evidence and limits.** Record Python version, absolute workspace, exact
   commands, stdout, stderr, immediate statuses, source-file identity, model
   counts, and declared bounds. Create <code>evidence-map.md</code> classifying
   each item as definition, assumption, proof from a cited source, structural
   check, unit test, component-validation evidence, or deployment evidence.
   Do not relabel one category as another. Name the standards or specifications
   that an implementation team would still need to select and verify without
   claiming this assessment made that selection.

## Completion criteria

Use the [rubric](rubric.md). Passing requires at least 80/100 and every critical
criterion. A passing submission must:

- satisfy **CRY-101-01** with asset-specific goals and two complete,
  attacker-matched security notions;
- satisfy **CRY-101-02** with explicit trust crossings, owned assumptions, and
  correct key/nonce/randomness distinctions across lifecycle events;
- satisfy **CRY-101-03** with a traced, bounded, failure-sensitive executable
  model and a premise-complete composition audit; and
- preserve reproducible evidence while limiting every claim to the model,
  definitions, assumptions, and evidence actually supplied.

A mechanism-only answer, ambiguous win event, nonce/randomness substitution,
unstated endpoint trust, unsupported compromise claim, evaluator output called
a proof, or cryptographic implementation cannot pass.
