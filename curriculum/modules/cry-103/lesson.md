# Public-key cryptography, signatures, and key establishment

Public-key cryptography is not one interchangeable operation. Encryption,
digital signatures, key agreement, and key encapsulation expose different
interfaces and promise different properties under different attacker models.
Professional work begins by naming the required property, authenticating the
right key, selecting a ratified construction and profile, and specifying every
validation and failure boundary. It does not begin by writing a new primitive.

This module contains no production cryptographic implementation. Its Python
examples expose only a tiny, enumerable group and a metadata-only transcript
validator. They exist to make validation and context-binding obligations
auditable; they provide no security.

## Learning objectives

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

## Prerequisites

Pass <code>cry-101</code>, <code>mat-103</code>, and <code>mat-104</code>.
You should be able to state a security goal and attacker model, reason about a
finite prime field, distinguish exact calculation from security evidence, and
analyze probability, collision, and sampling claims. No prior public-key API,
certificate, KEM, or post-quantum experience is assumed.

Use Python 3.11 or newer and only the standard library for the teaching
examples. They run offline and process no credential, private key, seed,
nonce, ciphertext, or other secret material.

## Lesson

### Choose a service before choosing an algorithm

The word “asymmetric” means that an operation uses a related public/private
key pair. It does not identify the service provided.

| Operation | Typical interface | Primary goal | What it does not provide by itself |
| --- | --- | --- | --- |
| Public-key encryption | encrypt to recipient public key; decrypt with recipient private key | Plaintext confidentiality against the construction's declared attacker | Sender identity, replay protection, key authenticity, or transcript agreement |
| Digital signature | sign with signer private key; verify with signer public key | Detect modification and authenticate a signer under an unforgeability model | Confidentiality, freshness, or proof that the verifying public key belongs to the claimed person |
| Key agreement | each party combines local private input with peer public input | Derive shared keying material | Peer authentication, confirmation that both parties derived the same key, or protection of later messages |
| Key encapsulation mechanism (KEM) | key generation; encapsulate to public key; decapsulate with private key | Establish a fresh shared secret plus an encapsulation | Bulk data encryption, public-key authenticity, or application-context binding |

For encryption, a professional requirement might be confidentiality against
an active attacker who can submit modified ciphertexts and observe whether
decryption succeeds. “The attacker cannot factor this modulus” is not a full
protocol claim. Encoding, padding, chosen-ciphertext behavior, key
authentication, and error leakage are also in scope.

For signatures, a common goal is existential unforgeability under chosen
message attack: after obtaining signatures on messages of its choice, the
attacker still cannot produce a valid signature on a new message. Signature
verification is public. It therefore cannot hide the message. A verified
signature establishes origin only relative to the verified public key, the
bytes actually signed, the algorithm/profile, and the trust decision that
associated that key with a signer. Operational claims such as
non-repudiation additionally depend on private-key custody, authorization,
revocation, audit, identity proofing, and applicable policy.

For key establishment, distinguish at least:

- **key agreement**, where both parties contribute inputs;
- **key transport**, where one party selects keying material and protects it
  for another;
- **KEM encapsulation**, where encapsulation returns a shared secret and an
  encapsulated value for a public key; and
- **key confirmation**, evidence that another party possesses the derived
  key, usually provided by a protocol step rather than the primitive alone.

Never substitute one service for another. “Encrypt with a private key” is not
a sound model of signatures. A signature encoding and an encryption encoding
can have different proofs, parsing rules, and failure requirements even when a
standard family historically uses related arithmetic.

### State the attacker and compromise timeline

A security claim needs capabilities and a time horizon. At minimum ask whether
the attacker can:

- only observe traffic, or also intercept, reorder, replay, inject, and adapt
  messages after seeing failures;
- choose messages to be signed, ciphertexts to be opened, public keys, domain
  parameters, or protocol offers;
- replace a directory entry, certificate, trust anchor, or cached key;
- compromise a long-term private key, an ephemeral key, a random generator,
  process memory, or one endpoint; and
- retain encrypted traffic for later cryptanalysis, including a future
  cryptographically relevant quantum computer.

