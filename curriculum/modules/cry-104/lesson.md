# Standards, errata, provenance, and vectors

A cryptographic result is useful only when its meaning can be reconstructed.
“The tests passed” omits which standard, revision, corrections, inputs,
implementation, environment, and claim were tested. This module turns those
missing nouns into an offline evidence chain.

The worked code does not implement a hash function. It validates a small,
course-maintained vector bundle and invokes Python's existing SHA-256
implementation. Passing those vectors is useful regression evidence; it is not
a proof, a CAVP certificate, a FIPS 140 module validation, or a deployment
approval.

## Learning objectives

- **CRY-104-01:** Classify a standards source, its exact version and status,
  normative language, updates, and errata, then extract atomic requirements
  with stable locations.
- **CRY-104-02:** Preserve standards and vector provenance with bounded
  manifests, content digests, review context, and explicit authenticity limits.
- **CRY-104-03:** Execute positive and negative vectors reproducibly, retain
  failure evidence, and scope claims to what the vectors actually establish.

## Prerequisites

Pass <code>cry-102</code>, <code>cry-103</code>, and <code>cmp-102</code>. You
should be able to distinguish primitive goals, use exact bytes and hexadecimal,
read a Git revision and diff, run Python tests, and explain why an authenticated
construction has requirements beyond its underlying primitive.

Use Python 3.11 or newer and only the standard library. All supplied artifacts
are local. No network, account, administrator access, cryptographic key, or
external package is needed.

## Lesson

### The evidence chain has distinct links

Use this sequence:

~~~text
source identity -> interpreted requirements -> acquired artifact
  -> provenance record -> vector schema -> implementation run
  -> retained result -> bounded claim
~~~

Each arrow is a possible failure. A genuine document can be misread. A correct
requirement can be encoded into the wrong byte order. An authentic vector can
be run against the wrong algorithm. A correct result can be reported as a much
larger claim than it supports.

Do not collapse these links into one “compliant” Boolean. Preserve enough
evidence to locate the first unsupported transition.

### Identify authority before interpreting text

A usable source record includes at least:

- publisher and document series or repository owner;
- exact title, number, revision, publication date, and status;
- stable URL or repository path plus immutable revision when available;
- the section, table, algorithm profile, and parameter set in scope;
- documents that update, obsolete, or constrain it;
- errata state and the date that state was observed;
- acquisition date and a digest of the acquired local artifact; and
- who reviewed the interpretation and in which repository revision.

For this lesson, the algorithm specification is **FIPS 180-4, Secure Hash
Standard**, updated final publication dated August 2015. Its publication page
also carries a March 2023 planning note that NIST decided to revise it. A
planning note does not itself replace the final algorithm text. Record both
facts; do not silently treat a future revision as published.

The NIST CAVP Secure Hashing page is a different source. It describes testing
requirements and supplies response files. NIST explicitly characterizes its
published vectors as useful for informal correctness checks and says using
them does not replace CAVP validation. That limitation must survive into every
result derived from them.

### Separate standard, profile, protocol, and validation program

“SHA-256” may refer to several layers:

- FIPS 180-4 specifies the hash algorithm;
- another standard or protocol selects SHA-256 for a particular purpose;
- a profile restricts parameters, encodings, operational environments, or
  lifecycle dates;
- test-vector material gives particular input/output examples;
- CAVP evaluates algorithm implementations under its program; and
- CMVP evaluates cryptographic modules under a different boundary and set of
  requirements.

Evidence at one layer does not automatically satisfy another. A SHA-256 vector
match says nothing by itself about HMAC key handling, an AEAD nonce policy, a
signature encoding, side-channel behavior, module boundaries, or operational
approval.

### Read normative words in their declared context

RFC 8174 updates the BCP 14 convention: its defined requirement meanings apply
to the listed words only when the document invokes BCP 14 and the words appear
in uppercase. Lowercase “must” keeps its normal English meaning under that
convention. Normative text can also exist without BCP 14 words.

For every extracted statement, record:

1. a local requirement ID;
2. exact source and location;
3. subject and operation;
4. preconditions and parameter domain;
5. required result or prohibited behavior;
6. requirement strength and why it has that strength;
7. failure behavior;
8. verification method; and
9. unresolved interpretation questions.

One sentence can contain several requirements. Split them so that one failing
test maps to one precise obligation. Preserve exact quoted text only when
licensing and quotation limits permit it; otherwise paraphrase and retain the
stable location.

### Treat errata as stateful evidence

RFCs do not change after publication. The RFC Editor keeps errata separately.
Its current status model includes Reported, Verified, Rejected, and Held for
Document Update. A report is not automatically a correction. A rejected item
can explain why an appealing interpretation is wrong; a held item can still
matter to a future revision.

