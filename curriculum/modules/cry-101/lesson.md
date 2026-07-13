# Cryptographic goals and attacker models

Cryptography begins with a claim, not an algorithm name. A useful claim says
which asset is protected, which property is required, what an attacker may do,
which assumptions and trust boundaries the claim depends on, and what happens
when a premise fails. Without that frame, even a correctly implemented
primitive can solve the wrong problem.

This module does not design or implement a cipher, hash, signature, random-bit
generator, or protocol. Its Python example is a bounded requirements checker.
It can expose missing declarations and broken references; it cannot prove a
construction secure or approve a deployment.

## Learning objectives

- **CRY-101-01:** State an asset-specific cryptographic goal, an attacker model,
  and a security-game-style notion with explicit capabilities, resources,
  exclusions, success event, and evidence limits.
- **CRY-101-02:** Distinguish keys, nonces, and security randomness while
  documenting assumptions, trust boundaries, lifetimes, scopes, and failure
  responses.
- **CRY-101-03:** Analyze how cryptographic claims compose with encoding,
  state, key management, and application behavior, then use a bounded
  evaluator without mistaking structural completeness for security.

Together these outcomes provide instruction, practice, and assessment for
**CRY-01: State cryptographic goals, attacker models, assumptions, and security
notions.**

## Prerequisites

Pass <code>mat-101</code> and <code>prg-101</code>. You should be able to read
quantified statements, distinguish proof from testing, reason about sets and
functions, and run a bounded Python 3.11 program with explicit input errors.

Use Python 3.11 or newer and only the standard library. The lesson and lab are
offline. They require no administrator access, external package, secret data,
or network operation.

## Lesson

### Start with an asset and a consequence

An **asset** is something whose loss or misuse matters: plaintext records, a
secret signing capability, a software update decision, an account session, or
the state that says which messages have already been processed. Name the asset
at a useful granularity and state its lifetime. “Data” is too broad; “the
unreleased payroll record while stored in the export queue” can be reviewed.

Then choose the required property. Common goals include:

- **Confidentiality:** specified information is not learned beyond declared
  leakage. Ciphertext length, timing, participant identities, and access
  patterns may remain visible unless the design addresses them.
- **Integrity:** unauthorized modification, insertion, or deletion is detected
  or prevented within a stated scope.
- **Authenticity:** a verifier obtains evidence about an asserted source or
  key holder. Data-origin authentication is not automatically live entity
  authentication, authorization, or human identity.
- **Freshness or replay resistance:** stale but otherwise valid data is not
  accepted where a new event is required. This usually needs protocol state,
  counters, epochs, or challenge handling in addition to cryptography.
- **Availability:** authorized work remains possible. Cryptography can support
  recovery and integrity, but an attacker who can drop every packet can still
  deny a network service.

A goal must name unacceptable outcomes. “Use encryption” is a mechanism
instruction. “An observer of the queue must not learn report contents beyond
encoded length before publication” is a confidentiality requirement with
visible leakage and a time boundary.

Properties can conflict. Rejecting every malformed record protects an
integrity boundary but may let an attacker exhaust service capacity. Erasing a
key can contain exposure but destroy availability if recovery was never
designed. Record the tradeoff instead of hiding it behind the word “secure.”

### Give the attacker powers and limits

An **attacker model** defines the interface against which a claim is made. It
should answer at least these questions:

1. What can the attacker observe: traffic, ciphertexts, lengths, timing,
   errors, storage, logs, or process memory?
2. What can the attacker change: reorder, replay, inject, truncate, roll back,
   or delete data?
3. Can the attacker choose inputs adaptively after seeing earlier outputs?
4. Can the attacker call encryption, decryption, signing, verification, or
   comparison interfaces, and how many times?
5. Can the attacker compromise endpoints, operators, dependencies, build
   systems, or keys? If not, where is that exclusion recorded?
6. What time, memory, query, physical-access, and concurrency bounds apply?