Then name the desired property: confidentiality, integrity, origin
authentication, peer authentication, replay resistance, key confirmation,
forward secrecy, compromise recovery, or some defined combination. For
example, an unauthenticated ephemeral Diffie–Hellman exchange can hide a
derived value from a passive observer while remaining vulnerable to an active
person-in-the-middle. A certificate can authenticate a long-term key but does
not retroactively give forward secrecy to a key-transport design.

The claim belongs to a concrete construction and profile, not to an arithmetic
problem in isolation. Include algorithm identifiers, parameter sets, modes,
key use, message grammar, key lifecycle, and failure behavior in the review.

### A public key is public, not automatically authentic

An attacker may know a public key perfectly and still have supplied the wrong
one. Before encrypting or verifying, the relying party needs a justified
binding between a key and the intended identity, role, service, or endpoint.
Possible mechanisms include a validated certification path, an authenticated
directory, a preconfigured trust anchor, a securely provisioned pin, or an
out-of-band comparison. Each mechanism has a different update and compromise
story.

In the X.509 PKI model, RFC 5280 path validation starts from a locally trusted
anchor and evaluates a candidate chain. A deployment profile must also apply
the intended reference identity and usage. Relevant checks can include:

- certificate signatures and issuer chaining;
- validity time under an explicit clock policy;
- subject alternative name or other profile-specific identity matching;
- basic constraints, path length, key usage, extended key usage, name
  constraints, certificate policy, and unrecognized critical extensions;
- algorithm and parameter policy; and
- revocation or short-lived-certificate policy, including defined behavior
  when status information is unavailable.

Merely parsing a certificate, verifying the leaf signature, accepting any
chain offered by the peer, or observing that a certificate is self-signed is
not path validation. The trust anchor is an input, not a fact discovered from
untrusted traffic. A pin also needs rotation and recovery rules; otherwise an
emergency replacement can become an availability failure or an insecure
bypass.

### Validate parameters, keys, encodings, and outputs

Public input is attacker-controlled input. Validation occurs before an
operation relies on it and follows the exact standard and profile.

For a finite-field subgroup with prime modulus <code>p</code>, subgroup order
<code>q</code>, and generator <code>g</code>, a teaching validation might
check fixed approved parameters, canonical encoding, range, non-identity, and
the subgroup relation <code>y^q mod p = 1</code>. The supplied
[toy group](examples/toy_group.py) fixes
<code>(p,q,g)=(23,11,2)</code>, accepts teaching scalars 1 through 10, and
rejects identity, minus one, and out-of-subgroup public values. Every discrete
log can be recovered by enumeration, so none of these values is secret and no
security conclusion follows.

Real profiles differ. Elliptic-curve validation may require encoded-point,
field, curve, subgroup, and identity checks. RFC 7748 specifies X25519/X448
decoding behavior and discusses checking an all-zero output; RFC 9180 makes
KEM input and output validation part of its KEM profiles. FIPS 203 specifies
ML-KEM's exact encodings, parameter sets, algorithms, and input checking.
Apply the selected document literally through a reviewed implementation. Do
not transplant the toy subgroup predicate to another group, invent a
“reasonable” decoder, or accept a malformed value because one library call
returned bytes.

Validation has several layers:

1. Bound input length before allocation or expensive work.
2. Parse one canonical grammar and reject trailing, duplicate, ambiguous, or
   unknown critical fields.
3. Confirm the selected algorithm and parameter set are allowed for this key
   and service.
4. Validate public and private key encodings and mathematical conditions
   required by the profile.
5. Validate operation output as specified, including prohibited or failure
   values.
6. Continue only after key authenticity and protocol state are established.

Passing key validation does not authenticate the key. Authenticating a key
does not prove its encoding or parameters are valid. Both obligations remain.

### Randomness and nonce rules are algorithm-specific

Randomness can be required for key generation, ephemeral key generation,
encapsulation, randomized signatures, blinding, and protocol nonces. A nonce
may require uniqueness, unpredictability, or both. Those are distinct
properties.

