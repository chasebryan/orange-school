# Assessment: fail-closed symmetric-protocol review

## Instructions

Complete this assessment independently in a fresh temporary directory with
Python 3.11 or newer and only the standard library. Do not copy or rename the
lesson's manifest, example functions, lab case, tests, or prose. Submit a
self-contained review package, source, tests, and reproducible evidence record.

Use only public assessor-provided byte strings. Do not use a real key, password,
credential, user record, production configuration, network operation, external
package, or global configuration change. Do not implement encryption, a block
or stream cipher, padding, HKDF, a mode of operation, or AEAD. When the scenario
needs those operations, specify a maintained production-library interface and
its required behavior without simulating the cryptography.

The assessed outcomes are:

- **CRY-102-01:** Distinguish symmetric encryption, an unkeyed hash, a MAC, a
  password KDF, a general KDF, and AEAD by goal, contract, and limitation.
- **CRY-102-02:** Analyze nonce, tag, AAD, domain, key-separation, composition,
  replay, and failure invariants.
- **CRY-102-03:** Produce bounded executable SHA-256, HMAC-SHA-256, and
  PBKDF2-HMAC-SHA-256 mechanics and invalid-input evidence without making a
  production-security claim.
- **CRY-102-04:** Specify and audit a versioned metadata manifest and identify
  the library, deployment, and operational evidence still required.

The scenario is a disconnected research station that stores sensor batches,
emits visible audit envelopes, and authenticates local operators. The supplied
fictional [station assessment profile r7](resources/station-assessment-profile-r7.md)
defines the exact algorithm identifiers, key purposes, ASCII domain labels,
canonical AAD and audit encodings, nonce layout, writer allocation, message and
record caps, rotation rules, replay owner, password-parameter authority, and
benchmark record used by this assessment. Treat every stated value and bound
as an input; do not invent a replacement or silently import the lesson fixture.

This fictional sheet is evidence about the assessment scenario only. It is not
current organizational, regulatory, FIPS-module, platform, or production
approval.

## Knowledge check

Answer without copying the lesson.

1. For symmetric encryption, hash, MAC, password KDF, general KDF, and AEAD,
   state inputs, outputs, primary claim, and one claim it does not provide.
2. Explain preimage, second-preimage, and collision resistance. Why must hash
   collisions exist, and why can the function still be useful?
3. Give an attack in which an unkeyed digest of a download is replaced with the
   download. Contrast a trusted digest channel and a MAC.
4. Explain why HMAC is not `hash(key || message)`, why a full equality operator
   is not the intended verification API, and why a shared-key MAC is not a
   signature among key holders.
5. Distinguish password salt, HKDF salt, HKDF `info`, AEAD nonce, AAD, MAC tag,
   AEAD tag, domain label, and key identifier. State which are normally secret.
6. Explain why HKDF must not silently replace a password KDF and why a
   password KDF does not create entropy.
7. Trace authenticated opening for correct input, changed ciphertext, wrong
   AAD, wrong nonce, wrong key, and wrong tag. At what point may plaintext be
   returned?
8. Explain the consequences of nonce reuse for a same-key AEAD context. Give
   restart, clone, concurrency, rollback, and exhaustion cases a design must
   handle.
9. Explain how replay can pass AEAD authentication and what protocol state must
   reject it.
10. Distinguish algorithm standardization, parameter-profile approval,
    protocol correctness, implementation validation, and operational fitness.

## Independent task

1. **Claims and service selection — CRY-102-01.** Write `claims.md` containing
   an asset/attacker/claim/assumption/exclusion table for sensor-record
   confidentiality, record and header integrity, audit-envelope
   authentication, operator password defense, key derivation, and replay
   control. Map each to a primitive or protocol-state mechanism. For every row,
   give one plausible but wrong substitution and explain the failure.

   Add a value-semantics table for password, key, salt, nonce, AAD, digest, MAC
   tag, AEAD tag, ciphertext, key identifier, domain, and replay counter. Correct
   any statement that makes a nonce or salt secret, makes a digest authentic by
   itself, or makes ciphertext authenticated by itself.
2. **Independent public mechanics — CRY-102-03.** Create
   `assessed_mechanics.py` and `test_assessed_mechanics.py`. Use `hashlib` and
   `hmac` directly behind your own explicit bounds:

   - SHA-256 accepts exact bytes from 0 through 131,072 bytes;
   - HMAC-SHA-256 accepts a 16-through-80-byte public test key, a bounded
     message, and verifies only a full 32-byte tag with `compare_digest`;
   - PBKDF2-HMAC-SHA-256 accepts a nonempty public test label of at most 512
     bytes, a 16-through-48-byte salt, exact-integer lab iterations from 1
     through 15,000, and output from 16 through 40 bytes; and
   - all wrong types, Boolean numeric values, malformed tags, and values outside
     the bounds fail explicitly.

   Pin the SHA-256 `abc` vector and RFC 4231 HMAC-SHA-256 test case 3. Add a
   fixed PBKDF2 regression using labels clearly marked public. Test every exact
   endpoint and one value beyond each, message and tag modification, and a
   deliberate wrong-vector failure followed by restoration. Print no input,
   digest, tag, or derived bytes. The module docstring and evidence must say the
   lab cost range is not a password-storage recommendation and that Python API
   tests do not prove constant-time behavior, secure erasure, or production
   key handling.