“External attacker” is not enough. A passive observer and an active storage
administrator have different powers. An attacker who can submit chosen inputs
may expose behavior that known-input testing cannot. A side-channel observer
is not represented by a black-box input/output game unless timing, power, cache
state, or faults are explicitly part of the interface.

Exclusions bound a claim; they do not make excluded events harmless. If
endpoint compromise is out of scope, also state how the system detects,
contains, and recovers from it operationally. If denial of service is out of a
confidentiality analysis, availability remains an unsatisfied goal rather than
an implied benefit.

### Mark trust boundaries and assumptions

A **trust boundary** is a crossing where control or confidence changes. Name
the source zone, destination zone, data that crosses, enforcement point, and
failure action. Examples include an application sending bytes into an
untrusted queue, a parser handing fields to a cryptographic library, or a
service asking a platform key store to perform an operation.

The trusted computing base is every component whose failure can invalidate the
claim. Minimize it, but do not pretend it is empty. Correct cryptographic math
does not compensate for a parser that authenticates one byte sequence and
executes another, a logger that writes plaintext, or a key service that grants
the wrong caller access.

An **assumption** is a premise on which the reasoning depends. Useful
assumptions are specific, owned, and falsifiable. Record:

- the statement, such as “the per-key counter survives ordinary restart”;
- who owns it;
- what observation would show it is false; and
- which requirements or composition steps depend on it.

Mathematical assumptions, implementation assumptions, environmental
assumptions, and operational assumptions are different. A reduction may say a
construction is secure if an underlying problem is hard. Deployment reasoning
still depends on correct parameter selection, library behavior, key control,
encoding, state, and error handling.

### Turn a goal into a security game

A security game is a precise experiment between a **challenger** and an
**adversary**. Games make ambiguous phrases such as “cannot read encrypted
data” reviewable. At an introductory level, write the following pieces:

1. **Setup:** how parameters and secret state are created, and what public
   information the adversary receives.
2. **Interfaces:** which operations the adversary may query, whether choices
   are adaptive, and which queries are forbidden.
3. **Challenge:** the event or hidden choice that tests the target goal.
4. **Win event:** the exact Boolean condition for adversary success.
5. **Baseline:** success achievable without the protected information, such
   as random guessing.
6. **Advantage:** how far the win probability exceeds that baseline.
7. **Bounds and quantifiers:** security parameter, time, memory, number and
   size of queries, and the class of adversaries covered.
8. **Assumptions:** the premises under which the advantage is claimed to be
   small.

For a two-choice confidentiality experiment, a challenger might select a
hidden bit, protect one of two equal-length adversary-chosen messages under the
specified interface, and ask the adversary to guess the bit. Equal lengths
avoid giving away the choice through an already-declared length channel. The
game must state whether the adversary has other protection or recovery
interfaces and prohibit a trivial query that simply reveals the challenge.
The baseline is one half; a common advantage expression measures the distance
between actual success and one half.

This sketch is not itself a theorem about a product. A complete definition
fixes syntax, correctness, every interface, and every restriction. A proof is
conditional: for every adversary within the bound, under named assumptions,
the advantage satisfies a named bound. A test run samples a few executions; it
does not establish that quantified statement.

Different goals require different games. Confidentiality does not imply
integrity. An integrity game might count a fresh accepted forgery as a win and
must define what “fresh” means. Replay resistance often depends on a protocol
state machine rather than only a primitive game. Use the definition that
matches the asset and attacker, not whichever definition is easiest to pass.

### Keep keys, nonces, and randomness distinct

These values can all look like byte strings, but their contracts differ.

**Keys** parameterize cryptographic operations. Some keys must remain secret;
public keys are intentionally public but require authentic association with an
identity or policy. State the key type, purpose, generation or derivation
source, owner, access rules, activation time, cryptoperiod or epoch, backup and
recovery policy, rotation, destruction, and compromise response. A key
identifier is not the key material. Reusing one key across unrelated purposes
can create composition risks even when each individual operation is standard.