For DSA and ECDSA, the per-message value traditionally called <code>k</code>
must meet exact generation requirements. Reuse or bias can expose the private
signing key. RFC 6979 defines a deterministic generation procedure for DSA
and ECDSA; “deterministic” there does not mean a counter, a fixed value, or an
ad-hoc hash of a key and message. FIPS 186-5 defines approved signature
schemes and generation requirements. Use the mode implemented and validated
for the deployment; do not improvise nonce generation.

For an AEAD, nonce reuse under one key can be catastrophic even if every nonce
is public. For a KEM, encapsulation randomness is internal to the approved
algorithm and implementation. For long-term and ephemeral key generation,
entropy, health testing, state protection, fork behavior, backup, import, and
zeroization can all matter. A test seed is useful for a test vector only when
the standard defines that use. It must never silently enter production key or
nonce generation.

Record the responsibility: which component creates each value, its exact
length and distribution, whether uniqueness or unpredictability is required,
how concurrency and restart are handled, and what happens on generator
failure. “Uses randomness” is not an enforceable requirement.

### Compose a KEM, KDF, and AEAD through a ratified profile

A KEM-style application generally follows this shape:

1. Authenticate and validate the recipient's KEM public key.
2. Encapsulate under that key to obtain an encapsulated value and a fresh
   shared secret, or decapsulate an incoming encapsulated value.
3. Feed the shared secret into the profile's labeled key schedule or KDF,
   together with the required suite and context inputs.
4. Use derived, purpose-separated keys with the profile's AEAD, maintaining
   its nonce state and authenticating the required associated data.
5. On any failure, release no plaintext or derived secret and clear sensitive
   state according to the implementation contract.

Do not use a raw shared group element as an encryption key. Do not concatenate
KEM output, identities, and labels and call the result a key schedule. Do not
pair independently selected algorithms merely because each is approved.
Composition needs a specification with compatible security requirements,
encodings, labels, key lengths, error behavior, and test vectors.

RFC 9180 HPKE is an example of a specified KEM/KDF/AEAD construction. It uses
suite identifiers and labeled extraction/expansion, supplies setup
<code>info</code> and per-operation associated data, validates KEM input and
output, and exposes fallible setup and open operations. Here “hybrid public
key encryption” means combining asymmetric key establishment with symmetric
encryption; it does not by itself mean a classical-plus-post-quantum combiner.
An application adopting HPKE still has to define its wire encoding, key
authentication, mode, suite policy, information and associated-data contents,
message ordering, and state lifecycle.

### Bind the transcript, identities, roles, and purpose

An attacker should not be able to move a valid artifact into a different
protocol, role, version, peer pair, or negotiation. The bytes covered by a
signature, KDF context, key-confirmation MAC, or AEAD associated data therefore
need unambiguous framing and domain separation.

A protocol specification should decide whether to bind:

- protocol name and version;
- construction, mode, and complete algorithm/parameter identifiers;
- offered and selected profiles, so deleting a stronger offer cannot produce
  an unnoticed downgrade;
- initiator and responder roles and authenticated key identifiers;
- both public keys and the encapsulated value when the construction requires
  them;
- the ordered, canonically encoded handshake transcript;
- application purpose, channel, session identifier, and exported-key label;
  and
- message sequence numbers or replay state.

TLS 1.3 demonstrates the pattern: its CertificateVerify signatures use a
role-specific context string and a transcript hash, and Finished authenticates
the handshake transcript under derived keying material. That example is a
reason to follow a complete protocol specification, not permission to copy
one TLS field into a new design.

The supplied [protocol record validator](examples/protocol_record.py) accepts a
fixed metadata profile, exact field set, bounded ASCII identifiers, distinct
peer key identifiers, one bound offer, ordered public messages, a lowercase
SHA-256 record hash, and fixed public failure and nonce requirements. It
length-prefixes every field in a fixed order. It performs no KEM, KDF, AEAD,
signature, certificate validation, or secret processing. Its output is merely
candidate public context bytes for review; hashing public metadata does not
authenticate it.

### Make failure behavior part of the protocol

