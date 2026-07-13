# Lab: public-key protocol boundary review

## Goal

Turn a security requirement into an auditable public-key protocol boundary.
Separate encryption, signatures, and key establishment; define an active
attacker; authenticate and validate keys; bind a public transcript; specify
randomness, nonce, and failure behavior; and plan a standards-led
classical-to-post-quantum migration. Implement only bounded teaching
mechanics and public-metadata validation.

## Setup

From the repository root, inspect and run the supplied examples:

~~~sh
cd curriculum/modules/cry-103
python3 --version
PYTHONDONTWRITEBYTECODE=1 python3 examples/worked_case.py
PYTHONDONTWRITEBYTECODE=1 python3 checks/lab_smoke.py
~~~

The final command must print <code>cry-103 lab smoke: PASS</code> and exit 0.
It uses Python 3.11 or newer, the standard library, local public data, and a
temporary directory only.

Create a separate temporary workspace for learner work:

~~~sh
workdir="$(mktemp -d)"
cd -- "$workdir"
pwd
~~~

Keep every generated file under the printed directory. Do not copy a private
key, credential, random seed from an operational system, certificate with
private material, production message, or other secret into the lab. Do not
install packages or use a network service. The exercise never asks you to
implement encryption, a signature, a KEM, a KDF, an AEAD, certificate-path
validation, or a hybrid combiner.

## Tasks

1. **Define the services and attacker.** Use this scenario: a field device
   downloads signed software manifests and establishes an authenticated
   confidential telemetry session with one service endpoint. Write
   <code>threat-model.md</code> containing:

   - assets, roles, trust boundaries, entry points, and key owners;
   - passive observation plus active interception, substitution, replay,
     reordering, malformed-input, downgrade, and adaptive-failure capabilities;
   - separate requirements for manifest signatures, recipient key
     authentication, key establishment, key confirmation, telemetry
     confidentiality/integrity, replay resistance, and update freshness;
   - compromise cases for device long-term key, service long-term key,
     ephemeral state, trust anchor, random generator, and stored old traffic;
     and
   - explicit non-goals and availability tradeoffs.

   Make a service table with operation, initiating key, verifying or receiving
   key, goal, attacker model, authenticated input, output, and non-goals.
   Explain why signing a manifest cannot encrypt it, why encryption to an
   unauthenticated public key is vulnerable to substitution, and why bare key
   agreement lacks peer authentication.

2. **Derive and audit the bounded mechanics.** For the fixed public teaching
   profile <code>(p,q,g)=(23,11,2)</code>:

   - enumerate <code>g^0</code> through <code>g^10 mod p</code> and prove from
     the table that the generated subgroup has order 11;
   - derive the public values and both agreement calculations for teaching
     scalars 4 and 9;
   - show why 1 is the identity, 22 has order 2, and 5 is not in the order-11
     subgroup;
   - trace the exact validation order for a valid peer value, identity,
     out-of-range value, and out-of-subgroup value; and
   - state why complete enumeration makes this profile non-secure and why its
     validation rule cannot be copied to X25519, an elliptic-curve point
     profile, or ML-KEM.

   Create <code>toy_mechanics.py</code> from your derivation. Accept exact
   integers only; fix all parameters; allow teaching scalars 1 through 10;
   accept only non-identity members of the fixed subgroup; and expose public
   value and agreement-mechanics functions. Label every output public and
   non-secure.

3. **Build a strict public transcript record.** Create
   <code>public_record.py</code> using only <code>hashlib</code>,
   <code>re</code>, and standard-library types. It must process public metadata
   only and enforce this changed contract:

   - exact plain-dictionary fields <code>profile_id</code>,
     <code>protocol_id</code>, <code>protocol_version</code>,
     <code>offered_profiles</code>, <code>selected_profile</code>,
     <code>role</code>, <code>local_key_id</code>,
     <code>peer_key_id</code>, <code>purpose</code>,
     <code>transcript_hash</code>, <code>auth_requirement</code>,
     <code>nonce_requirement</code>, and <code>public_failure</code>;
   - fixed teaching profile
     <code>field-device-telemetry-record-v1</code>, one exact offered/selected
     profile, and fixed strings stating external PKI validation, an
     implementation-managed unique-per-key nonce, and one public rejection;
   - ASCII token fields of 1 through 48 bytes, printable purpose of 1 through
     80 bytes, exact integer version 1 through 4,095, two distinct key
     identifiers, and role <code>device</code> or <code>service</code>;
   - an ordered tuple of 1 through 12 public byte messages, each 1 through
     1,024 bytes;
   - SHA-256 over a domain separator, message count, and two-byte
     length-prefixed messages; and
   - a deterministic context encoding that includes every field in one fixed
     order with field names and two-byte lengths.

   Reject missing, extra, wrong-type, non-ASCII, control-character,
   out-of-bound, ambiguous-identity, unknown-profile, offer/selection,
   malformed-hash, and transcript-mismatch inputs. The validator must not
   claim that hashing public metadata authenticates it or that its fixed
   algorithm names constitute a complete deployable protocol.

4. **Write normal, boundary, invalid, and mutation tests.** Create
   <code>test_public_boundary.py</code> with <code>unittest</code>. Cover the
   task-2 derivations; scalar endpoints; valid subgroup values; identity,
   minus-one, out-of-subgroup, Boolean, float, and bound failures; record
   field and public-message endpoints; every rejection class in task 3;
   deterministic encoding; and changes to role, purpose, offer, key ID,
   message order, message content, and transcript length. Require each bound
   field to change the context bytes.

   Deliberately remove <code>offered_profiles</code> from the context encoding
   while retaining it in validation. Add a test that detects the omission and
   preserve the failing status. Restore the field and preserve the passing
   status. This mutation demonstrates failure sensitivity; it does not test a
   KEM or downgrade attack end to end.