A **nonce** is a value whose construction-specific contract prevents a
forbidden reuse. It is often public and need not be unpredictable. The scope
matters: many AEAD interfaces require a nonce to be distinct for every
invocation under a fixed key. A counter can meet that requirement only if
allocation is coordinated and state cannot silently roll back. Randomly
sampling a nonce changes a certainty requirement into a collision-probability
argument and is acceptable only when the construction, size, population, and
risk bound support it. Never infer a nonce rule from the field name alone;
read the selected construction's specification.

**Security randomness** is required when a value must resist prediction or
guessing. Separate the entropy source, conditioning, deterministic random-bit
generator, seed and internal state, generated output, and consumer. Statistical
uniformity tests do not establish unpredictability. NIST SP 800-90B addresses
entropy sources; SP 800-90A specifies deterministic generation mechanisms.
RFC 4086 likewise warns that output can look statistically random yet remain
predictable. Use an approved platform facility and applicable standards; do
not build a generator from clocks, process identifiers, or this course's
Python examples.

A value may need more than one property. A freshly generated secret key is
normally both secret and unpredictable. A nonce for a particular use can be
public but unique within a key scope. Random generator output may be
unpredictable without being a nonce until a protocol assigns a uniqueness
rule. Salts, counters, initialization vectors, challenges, and tokens also have
specification-specific contracts and are not interchangeable merely because
they are bytes.

### Composition carries every premise upward

A system claim is a chain:

~~~text
primitive property
  + construction preconditions
  + unambiguous encoding
  + state and replay rules
  + key and randomness lifecycle
  + API use and error behavior
  + endpoint and operational controls
  -> bounded application claim
~~~

Every plus sign is a failure boundary. Authenticated encryption with associated
data (AEAD), for example, is designed to provide confidentiality for plaintext
and authenticity for plaintext plus associated data under its defined
interface. It does not automatically hide associated data or lengths, prevent
replay, authorize a user, protect a compromised endpoint, preserve nonce state
after rollback, or keep a service available when traffic is dropped.

RFC 5116 requires a nonce to be distinct for each authenticated-encryption
invocation with a fixed key. Its discussion of GCM warns that nonce reuse can
damage both confidentiality and integrity. Therefore “we use AEAD” is not a
complete claim. The caller must show how keys and nonces are scoped, how
encoded fields are bound, what happens on authentication failure, and what
state handles replay.

Failure behavior belongs in the design:

- identify which claims no longer hold when an assumption fails;
- stop operations that could worsen exposure;
- avoid releasing unauthenticated plaintext;
- make externally visible errors no more revealing than necessary;
- preserve bounded diagnostic evidence without logging secrets;
- define key revocation, state repair, reprocessing, and notification; and
- record availability and data-loss consequences of failing closed.

“Fail closed” is incomplete unless it says which operation closes, who can
restore service, and how recovery avoids repeating the failure.

### Use structural tools as checklists, not oracles

The [security-requirements example](examples/security_requirements.py) uses
frozen data classes and enums to represent a bounded model. It accepts at most
16 assets, assumptions, trust boundaries, material declarations, and
composition dependencies, and at most 64 requirements. Text fields are at most
400 characters. Exact bounds make accidental unbounded input and review scope
visible.

The evaluator checks:

- duplicate identifiers and broken references;
- whether every declared asset goal has a requirement;
- whether every declared attacker capability is addressed;
- whether assumptions and trust boundaries are linked;
- whether the teaching model states secret-key secrecy and unpredictability,
  nonce uniqueness scope, and randomness unpredictability; and
- whether composition dependencies name a required property and failure
  response.

It does not parse prose for truth. A false assumption can be well formed. A
requirement can cite weak evidence. A clean result does not inspect a library,
verify a standard, prove a reduction, detect a side channel, or authorize
deployment. Human review and later cryptography, systems, and assurance modules
must supply those judgments.

## Worked example

