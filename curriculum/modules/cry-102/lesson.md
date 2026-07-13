# Symmetric cryptography, hashes, MACs, KDFs, and AEAD

Cryptographic APIs expose values with similar shapes: keys, salts, nonces,
digests, tags, and derived bytes. Their security roles are not interchangeable.
A hash does not authenticate an attacker-controlled message, encryption alone
does not establish integrity, a salt is not a secret key, and a password KDF is
not a general-purpose key-expansion function. Professional work begins by
stating the required service and protocol invariant before choosing an
algorithm or calling a library.

This module teaches those distinctions and the failure behavior around them.
Its Python examples exercise standardized one-way library functions and review
non-secret metadata. They do not implement a cipher or AEAD, and they are not a
production cryptographic system.

## Learning objectives

- **CRY-102-01:** Distinguish symmetric encryption, an unkeyed hash, a MAC, a
  password KDF, a general key-derivation function, and AEAD by security goal,
  input contract, output, and limitation.
- **CRY-102-02:** Analyze nonce uniqueness, tag verification, AAD, domain
  separation, key separation, and composition rules, including the consequence
  of violating each invariant.
- **CRY-102-03:** Use Python 3.11's standard library to check bounded SHA-256,
  HMAC-SHA-256, and PBKDF2-HMAC-SHA-256 mechanics and invalid inputs without
  presenting the exercise as encryption or production key handling.
- **CRY-102-04:** Specify and audit a versioned cryptographic manifest that
  separates algorithm identifiers, parameter profiles, key purposes, and
  fail-closed behavior, then identify what still requires a maintained
  production library and deployment review.

Together these outcomes provide instruction, practice, and independent
assessment for competency **CRY-02**.

## Prerequisites

Pass `cry-101` and `mat-103`. You should be able to state an asset, attacker,
security claim, assumption, and exclusion; distinguish computational evidence
from a proof; and reason about finite arithmetic and collision bounds. This
lesson restates every cryptographic interface it uses.

Use Python 3.11 or newer and only the standard library for the executable
exercise. No network, external package, administrator access, real credential,
production key, or learner-supplied secret is required. The lab data is public
test data.

## Lesson

### Name the service before the primitive

A protocol should begin with claims such as these:

- an observer without the key cannot learn the protected record;
- a modified record is rejected before any plaintext is used;
- a record header is visible but bound to the ciphertext;
- two different protocol purposes do not reuse one key or input domain; and
- a password database makes each offline guess deliberately expensive.

Only then can the designer map claims to mechanisms.

| Mechanism | Typical inputs | Output | Primary service | Does not provide by itself |
| --- | --- | --- | --- | --- |
| Symmetric encryption | secret key, mode inputs, plaintext | ciphertext | confidentiality | integrity or authenticity |
| Cryptographic hash | message | fixed-length digest | a one-way message summary with collision and preimage goals | authenticity when an attacker can replace message and digest |
| MAC | secret key, framed message | authentication tag | integrity and source authentication among key holders | confidentiality or non-repudiation between key holders |
| Password KDF | password, unique salt, cost profile | verifier or derived bytes | cost amplification for low-entropy password guesses | entropy creation or general key expansion |
| General KDF | keying material, salt/context, output labels | one or more keys | extraction and/or purpose-separated expansion | password-guess resistance unless designed and profiled for passwords |
| AEAD | secret key, nonce, plaintext, AAD | ciphertext and tag | confidentiality plus integrity for plaintext and AAD | nonce management, key storage, authorization, or replay policy |

AES is a block cipher standardized by FIPS 197. It transforms one fixed-size
block under a key. A block cipher alone is not a file, record, or transport
encryption scheme. A mode defines how blocks, nonces, padding or counters, and
authentication interact. GCM, specified by NIST SP 800-38D, is an authenticated
encryption mode. ChaCha20-Poly1305 is a different AEAD specified for IETF use by
RFC 8439. Do not mix pieces from their interfaces or construct a new mode.

### Algorithm, construction, profile, and implementation are separate decisions

“Use AES” is incomplete. A review needs at least four layers:

1. **Algorithm or construction:** a precise identifier and revision, such as
   AES-256-GCM under a named specification.
2. **Parameter profile:** key size, nonce size and allocation rule, tag size,
   message limits, password work factors, domain labels, rekey limits, and
   allowed failure behavior.
