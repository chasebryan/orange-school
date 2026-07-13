# Assessment: authenticated maintenance-channel boundary

## Instructions

Complete this assessment independently with Python 3.11 or newer and only the
standard library. Work in a fresh temporary directory with public teaching
data only. Submit derivations, threat model, standards/profile review, source,
tests, failed-mutation evidence, PKI and randomness matrices, migration plan,
and a reproducible command/result record. Do not copy or rename the supplied
examples or the lab implementation.

Do not implement or simulate production encryption, signatures, a KEM, a KDF,
an AEAD, certificate-path validation, or a classical/post-quantum combiner.
The executable task is limited to an explicitly non-secure finite group and a
strict validator for public transcript metadata.

This assessment covers:

- **CRY-103-01:** Distinguish public-key encryption, digital signatures, and
  key establishment by operation, security goal, attacker capability, and
  non-goal.
- **CRY-103-02:** Analyze parameter and key validation, randomness and nonce
  requirements, public-key authenticity, transcript and context binding, and
  externally observable failure behavior.
- **CRY-103-03:** Design and evaluate a KEM-style composition and a
  classical-to-post-quantum migration boundary using ratified profiles,
  explicit PKI assumptions, and failure-safe evidence rather than home-grown
  production cryptography.

## Knowledge check

1. Contrast public-key encryption, digital signatures, key agreement, key
   transport, KEM encapsulation, and key confirmation. Give one goal and two
   non-goals for each.
2. Define a passive attacker, active person-in-the-middle, adaptive
   chosen-ciphertext attacker, and chosen-message signature attacker. Explain
   why a hardness assumption is not a complete protocol security claim.
3. Explain why “encrypt with a private key” is an unsafe model of signatures
   and why a valid signature provides no message confidentiality.
4. Separate mathematical/encoding key validation from public-key
   authenticity. Give two independent failures accepted when only one is
   checked.
5. Describe the trust-anchor and application inputs to RFC 5280 path
   validation. Name six path, identity, usage, or status decisions beyond
   parsing a leaf certificate.
6. Explain why DSA/ECDSA per-message value reuse or bias can expose a private
   key. Contrast a standard deterministic procedure with a fixed value,
   counter, and test seed.
7. Distinguish nonce uniqueness and unpredictability. Give an example that
   requires each and identify its scope.
8. Describe KEM key generation, encapsulation, and decapsulation. Explain why
   a KEM shared secret is not a bulk-encryption key or authenticated channel.
9. Explain why a KEM/KDF/AEAD composition needs a complete profile. Name eight
   values or identities that may need transcript or context binding.
10. Explain how detailed parsing, decapsulation, signature, or AEAD failures
    can become an oracle. Distinguish a uniform public rejection from
    controlled internal diagnosis.
11. Distinguish HPKE's use of “hybrid public key encryption” from a
    classical-plus-post-quantum hybrid migration. Explain why neither permits
    an ad-hoc combiner.
12. Define crypto agility without permitting unauthenticated algorithm
    negotiation. List six inventory or lifecycle facts needed for a
    post-quantum migration.

## Independent task

Use this scenario: a manufacturer operates controllers for twelve years. An
authorized maintenance station sends signed authorization manifests and then
opens an authenticated confidential maintenance session through an untrusted
relay. A controller may be offline for months. Commands can change physical
state. Public verification records must remain auditable for twelve years, and
captured session traffic contains commercially sensitive configuration.

1. **Security services and attacker — CRY-103-01 (20 points).** Create
   <code>security-case.md</code> with assets, roles, key owners, trust
   boundaries, entry points, assumptions, non-goals, and an attack tree. The
   attacker can observe, delay, replay, reorder, inject, replace keys and
   certificates, alter algorithm offers, submit malformed inputs repeatedly,
   observe public failures and timing, compromise one controller, and retain
   traffic for future attack. Map each requirement to signature, authenticated
   key establishment, KDF, AEAD, replay state, or non-cryptographic
   authorization. Include long-term and ephemeral compromise timelines,
   forward-secrecy and recovery expectations, command-safety consequences,
   and availability tradeoffs. Explain why none of the selected primitives
   alone authorizes a physical command.

2. **Key, PKI, and randomness boundaries — CRY-103-02 (20 points).** Create
   <code>trust-boundaries.md</code> with:

   - a certificate/path matrix covering trust-anchor provisioning and update,
     chain signatures, time while offline, reference identity, constraints,
     key and extended-key usage, critical extensions, algorithm policy,
     revocation/status availability, cache age, pin rotation, compromise, and
     one public rejection;
   - a key-validation matrix separating length/grammar, canonical encoding,
     algorithm/parameters, mathematical checks, prohibited outputs,
     authenticity, authorization, and lifecycle state for every public key;
   - a randomness/nonce matrix for long-term and ephemeral keys, KEM
     encapsulation, signature generation, AEAD nonce, challenge, test vector,
     and blinding; and
   - exact failure, logging, zeroization, retry, state-commit, resource-bound,
     and side-channel requirements.

   Cite FIPS 186-5, SP 800-56A Revision 3, SP 800-57 Part 1 Revision 5, RFC
   5280, and RFC 6979 at the requirement each supports. Record status, edition,
   and any announced revision rather than treating every source as equally
   current.