The [sealed-export case](examples/worked_case.py) models one record crossing a
trusted sender, an untrusted queue, and a trusted receiver. Its attacker can
observe, alter, and replay traffic but cannot compromise endpoints. That
exclusion narrows the claim; the model does not declare endpoint compromise
safe.

The record has confidentiality, integrity, and freshness goals. Three separate
requirements address the three attacker capabilities. The model declares a
secret record key, a public per-key-unique nonce, and unpredictable key
generation input. It also links the application claim to two assumptions:
approved AEAD behavior and durable nonce/replay state. The composition edge
says which application claims stop when either premise fails.

From this module directory, run:

~~~sh
PYTHONDONTWRITEBYTECODE=1 python3 -B examples/worked_case.py
PYTHONDONTWRITEBYTECODE=1 python3 -B checks/lab_smoke.py
~~~

The worked program reports zero structural findings and immediately prints the
limitation that this is not a security proof, implementation review, or
deployment approval. Change the nonce's properties to remove
<code>UNIQUE_WITHIN_SCOPE</code>; the evaluator reports
<code>missing-nonce-uniqueness</code>. Restore the declaration before running
the smoke check.

## Check your understanding

1. Rewrite “customer backups are encrypted” as an asset, lifetime,
   confidentiality goal, declared leakage, and failure condition.
2. Why does a passive-observer model not support a claim against an attacker
   who can replace ciphertexts?
3. In a two-choice confidentiality game, why must the win event, baseline, and
   challenge-query restrictions all be explicit?
4. Give one public nonce construction and name the exact scope in which it
   must not repeat. Which state failure could violate that rule?
5. Explain why statistically balanced output can still be predictable.
6. List four application properties that AEAD alone does not supply.
7. What does a zero-finding evaluator result establish? Name four things it
   does not establish.

## Next step

Complete the lab and independent assessment before advancing to
<code>cry-102</code>. That module studies selected primitives and
constructions. Carry this module's discipline forward: every mechanism must be
traced to an asset, attacker, security notion, preconditions, and explicit
failure boundary.

## Sources

The lesson is self-contained. These primary or author-maintained sources define
the standards and formal framing paraphrased above:

- NIST, *Recommendation for Key Management: Part 1 — General*, SP 800-57 Part
  1 Rev. 5 (May 2020):
  <https://csrc.nist.gov/pubs/sp/800/57/pt1/r5/final>. The module uses its
  key-management and security-service framing; it does not claim course
  examples satisfy a NIST deployment policy.
- NIST, *Recommendation for Random Number Generation Using Deterministic Random
  Bit Generators*, SP 800-90A Rev. 1 (June 2015):
  <https://csrc.nist.gov/pubs/sp/800/90/a/r1/final>.
- NIST, *Recommendation for the Entropy Sources Used for Random Bit Generation*,
  SP 800-90B (January 2018, with the errata notice linked by NIST):
  <https://csrc.nist.gov/pubs/sp/800/90/b/final>. The distinction between an
  entropy source and deterministic generation follows the scopes of 90B and
  90A.
- D. Eastlake 3rd, J. Schiller, and S. Crocker, *Randomness Requirements for
  Security*, RFC 4086 (June 2005):
  <https://www.rfc-editor.org/rfc/rfc4086.html>. The lesson uses its distinction
  between statistical appearance and unpredictability.
- D. McGrew, *An Interface and Algorithms for Authenticated Encryption*, RFC
  5116 (January 2008): <https://www.rfc-editor.org/rfc/rfc5116.html>. The AEAD
  interface, fixed-key nonce distinction, and nonce-reuse boundary are
  paraphrased from this standards-track RFC.
- Dan Boneh and Victor Shoup, *A Graduate Course in Applied Cryptography*,
  version 0.6 (January 2023), author-maintained site:
  <https://crypto.stanford.edu/~dabo/cryptobook/>. The game-based vocabulary
  and conditional nature of cryptographic claims follow this text; the module
  presents only an introductory, non-normative sketch.