An errata record therefore needs the RFC number, erratum ID, type, status,
affected format and section, observed date, and your disposition. Record “no
listed errata found as of date X” only after a defined search, never as an
eternal fact. Recheck when refreshing a standards profile.

When one document obsoletes another, start from the newer document and follow
its declared relationship. RFC 8439, for example, says it obsoletes RFC 7539
and incorporated filed errata. That is stronger evidence than silently
patching an old local copy.

### A digest is identity evidence, not source authentication

The supplied [provenance manifest](examples/provenance.json) records a path,
SHA-256 digest, publisher, source title and URL, retrieval date, and scope
statement. The [harness](examples/vector_harness.py) enforces:

- schema version 1 and exact allowed keys;
- unique bounded identifiers and no duplicate JSON keys;
- 1 through 100 artifacts and 1 through 1,000 vectors;
- relative contained artifact paths, including resolved-path containment;
- lowercase 64-hex digests;
- regular local files captured once with a hard 1,000,000-byte read bound;
- lowercase, even-length hexadecimal inputs;
- 32-byte SHA-256 expected digests; and
- decoded messages no larger than 1,000,000 bytes.

A matching digest establishes that the captured bytes match the bytes named by
that manifest. Vector parsing and execution use that same immutable byte
capture, so a later path change cannot substitute unverified input. The digest
does not establish who authored either file. If an attacker can
replace the artifact and the adjacent manifest, both can agree on malicious
bytes. Stronger provenance needs an authenticated, reviewed, or independently
pinned manifest channel: for example an approved signed release, protected Git
revision, transparency record, or independently recorded digest. The trust
root and verification policy must be named, not implied.

### Test-vector schema is part of the requirement

A vector is not merely a pair of strings. Its record needs:

- algorithm and variant;
- input encoding and bit or byte length;
- every key, nonce, associated-data, context, salt, and parameter field the
  algorithm consumes;
- expected output and whether it is full or truncated;
- source identity and vector or case ID; and
- whether success, rejection, or a specific failure is expected.

Hex text is a representation of bytes, not the bytes themselves. Odd-length
hex, mixed case where canonical lowercase is required, dropped leading zeroes,
Unicode text conversion, endianness, bit-oriented messages, and truncated
outputs can all change the case. Validate the schema before running the
primitive.

The course bundle is byte-oriented only. It must not be used to claim support
for NIST's bit-oriented cases.

### Positive and negative evidence answer different questions

A positive vector asks whether one expected input produces one expected
output. A negative test asks whether malformed input, an altered expected
result, a duplicate identifier, an untrusted path, a wrong digest, or an
authentication failure is rejected.

For cryptographic interfaces, failure behavior is part of the contract. A
runner that skips malformed vectors, normalizes ambiguous input, reports zero
cases as success, or continues after provenance failure can manufacture green
evidence.

Preserve at least one deliberate-failure run. Restore the vector and preserve
the later passing run. This proves the harness can notice the class of error
being claimed. It does not prove absence of all harness faults.

### Bound the resulting claim

After a run, separate these claim levels:

- **observed:** named cases produced named results in a named environment;
- **regression evidence:** the implementation still matches those cases;
- **conformance evidence:** a defined requirements set has broader evidence;
- **program validation:** an authorized program issued a result for an exact
  implementation and operational environment; and
- **system assurance:** the deployed composition, lifecycle, and threat model
  support a scoped security claim.

The supplied run supports only the first two. Vectors alone do not cover all
inputs, prove an algorithm, establish constant-time execution, validate key
management, identify the binary that a user deployed, or authorize a product
claim.

### Reproducibility includes failures and environment

A useful run record contains:

- source and manifest digests;
- repository revision and dirty-state description;
- Python implementation and version;
- operating system and architecture when relevant;
- exact command, working directory, environment controls, stdout, stderr, and
  immediate exit status;
- case counts, identifiers, skipped-case count, and per-case verdicts;
- the deliberate mutation and its nonzero result; and
- the smallest claim justified by the evidence.

Archive the source record, requirement matrix, vector bytes, manifest, harness,
and result together. A screenshot without input artifacts is not replayable.

### Connection to Orange journey J-02

Orange journey J-02 eventually turns an external standard into an admitted,
versioned specification. This general module teaches the intake evidence for
that workflow. At the pinned pre-alpha Orange revision, the admitted-
specification capability is not implemented. Completing CRY-104 does not claim
that an Orange specification was created or accepted.

## Worked example

The local evidence set has three layers:

1. <code>vectors/sha256.json</code> identifies FIPS 180-4, the exact NIST CAVP
   byte-vector ZIP plus response member and their digests, and the exact NIST
   SHA-256 example PDF plus its digest and page coordinates. Each of its three
   cases names one of those source artifacts and an exact location.