5. **Produce a KEM-style composition review, not an implementation.** Write
   <code>profile-review.md</code> for an assessor-approved, published
   KEM/KDF/AEAD application profile. Cite the exact controlling standard,
   publication status, edition, errata decision, registered identifiers, and
   library/module boundary. Include:

   - security goals, attacker capabilities, assumptions, and non-goals;
   - authenticated recipient-key source and separate mathematical/encoding
     validation;
   - encapsulation and decapsulation inputs, outputs, and prohibited outputs;
   - labeled key-schedule inputs, derived-key separation, exact setup context,
     associated data, and exporter labels if used;
   - nonce owner, uniqueness scope, counter exhaustion, concurrency, restart,
     and state-commit behavior;
   - canonical wire fields, length bounds, message order, role and identity
     binding, replay state, and downgrade resistance;
   - internal error categories and the one externally observable rejection;
   - known-answer/interoperability, malformed-input, state, rollback,
     resource, and side-channel evidence required before release; and
   - ownership for implementation updates, errata review, key rotation,
     monitoring, incident response, and retirement.

   If the profile uses RFC 9180, distinguish base, PSK, authenticated, and
   authenticated-PSK modes and select only one. State that HPKE does not define
   the application's wire format or authenticate an arbitrary recipient key.
   Do not add ML-KEM to an HPKE suite unless the chosen published profile
   registers and specifies that exact integration.

6. **Audit key authenticity and randomness.** In
   <code>boundary-matrix.md</code>, make two matrices.

   The PKI matrix must cover trust-anchor provenance, chain signatures,
   validity time, reference identity, basic constraints, key usage, extended
   key usage, name constraints, critical extensions, algorithm policy,
   revocation/status availability, caching, pin rotation, clock failure, and
   public failure. For each, state input, decision owner, failure result, and
   evidence. Explain why certificate parsing and leaf-signature verification
   are insufficient.

   The randomness/nonce matrix must cover long-term key generation, ephemeral
   key generation, KEM encapsulation randomness, DSA/ECDSA per-message value,
   AEAD nonce, challenge/freshness value, test vector seed, and blinding if the
   selected implementation uses it. For each, state whether unpredictability,
   uniqueness, or both are required; scope; responsible component; restart and
   concurrency behavior; failure result; and validation evidence. Cite FIPS
   186-5 and RFC 6979 for signature-generation distinctions without designing
   a replacement procedure.

7. **Plan a post-quantum migration.** Write <code>pq-migration.md</code> for
   the same device fleet. Include an inventory of keys, certificates,
   protocols, libraries, hardware, firmware, stored ciphertext, signed
   artifacts, trust anchors, dependencies, owners, cryptoperiods, and data
   secrecy/verification lifetimes. Compare the selected classical baseline
   with applicable FIPS 203 and FIPS 204 roles; record the FIPS 203 errata
   review; and measure or budget key, encapsulation, signature, certificate,
   handshake, storage, memory, latency, and bandwidth impacts.

   Define staged interoperability, malformed-input, mixed-version, downgrade,
   recovery, rollback, observability, and retirement gates. If proposing a
   classical-plus-post-quantum hybrid, identify the exact published combiner
   profile. If no ratified profile fits, record that as a blocker. Never invent
   a combiner, accept either of two signatures, or concatenate two secrets as
   an unevaluated substitute.

8. **Map evidence and limitations.** Write <code>evidence-map.md</code> that
   maps every artifact and test group to CRY-103-01, CRY-103-02, or
   CRY-103-03. Record Python version, absolute temporary directory, source
   identity, exact commands, stdout, stderr, and immediate statuses. State
   explicitly that the work does not establish primitive correctness,
   computational security, entropy quality, key authenticity, certificate
   validation, interoperability, constant-time behavior, side-channel safety,
   Orange behavior, or standards conformance.

## Verification

From the temporary workspace, run:

~~~sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v
test_status=$?
printf 'test status: %s\n' "$test_status"
~~~

Status 0 is necessary but not sufficient. Inspect the derivations, source,
tests, threat model, matrices, profile review, migration plan, mutation record,
and limitations. Confirm that:

- each operation is tied to the correct goal and non-goal;
- the attacker can substitute keys, transcripts, offers, and failures;
- every input and work bound is checked before hashing or exponentiation;
- every context field affects the deterministic encoding;
- authenticating a key and validating it are separate requirements;
- randomness, uniqueness, and deterministic signature generation are not
  conflated;
- the KEM-style review names a complete published profile and contains no
  learner-written cryptographic primitive;
- one public failure does not release plaintext, keying material, or detailed
  validity distinctions;
- a proposed post-quantum or hybrid path has an exact profile or remains
  explicitly blocked; and
- the passing Python suite is labeled structural evidence only.

Rerun the repository smoke check separately from the module directory. Remove
any generated bytecode cache from the temporary copy before packaging the
submission.

## Reflection

Write six to eight sentences:

- Which requirement selected a signature, and which selected key
  establishment plus AEAD?
- Where did public-key authenticity enter, and what would fail if it were
  omitted?
- Which validated field prevented an algorithm-offer downgrade from becoming
  invisible?
- Which values required unpredictability, uniqueness, or both?
- Why did the mutation test provide more evidence than a passing happy path?
- Which public failures were intentionally collapsed, and what internal
  operational signal remained?
- What exact evidence is missing before the reviewed profile can be deployed?
- What condition would block rather than improvise a post-quantum hybrid?