Every public-key operation is fallible. Failure categories include malformed
encoding, unsupported profile, invalid key, invalid encapsulation, signature
failure, certificate-path failure, expired or revoked credential, AEAD tag
failure, replay, state exhaustion, random-generator failure, and internal
resource failure.

Define both internal handling and the external observation. A robust boundary
normally:

- bounds and validates before performing expensive or state-changing work;
- treats unauthenticated plaintext and derived values as unavailable until
  the entire operation succeeds;
- commits state only after verification, or rolls it back safely;
- exposes one profile-defined public rejection where detailed distinctions
  could become an oracle;
- does not retry with weaker algorithms, skip certificate checks, or return
  partial plaintext;
- limits logs to non-secret operational facts with controlled access; and
- considers timing, memory access, cache behavior, power, faults, and resource
  consumption, not only exception text.

“Catch every exception” is not a cryptographic failure policy. Some KEMs define
decapsulation behavior that deliberately avoids exposing validity details.
Some protocol layers require a connection abort. Follow the exact primitive
and protocol specifications and the reviewed library contract. Tests should
cover invalid inputs and stable public behavior, but ordinary Python timing is
not evidence of constant-time execution.

### Plan the full key lifecycle

Keys need authorized generation, provenance, storage, access control, usage
constraints, activation, rotation, archival or destruction, compromise
response, and audit. Separate signing, decryption, key establishment, test,
and production keys. Enforce algorithm, parameter, role, and purpose at the
key-management boundary, not only in caller prose.

NIST SP 800-57 Part 1 gives general key-management guidance and distinguishes
key types and security services. A professional design also identifies trust
anchors, cryptoperiods, certificate renewal, revocation, backup and recovery,
hardware or service boundaries, deployment ownership, monitoring, and an
emergency disable path. A cryptographically strong primitive cannot rescue an
exported private key or an unauthenticated key directory.

### Migrate to post-quantum profiles without inventing a combiner

FIPS 203 specifies ML-KEM; FIPS 204 specifies ML-DSA. They are different
services and are not drop-in names for every existing protocol field. A
migration inventory should locate algorithms, parameter sets, keys,
certificates, libraries, hardware, firmware, wire formats, stored data,
signatures with long verification lifetimes, trust anchors, dependencies, and
owners. Prioritize information exposed to “harvest now, decrypt later” risk
and artifacts that must remain verifiable for years.

Migration work includes:

1. Pin the exact standard edition, errata decision, implementation, module
   validation requirements, and application profile.
2. Measure public-key, ciphertext/encapsulation, signature, certificate,
   handshake, memory, latency, and bandwidth changes at real boundaries.
3. Update authentic key distribution, negotiation, transcript binding,
   storage, observability, rollback, and incident procedures.
4. Test interoperability, known-answer vectors, malformed inputs, downgrade,
   mixed-version fleets, failure behavior, and recovery.
5. Stage deployment with an explicit retirement condition for old profiles;
   indefinite “temporary” compatibility is not a migration.

A **hybrid migration mode** often means combining classical and post-quantum
components so the result can retain a stated property if at least one component
remains secure. The combiner, authentication, labels, encoding, failure rule,
and downgrade policy are security-critical. Concatenating two shared secrets,
accepting success from either signature, or negotiating whichever algorithm
parses is not a justified hybrid. Use a standards-defined or otherwise
ratified deployment profile with an analyzed combiner and interoperable test
evidence.

Crypto agility means being able to inventory, replace, and adapt algorithms
while preserving security and operations. It does not mean arbitrary runtime
algorithm choice. NIST CSWP 39upd1 discusses agility strategies; NIST SP
800-227 gives current KEM usage recommendations. The FIPS 203 source page also
publishes an errata notice, so edition and errata tracking are live
professional obligations.

## Worked example

Inspect the [tiny group](examples/toy_group.py), [strict public record
validator](examples/protocol_record.py), and [worked
case](examples/worked_case.py). Then run:

~~~sh
cd curriculum/modules/cry-103
PYTHONDONTWRITEBYTECODE=1 python3 examples/worked_case.py
PYTHONDONTWRITEBYTECODE=1 python3 checks/lab_smoke.py
~~~