3. **Protocol binding:** exact byte serialization, AAD fields, replay state,
   version negotiation, key purpose, and lifecycle.
4. **Implementation:** a maintained cryptographic library or validated module,
   safe API, platform behavior, side-channel posture, key store, monitoring,
   tests, and operational ownership.

“Approved” always has an authority and scope. FIPS and NIST publications define
algorithms and guidance for particular contexts; IETF RFCs define interoperable
protocol constructions; an organization then selects a current deployment
profile. An algorithm name appearing in a standard does not prove that every
mode, key size, tag truncation, library build, device, or use case is approved.
The course manifest later in this module is deliberately named
`course-audit-only`. Passing its validator proves only that metadata matches one
teaching profile.

Production work therefore records the approving authority, document revision,
profile version, implementation identity, and revalidation date. Standards and
transition guidance change. A copied parameter without that provenance becomes
an unowned security decision.

### Hashes summarize; they do not establish a secret source

A cryptographic hash accepts a message of arbitrary allowed length and returns
a fixed-length digest. FIPS 180-4 specifies the SHA-2 family, including
SHA-256. The relevant goals are:

- **preimage resistance:** given a digest, finding a matching message is
  computationally infeasible within the stated model;
- **second-preimage resistance:** given one message, finding a different
  message with the same digest is computationally infeasible; and
- **collision resistance:** finding any two different messages with the same
  digest is computationally infeasible.

These are computational claims, not impossibility claims. Because a digest has
fixed length and the message space is larger, collisions must exist. The claim
is that finding one is infeasible for the approved parameters and threat model.

An unkeyed digest can detect accidental change when the expected digest arrives
through a trusted channel. It cannot authenticate an attacker-controlled
download if the attacker can replace both file and digest. It is also not a
password-storage scheme: fast evaluation helps an offline guesser.

Serialization is part of the hashed message. Hashing ambiguous concatenations
such as `user || amount` without lengths, types, or a canonical encoding can
make different field sequences produce the same bytes before the hash is even
called. Define one bounded encoding, version it, reject non-canonical inputs,
and test the byte sequence.

### MACs authenticate to parties that share a key

A message authentication code takes a secret key and a message and produces a
tag. HMAC, specified by FIPS 198-1 and used in many RFCs, combines a hash with a
defined keyed construction. It is not “hash(key || message),” and learners
should not replace it with such a concatenation.

The sender computes a tag over the exact framed message. The receiver
recomputes it with the corresponding key and verifies it before acting on the
message. Verification needs all of these invariants:

- the key is for this MAC purpose and not reused as an encryption key;
- both sides authenticate identical, unambiguous bytes and the same domain;
- the tag length follows the versioned profile;
- comparison uses a library operation intended for digest comparison, such as
  Python's `hmac.compare_digest`; and
- a malformed or incorrect tag produces rejection with no authenticated action.

A MAC does not hide the message. It also does not provide non-repudiation among
key holders: any holder of the shared MAC key could have generated a valid tag.
Do not call an HMAC tag a signature.

The supplied example returns a full 32-byte HMAC-SHA-256 tag inside its lab
contract. It rejects other tag lengths before `compare_digest`. That rule is a
course rule, not a claim that every protocol must use the same representation.
A production profile must define whether truncation is allowed and analyze its
forgery bound and attempt limits.

### Password KDFs and general KDFs solve different input problems

A human password usually has far less entropy than a uniformly generated
cryptographic key. An attacker who obtains a password verifier can enumerate
likely passwords offline. A password KDF combines each candidate with a public,
usually unique salt and an intentionally costly profile so each guess consumes
time and, for memory-hard designs, memory.

The salt is not a password and not a secret. Its central job is to make equal
passwords use different computations and to defeat one precomputed table across
many records. A salt does not make a weak password strong. A pepper, when a
system uses one, is a separate secret with a separate storage and rotation
problem; it is not a replacement for a salt.

NIST SP 800-132 specifies PBKDF2-based password derivation for storage
applications. RFC 9106 specifies Argon2 and includes Argon2id password-hashing
profiles. Selection is a deployment decision: use the current organizational
and platform profile, benchmark defender latency and memory, store the
algorithm and cost parameters with the verifier, bound resource consumption,
and plan migration when the profile changes.