2. <code>provenance.json</code> pins the exact vector-file bytes with SHA-256
   and retains source and scope fields.
3. <code>vector_harness.py</code> validates the manifest and schema before
   invoking <code>hashlib.sha256</code>.

Run:

~~~sh
cd curriculum/modules/cry-104
PYTHONDONTWRITEBYTECODE=1 python3 examples/vector_worked.py
status=$?
printf 'status: %s\n' "$status"
~~~

The final lines are:

~~~text
sha256-empty: PASS: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
sha256-abc: PASS: ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad
sha256-two-block-example: PASS: 248d6a61d20638b8e5c026930c3e6039a33ce45964ff2167f6ecedd419db06c1
summary: 3/3 passed
status: 0
~~~

The smoke check copies the bundle to a temporary directory. Appending one byte
causes provenance verification to fail. It then changes an expected digest and
updates the adjacent manifest: provenance succeeds, but vector execution fails
that case. This distinction demonstrates both what a digest establishes and
what it does not.

The valid claim is: “Python's SHA-256 implementation produced the three
expected byte-oriented results after the course-local artifact matched its
manifest.” It is not: “SHA-256 is proved correct” or “this environment is NIST
validated.”

## Check your understanding

1. Why are a FIPS algorithm standard and a CAVP validation result different
   evidence?
2. When do RFC 8174's uppercase requirement meanings apply?
3. Does a Reported RFC erratum immediately change the RFC text?
4. What does a content digest establish when artifact and manifest are held in
   the same writable directory?
5. Why must a vector state byte versus bit encoding and output truncation?
6. What additional claim does one deliberate failing run support?
7. Name four properties that three passing SHA-256 vectors do not establish.

Answers:

1. The standard defines an algorithm; CAVP is a program result for an exact
   implementation and recorded environment under program procedures.
2. When the document invokes BCP 14 and the defined words appear in uppercase;
   normative prose can still exist without those words.
3. No. RFC text is immutable and errata have separate statuses that must be
   interpreted and recorded.
4. Byte agreement with the digest. It does not independently authenticate
   either file against an attacker who can replace both.
5. Because textual fields can decode to different inputs, and a truncated
   expected value changes the comparison contract.
6. It shows the harness detected that specific introduced fault in that run.
7. Examples include full-input correctness, proof, side-channel resistance,
   key management, module validation, binary provenance, protocol safety, and
   deployment approval.

## Next step

Complete the lab by building a source record, atomic requirements matrix,
mutated-vector failure record, and bounded claim ledger. The assessment then
transfers the workflow to RFC 4231 HMAC-SHA-256 vectors with a separate schema
and harness.

## Sources

- National Institute of Standards and Technology,
  [FIPS 180-4, Secure Hash Standard](https://csrc.nist.gov/pubs/fips/180-4/upd1/final),
  updated final publication, August 2015; publication page retrieved
  2026-07-12.
- NIST Cryptographic Algorithm Validation Program,
  [Secure Hashing test requirements and vectors](https://csrc.nist.gov/Projects/Cryptographic-Algorithm-Validation-Program/Secure-Hashing),
  retrieved 2026-07-12. The page distinguishes informal vector use from CAVP
  validation.
- RFC Editor, [RFC 8174, Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words](https://www.rfc-editor.org/rfc/rfc8174.html),
  BCP 14, May 2017.
- RFC Editor, [Errata in RFCs](https://www.rfc-editor.org/series/rfc-errata/),
  status definitions retrieved 2026-07-12.
- Nir and Langley,
  [RFC 8439, ChaCha20 and Poly1305 for IETF Protocols](https://www.rfc-editor.org/rfc/rfc8439.html),
  June 2018; used as an example of an obsoleting document that incorporates
  predecessor errata.
- Nystrom,
  [RFC 4231, Identifiers and Test Vectors for HMAC-SHA-224, HMAC-SHA-256, HMAC-SHA-384, and HMAC-SHA-512](https://www.rfc-editor.org/rfc/rfc4231.html),
  Standards Track, December 2005; assessment transfer source.
- RFC Editor,
  [RFC 4231 errata search](https://www.rfc-editor.org/errata/rfc4231),
  retrieved 2026-07-12; source for the dated assessment errata snapshot.
- Python Software Foundation,
  [<code>hashlib</code> documentation for Python 3.11](https://docs.python.org/3.11/library/hashlib.html),
  library interface used by the worked harness.
- Python Software Foundation,
  [<code>hmac</code> documentation for Python 3.11](https://docs.python.org/3.11/library/hmac.html),
  transfer-assessment API including <code>compare_digest</code>.