The worked case maps public teaching scalars 3 and 7 to subgroup values 8 and
13 and obtains the same enumerable value 12 on both sides. It then hashes
three public transcript messages and encodes every validated metadata field.
The smoke check also rejects identities, out-of-subgroup values, wrong types,
unknown or missing record fields, a changed transcript, a changed profile,
ambiguous peer identities, and values outside exact bounds.

This evidence supports only the claimed Python validation mechanics. It does
not demonstrate confidentiality, signature unforgeability, KEM correctness,
entropy, key authenticity, PKI validation, side-channel resistance, Orange
behavior, or conformance to any cited standard.

## Check your understanding

1. Why does encryption to a public key not authenticate the sender? Why does a
   valid signature not hide its message?
2. Give one passive and three active attacker capabilities relevant to a key
   establishment protocol. Which additional steps defeat a person-in-the-middle?
3. Separate mathematical key validation from public-key authenticity. Give a
   failure that each check catches and one that it cannot catch.
4. Why can a repeated or biased ECDSA per-message value expose a private key?
   Why is “replace it with a counter” not an acceptable repair?
5. Name six fields that should be bound into a key schedule or signed
   transcript. Which downgrade becomes possible if offered algorithms are
   omitted?
6. Why must a KEM shared secret pass through a specified key schedule before
   AEAD use? What remains outside a bare KEM's guarantees?
7. What is ambiguous about the word “hybrid” in HPKE and post-quantum
   migration discussions?
8. Why can detailed decapsulation or decryption errors become an oracle? What
   operational evidence can still be retained safely?
9. List four PKI path or application checks beyond parsing the leaf
   certificate.
10. Explain why the supplied transcript hash and toy agreement value are not
    cryptographic security evidence.

## Next step

Complete the lab in a fresh temporary directory. Preserve the threat model,
profile decision, validation matrix, transcript schema, negative tests, public
failure contract, and migration plan as separate evidence. The next module,
<code>cry-104</code>, turns standards, errata, provenance, and vectors into a
traceable professional validation workflow.

## Sources

These are primary standards and recommendations. Record the publication status,
edition, errata, and deployment profile actually used; a URL alone is not a
conformance claim.

- [NIST FIPS 186-5, Digital Signature Standard (final, 2023)](https://csrc.nist.gov/pubs/fips/186-5/final)
- [NIST SP 800-56A Revision 3, pair-wise discrete-log key establishment (final, 2018; update announced in 2026)](https://csrc.nist.gov/pubs/sp/800/56/a/r3/final)
- [NIST SP 800-57 Part 1 Revision 5, key management (final, 2020)](https://csrc.nist.gov/pubs/sp/800/57/pt1/r5/final)
- [NIST FIPS 203, ML-KEM (final, 2024; source page carries an errata notice)](https://csrc.nist.gov/pubs/fips/203/final)
- [NIST FIPS 204, ML-DSA (final, 2024)](https://csrc.nist.gov/pubs/fips/204/final)
- [NIST SP 800-227, Recommendations for Key-Encapsulation Mechanisms (final, 2025)](https://csrc.nist.gov/pubs/sp/800/227/final)
- [NIST CSWP 39upd1, Considerations for Achieving Crypto Agility (final, updated 2026)](https://csrc.nist.gov/pubs/cswp/39/upd1/considerations-for-achieving-crypto-agility/final)
- [RFC 5280, Internet X.509 PKI Certificate and CRL Profile](https://www.rfc-editor.org/rfc/rfc5280.html)
- [RFC 6979, Deterministic DSA and ECDSA](https://www.rfc-editor.org/rfc/rfc6979.html)
- [RFC 7748, Elliptic Curves for Security](https://www.rfc-editor.org/rfc/rfc7748.html)
- [RFC 8446, TLS 1.3](https://www.rfc-editor.org/rfc/rfc8446.html)
- [RFC 9180, Hybrid Public Key Encryption](https://www.rfc-editor.org/rfc/rfc9180.html)