Python 3.11's standard library exposes `hashlib.pbkdf2_hmac` but not Argon2.
The module wrapper deliberately accepts only 1 through 50,000 iterations so
boundary tests finish quickly. Values in that interval, including its maximum,
are **not production recommendations**. The function demonstrates API shape
and validation only. Production code should use a maintained password-storage
facility and a deployment-owned profile, not copy the lab constant.

A general KDF begins with secret keying material, often a shared secret or
other input with significant entropy, and derives purpose-specific keys. RFC
5869 defines HKDF's extract-then-expand structure. Its `salt` assists
extraction; its `info` binds application and context to expansion. HKDF does
not make a human password expensive to guess. PBKDF2 or Argon2 should not be
silently substituted for a protocol's specified HKDF either.

Keep these operations distinct:

- **generation** obtains a new unpredictable key from an approved random source;
- **password derivation** raises the cost of guesses against a low-entropy input;
- **extraction** converts suitable input keying material into a pseudorandom key;
- **expansion** derives one or more bounded, labeled keys from suitable keying
  material; and
- **rotation** replaces a key and updates identifiers, state, and lifecycle.

No KDF creates entropy that was absent from its inputs. Output length is not an
entropy meter.

### AEAD has an all-or-failure opening contract

RFC 5116 models authenticated encryption with associated data using two
operations. Conceptually:

~~~text
seal(key, nonce, plaintext, aad) -> ciphertext_and_tag
open(key, nonce, ciphertext_and_tag, aad) -> plaintext OR authentication failure
~~~

The nonce and AAD normally travel openly. The plaintext is confidential. The
tag binds the ciphertext and AAD to the key, nonce, algorithm, and defined
format. AAD is **authenticated but not encrypted**; typical AAD includes a
protocol version, record type, sender or stream identifier, and sequence
number that the receiver needs before decryption.

On opening, the interface must not return unauthenticated plaintext. A tag
failure, wrong nonce, wrong AAD, wrong key, corrupted ciphertext, or unsupported
version all lead to rejection. Internally useful diagnostics should not turn
into an oracle that reveals sensitive distinctions to an attacker. Bound input
sizes before expensive work, use one externally safe failure class where the
protocol requires it, rate-limit abusive paths, and keep only non-sensitive
operational evidence.

AEAD does not automatically prevent replay. A valid old record may still have
a valid tag. Sequence numbers, windows, database state, or idempotency rules
must enforce the protocol's freshness claim, and the relevant identifier must
be bound into AAD or the nonce construction.

### A nonce is not a secret, but reuse can be catastrophic

A nonce is a value used once under the scope defined by the algorithm and
profile. For GCM and ChaCha20-Poly1305, repeating a nonce with the same key can
destroy confidentiality and/or authentication guarantees. RFC 8439 explicitly
requires a different 96-bit nonce for each invocation with the same
ChaCha20-Poly1305 key. NIST SP 800-38D defines GCM IV requirements.

“Generate 12 random bytes” is not a complete uniqueness design. A review asks:

- What is the nonce's exact key scope?
- Is it a counter, a partitioned sender/counter value, or a profile-approved
  random construction with a quantified collision budget?
- How does it survive restart, rollback, backup restore, and clone creation?
- How do concurrent writers reserve disjoint values?
- What prevents counter wrap and enforces message limits?
- Does rotation reset state only after a genuinely different key is active?

Nonce reuse is not repaired by making the nonce secret, appending a timestamp,
or hoping collisions are rare. A system that cannot maintain the selected
mode's invariant needs a different approved construction or architecture,
chosen by qualified reviewers.

Tags are also normally non-secret. Their length affects forgery probability and
must be fixed by the profile. Never accept a caller-selected tag length, compare
only a prefix unless the profile requires that exact truncation, or continue
with plaintext after failure.

### Domains and keys separate purposes

One protocol often needs record encryption, audit-message authentication,
export protection, and password verification. Reusing a key for multiple
purposes couples analyses and can enable cross-protocol attacks. Use independent
keys or derive separate keys under a reviewed KDF with distinct output labels.
Record each key's purpose, algorithm, scope, creation version, and rotation
state. A human-readable key identifier is metadata; it is not the key.

Domain separation ensures that the bytes for one role cannot be accepted as
another role. Examples include:

- an HKDF `info` label such as `application/record-aead/key/v1`;
- an HMAC input prefix such as `application/audit-event/v1`; and
- AAD containing the protocol name, version, record type, and stream identity.

Labels must be distinct, stable, encoded exactly, and bound to an unambiguous
serialization. Changing punctuation, case, Unicode normalization, field order,
or version changes the byte string. “The strings look different” is not enough;
tests should compare the actual bytes and reject unknown domains.

Domain separation does not rescue key reuse that a standard forbids. It is one
part of a construction, not permission to ignore the primitive's key rules.

### Prefer a standardized composition and a misuse-resistant API

Legacy designs sometimes combine encryption and a MAC. The safe order,
framing, keys, and verification semantics depend on a proven construction. A
common high-level rule is encrypt-then-MAC with separate keys and verification
before decryption, but that sentence is not a complete protocol specification.
Padding, length framing, algorithm negotiation, tag scope, error channels, and
replay still matter. New designs should prefer an approved AEAD exposed through
a high-level library API rather than composing primitives locally.

Do not:

- use ECB as a record-encryption scheme;
- use a stream cipher or counter mode twice with the same key/nonce pair;
- treat `hash(key || message)` as HMAC;
- authenticate plaintext in one parser and decrypt a differently framed record;
- use the same key for AEAD and a separate HMAC;
- release plaintext and check the tag afterward;
- fall back from tag failure to unauthenticated data;
- use HKDF as a password hasher; or
- write a new cipher, mode, padding scheme, or AEAD for production.

Cryptography is only one trust boundary. Authorization, input parsing, memory
safety, side-channel behavior, rollback protection, key custody, backups,
observability, incident response, and dependency updates remain system work.

### A manifest makes reviewable decisions explicit

The [protocol manifest example](examples/protocol_manifest.py) accepts exactly
one non-secret teaching schema. It records:

- the schema and course-only deployment profile;
- distinct domain labels for AEAD AAD, HKDF `info`, and audit HMAC input;
- distinct key identifiers for record AEAD, audit MAC, and password verifier;
- an AES-256-GCM review profile with a 96-bit nonce, 128-bit tag, nonce
  uniqueness rule, and reject-before-plaintext policy;
- HKDF-SHA-256 applied to high-entropy shared-secret input, not a password;
- PBKDF2-HMAC-SHA-256 whose actual work factor belongs to deployment policy;
  and
- full-length HMAC-SHA-256 for a separately keyed audit purpose.

The validator rejects missing and extra fields, unknown algorithms, reused key
labels, reused domains, changed sizes, a low-entropy HKDF source label, and
unsafe failure wording. This is useful evidence that the manifest is complete
and internally consistent under its exact schema. It does **not** validate AES,
implement GCM or HKDF, allocate nonces, test a library, certify a module, prove
side-channel resistance, or approve a deployment.

The [bounded mechanics example](examples/crypto_mechanics.py) similarly wraps
`hashlib.sha256`, `hmac.new`, `hmac.compare_digest`, and
`hashlib.pbkdf2_hmac`. It accepts exact byte strings, rejects Boolean counts,
bounds all work, and never writes or prints inputs. Those choices make the lab
reproducible. They do not establish secure erasure, process isolation,
constant-time execution, real key custody, or production password parameters.

## Worked example

From the repository root, run:

~~~sh
cd curriculum/modules/cry-102
PYTHONDONTWRITEBYTECODE=1 python3 examples/worked_review.py
PYTHONDONTWRITEBYTECODE=1 python3 checks/lab_smoke.py
~~~

The worked program checks three fixed public regression cases and the course
manifest. It prints only pass labels and the explicit statement that no cipher
or AEAD implementation is included. It never prints a key, password, digest,
tag, or derived value.

The SHA-256 case uses the standard `abc` digest. The HMAC-SHA-256 case is RFC
4231 test case 1 with published test bytes. The PBKDF2 case is a module-local
regression value using public labels and one iteration; one iteration is useful
only for checking mechanics and is not a deployment setting. The smoke check
also exercises exact endpoints, oversized and wrong-type inputs, message and
tag modification, manifest policy violations, duplicate domains and key
labels, and unexpected key-material fields.

A successful final line is exactly:

~~~text
cry-102 lab smoke: PASS
~~~