3. **Independent bounded mechanics and public-record validator — CRY-103-02
   (25 points).** For the explicitly non-secure teaching profile
   <code>(p,q,g)=(47,23,2)</code>:

   - enumerate all 23 generated elements, establish the generator order, and
     derive both agreement calculations for assessor-selected scalars in 1
     through 22;
   - identify the identity, a valid endpoint, and at least two invalid public
     values from different rejection classes;
   - implement exact-integer scalar and public-value validation, public-value
     derivation, and agreement mechanics with fixed parameters and explicit
     bounds; and
   - label every value enumerable, public, and non-secure.

   Separately implement <code>maintenance_record.py</code>. It processes only
   ordered public messages and an exact record with these fields:
   <code>profile_id</code>, <code>protocol_version</code>,
   <code>offered_profiles</code>, <code>selected_profile</code>,
   <code>role</code>, <code>controller_key_id</code>,
   <code>station_key_id</code>, <code>controller_model</code>,
   <code>command_class</code>, <code>authorization_epoch</code>,
   <code>transcript_hash</code>, <code>trust_requirement</code>,
   <code>nonce_requirement</code>, and <code>public_failure</code>.

   Fix profile <code>maintenance-authorization-record-v2</code>. Define exact
   ASCII/token, integer, count, message-length, and total-work bounds no larger
   than the lab bounds. Require distinct key IDs, role separation, one exact
   offered/selected profile, a positive bounded authorization epoch, fixed
   external trust and nonce requirements, and one public rejection. Hash a
   domain-separated, counted, length-prefixed ordered public transcript. Encode
   every field name and value with unambiguous lengths in a fixed order.

   Write <code>test_maintenance_record.py</code> with positive, exact-boundary,
   outside-bound, wrong-type, identity, subgroup, missing/extra-field,
   noncanonical, transcript-mutation, message-order, role, peer, offer,
   selection, epoch, and public-failure tests. Mutate the encoder to omit
   <code>authorization_epoch</code>; preserve the failing run that detects the
   omission, then restore and preserve the passing run. Python tests are not
   evidence of production cryptographic security or constant-time behavior.

4. **Ratified composition and failure review — CRY-103-03 (20 points).** Write
   <code>composition-review.md</code> for one assessor-approved published
   KEM/KDF/AEAD application profile suitable for the maintenance channel.
   Identify the controlling standards, exact algorithms/parameter sets and
   identifiers, publication status, errata decision, implementation and
   validated-module boundary, authenticated recipient-key source, wire
   grammar, message ordering, setup context, associated data, exporter labels,
   replay state, nonce state, and key separation.

   Provide send and receive state machines. Each transition must name
   validated input, authenticated input, sensitive state created, commit point,
   rollback/clear action, internal diagnostic, and public result. Cover
   unsupported profile, malformed encoding, invalid key or encapsulation,
   trust failure, signature failure, replay, AEAD failure, state exhaustion,
   generator failure, resource exhaustion, and unexpected library failure.
   No failure may release plaintext, derived keying material, partial command,
   or weaker fallback. State the interoperability, vector, negative, state,
   failure-sensitive, fuzzing, resource, and side-channel evidence still
   required. Do not write any cryptographic primitive or combiner.

5. **Post-quantum migration — CRY-103-03 (10 points).** Write
   <code>migration-plan.md</code>. Inventory the twelve-year confidentiality
   and verification exposure, every cryptographic dependency and owner, and
   the device's certificate, firmware, memory, bandwidth, update, and recovery
   constraints. Map KEM and signature roles separately to FIPS 203 and FIPS
   204; include the current FIPS 203 errata decision and SP 800-227 guidance.
   Define measurement, interoperability, mixed-fleet, downgrade, rollout,
   observability, rollback, incident, and classical-retirement gates.

   If proposing a hybrid, cite the exact combiner and application profile and
   state its failure and transcript rules. If the required profile or device
   capacity is unavailable, preserve a quantified blocker and an owner rather
   than inventing a construction. Explain how crypto agility preserves
   authenticated policy while changing algorithms.

6. **Evidence record (5 points).** Create <code>evidence-map.md</code> mapping
   every claim and artifact to an outcome ID and evidence type. Record Python
   version, absolute directory, source revisions, exact commands, stdout,
   stderr, immediate statuses, fixed parameters, all bounds, mutation result,
   and final passing result. State limitations for arithmetic derivation,
   unit tests, standard review, implementation selection, PKI design, and
   migration planning.

## Completion criteria

Use the [rubric](rubric.md). Passing requires at least 80/100 and every
critical criterion. A submission must:

- map every service to the correct operation, goal, attacker, and non-goal for
  **CRY-103-01**;
- keep key validation, key authenticity, authorization, randomness, nonce,
  transcript binding, and public failure as separate enforceable obligations
  for **CRY-103-02**;
- pass normal, exact-boundary, invalid, and failure-sensitive tests while
  labeling the executable work public and non-secure;
- select and review a complete ratified KEM-style application profile without
  implementing a primitive or releasing sensitive output on failure; and
- give each post-quantum role, hybrid decision, rollout gate, blocker, and
  retirement condition a source and owner for **CRY-103-03**.

A correct modular calculation cannot compensate for an unauthenticated key. A
valid certificate chain cannot compensate for a wrong reference identity. A
passing Python suite cannot compensate for an invented production
construction, missing transcript field, secret-dependent public failure, or
unsupported post-quantum combiner.