3. **Versioned manifest and linter — CRY-102-04.** Create
   `station-manifest.json`, `manifest-schema.md`, `lint_manifest.py`, and
   `test_manifest.py`. Design a schema different from the lesson and lab while
   representing every field on `station-assessment-profile-r7`. Include exact
   references from algorithm entries to distinct key purposes and domains,
   nonce allocation and persistence rule, tag sizes, AAD schema, failure
   policy, password parameter authority and benchmark version, record/rekey
   limit source, and replay-state owner.

   The JSON is metadata only. It must contain no key bytes, password, verifier,
   plaintext, ciphertext, nonce instance, tag instance, or environment-derived
   value. The linter must use exact field sets and types, return deterministic
   errors, and reject every unsafe change named below. It must not treat a
   recognized algorithm string as proof of approval or implementation.
4. **Failure-sensitive manifest tests — CRY-102-02 and CRY-102-04.** Starting
   from one valid fixture, deep-copy and independently mutate:

   - algorithm identifier, key size, nonce size, nonce uniqueness, tag size;
   - AAD schema or domain, unknown version, and non-canonical encoding name;
   - fail-before-plaintext policy;
   - high-entropy HKDF source and HKDF output-purpose label;
   - duplicate AEAD/MAC key labels and duplicate domains;
   - password salt minimum, parameter authority, and benchmark version;
   - record-limit source, rekey rule, and replay owner; and
   - missing, extra, wrong-container, wrong-scalar, and Boolean numeric fields.

   Every mutation must make the linter fail for the intended reason. Include an
   explicit unexpected `secret_material` field and show its rejection. Preserve
   one valid CLI run, one deliberate invalid run, immediate statuses, stdout,
   and stderr.
5. **Nonce and replay state machine — CRY-102-02.** Write
   `state-machine.md` for three writers that may operate concurrently, restart,
   be restored from backup, or be cloned. Define nonce allocation under one key,
   durable reservation, exhaustion, writer retirement, rotation sequencing,
   and recovery stop conditions. Compute the available counter space from your
   field layout and state the much lower maximum permitted use selected by the
   scenario profile before mathematical exhaustion. Compute the plaintext-block
   contribution, add the canonical AAD and construction bookkeeping, and state
   why even this exercise cap remains blocked on a current quantitative GCM
   review and deployment authority.

   Define canonical AAD bytes containing station, writer, schema version,
   record type, batch sequence, and key identifier. Define replay persistence
   and the response to stale, duplicated, unknown-version, rolled-back, and
   out-of-window records. Explain why valid replay is not a tag failure.
6. **Composition and failure audit — CRY-102-02.** Review this intentionally
   unsafe design description in `audit.md`:

   > One key is used for record encryption and audit HMAC. Each writer chooses
   > random nonces but stores no nonce state. The visible version and sequence
   > are not AAD. The receiver decrypts, parses, and displays a record before
   > comparing a caller-selected tag prefix with `==`. On failure it retries as
   > unauthenticated legacy data. Operator passwords are hashed once with
   > SHA-256. A deployment key is produced by applying HKDF to the password.

   Identify every distinct violated invariant. For each, describe an attacker
   action, resulting claim failure, fail-closed correction, evidence needed to
   verify the correction, and one residual risk. Replace the design with a
   library-level interface and state machine in pseudocode, but do not implement
   cryptographic operations. The opening operation must have exactly two
   results: authenticated plaintext or failure, with parsing after success.
7. **Algorithm/profile/library boundary — CRY-102-04.** Write `approval.md`.
   For AES, GCM, SHA-256, HMAC, PBKDF2, and HKDF, cite the exact primary FIPS,
   NIST SP, or RFC landing page and state what that source specifies. Then list
   separately:

   - what the fictional assessment profile selects;
   - what a current deployment authority must approve;
   - what the selected library/module must demonstrate;
   - what platform and operational tests must demonstrate; and
   - what remains excluded from this assessment.

   Include Argon2/RFC 9106 as a password-profile alternative that Python 3.11's
   standard library example does not implement. Do not recommend a universal
   work factor from the assessment's fast test range.
8. **Reproducibility and handoff.** Write `evidence.md` and `handoff.md`.
   Record Python version, absolute temporary workspace, source identities,
   exact commands, public-vector origins, stdout, stderr, immediate statuses,
   input/work bounds, and the deliberate-failure/restoration sequence. In the
   handoff, assign owners and stop conditions for approval freshness, library
   selection, module validation if required, key generation and custody, nonce
   persistence, password benchmarking, serialization, message and rekey limits,
   replay storage, side-channel review, telemetry, incident response, backup
   and restore, dependency updates, and interoperability. State that no
   assessed code is an encryption or password-storage subsystem.

## Completion criteria

Use the [rubric](rubric.md). Passing requires at least **80%** and every critical
criterion. A passing submission must:

- map every service and value to an accurate contract and limitation for
  **CRY-102-01**;
- preserve same-key nonce uniqueness, exact AAD/domain/key separation,
  fail-before-plaintext opening, and separate replay state while finding every
  unsafe composition defect for **CRY-102-02**;
- pass normal, exact-endpoint, invalid, tamper, and failure-sensitivity tests for
  bounded public SHA-256, HMAC-SHA-256, and PBKDF2-HMAC-SHA-256 mechanics while
  making no production claim for **CRY-102-03**; and
- provide a complete metadata-only manifest, deterministic linter, primary
  source map, and owner/stop-condition handoff for **CRY-102-04**.

A submission cannot pass if it implements or recommends home-grown encryption,
uses a real secret, releases plaintext before authentication, permits same-key
nonce reuse, conflates HKDF with password hashing, reuses one key across the
AEAD and MAC purposes, calls the test iteration range a production profile, or
treats linter success as algorithm or deployment approval.