That line establishes the bounded Python behavior checked on this run. It does
not establish the security or compliance of any production cryptosystem.

## Check your understanding

1. Why can an attacker replace both a file and its unkeyed hash, and what
   additional trust channel or keyed mechanism changes that threat?
2. What security service does a MAC provide, and why is it not a digital
   signature among parties sharing the key?
3. Distinguish a password KDF salt, an HKDF salt, HKDF `info`, and an AEAD nonce.
4. What breaks when one AEAD key/nonce pair is used for two records?
5. Why must AAD be serialized and versioned even though it remains visible?
6. What should an AEAD opening API return when the tag is wrong, and when may
   the caller use plaintext?
7. Why is a course-accepted algorithm manifest not proof of production
   approval or implementation correctness?
8. Give three independent purposes that need separate keys or derivation
   labels, and state where each label is bound.
9. Why is the lab PBKDF2 maximum not a recommendation? What evidence is needed
   to select a real password-storage profile?
10. Which replay property remains outside AEAD, and how could a protocol bind
    the relevant state to a protected record?

## Next step

Complete the lab and independent assessment with public data only. Preserve a
claim/assumption/exclusion table and an exact manifest diff for each rejected
case. After passing, continue to `cry-103`, which introduces public-key
cryptography, signatures, and key establishment. Do not carry a symmetric
shared-key authentication claim into a signature claim without reanalyzing the
participants and trust model.

## Sources

These are primary standards and official API references. A deployment must
recheck current status, transition notes, applicable authority, and its own
approved profile rather than treating this source list as a procurement list.

- [FIPS 197, Advanced Encryption Standard, updated 2023](https://csrc.nist.gov/pubs/fips/197/final) defines AES-128, AES-192, and AES-256 as block ciphers.
- [FIPS 180-4, Secure Hash Standard](https://csrc.nist.gov/pubs/fips/180-4/upd1/final) specifies the SHA-2 hash family; its official page records NIST's revision plan.
- [FIPS 198-1, The Keyed-Hash Message Authentication Code](https://csrc.nist.gov/pubs/fips/198-1/final) specifies HMAC; its official page records NIST's transition planning.
- [NIST SP 800-38D, GCM and GMAC](https://csrc.nist.gov/pubs/sp/800/38/d/final) specifies GCM authenticated encryption and GMAC; its page records an active revision process.
- [NIST SP 800-57 Part 1 Revision 5, Recommendation for Key Management](https://csrc.nist.gov/pubs/sp/800/57/pt1/r5/final) supplies general key-management guidance.
- [NIST SP 800-132, Password-Based Key Derivation for Storage Applications](https://csrc.nist.gov/pubs/sp/800/132/final) specifies PBKDF2-based derivation for its stated storage scope and records a planned revision.
- [NIST SP 800-56C Revision 2, Key-Derivation Methods in Key-Establishment Schemes](https://csrc.nist.gov/pubs/sp/800/56/c/r2/final) distinguishes extraction and expansion for its key-establishment scope.
- [RFC 5116, An Interface and Algorithms for Authenticated Encryption](https://www.rfc-editor.org/rfc/rfc5116.html) defines the AEAD interface, nonce inputs, and authenticated-decryption failure model.
- [RFC 5869, HMAC-based Extract-and-Expand Key Derivation Function](https://www.rfc-editor.org/rfc/rfc5869.html) defines HKDF, including `salt` and `info` roles.
- [RFC 8439, ChaCha20 and Poly1305 for IETF Protocols](https://www.rfc-editor.org/rfc/rfc8439.html) defines ChaCha20-Poly1305 AEAD and its 96-bit nonce uniqueness requirement.
- [RFC 9106, Argon2 Memory-Hard Function](https://www.rfc-editor.org/rfc/rfc9106.html) specifies Argon2 and password-hashing profiles.
- [RFC 4231, Identifiers and Test Vectors for HMAC-SHA](https://www.rfc-editor.org/rfc/rfc4231.html) supplies the public HMAC-SHA-256 regression vector used by the example.
- [Python 3.11 `hashlib` documentation](https://docs.python.org/3.11/library/hashlib.html) documents `sha256` and `pbkdf2_hmac`.
- [Python 3.11 `hmac` documentation](https://docs.python.org/3.11/library/hmac.html) documents HMAC and `compare_digest`.
