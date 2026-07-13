# Reproducibility, supply chains, and offline replay

Reproducibility is the ability to repeat a declared process under a declared
environment and compare the new result with a declared expectation. It is not
the claim that every machine, every time, must produce equal bytes. Supply-chain
evidence binds a selected subject to its materials, dependency closure,
provenance records, environment, and trusted computing base (TCB). It does not
make those things trustworthy merely by listing them.

This module uses **Quartz**, a bounded Python 3.11 standard-library teaching
model. Quartz does not execute programs from a bundle. It applies one built-in
deterministic recipe after authenticating a manifest and validating every
archive boundary. Quartz is not Orange syntax, tooling, packaging, or release
infrastructure. Its results establish no Orange property.

## Learning objectives

- **ASS-103-01:** Design a canonical manifest that binds a subject and monotonic
  sequence to material sizes and digests, complete dependency closure,
  supply-chain provenance identities, an environment profile, a TCB inventory,
  a deterministic recipe, and an expected result.
- **ASS-103-02:** Validate a bounded replay bundle as hostile input, rejecting
  links, special entries, traversal, noncanonical paths, duplicate names,
  omissions, additions, and per-member or total oversize before retaining
  material payloads.
- **ASS-103-03:** Replay an authenticated dependency closure with no network in
  a fresh temporary directory, compare deterministic output exactly, and
  detect manifest or payload substitution, omission, unapproved provenance or
  TCB changes, and rollback below a trusted sequence floor.
- **ASS-103-04:** Produce reproducible, failure-sensitive replay evidence with
  exact commands, identities, endpoints, environment and TCB observations,
  deliberate failure/restoration pairs, residual risks, and narrow non-claims.

## Prerequisites

Pass <code>ass-101</code>, <code>sys-103</code>, and <code>cmp-103</code>. You
should be able to scope a claim and its evidence, distinguish source declarations
from built artifacts, inspect dependency closure, and explain why a digest is a
content identity rather than an authenticity proof.

The executable material requires Python 3.11 or newer and only its standard
library. It performs no network access. Replay writes material and result bytes
only below a fresh <code>TemporaryDirectory</code>, which it removes before
returning.

## Lesson

### Reproducibility starts with a complete question

"Can you reproduce this?" is incomplete. A professional replay request names:

1. the exact subject and its selected version or sequence;
2. every input in the transitive dependency closure;
3. the process or recipe and its parameter ordering;
4. the environment and TCB on which the process relies;
5. the expected observation and comparison rule; and
6. the trusted information used to select the intended subject.

Two useful but different targets are a **reproducible process**, where rerunning
the declared steps yields an acceptably equivalent result, and a
**reproducible build**, where independent construction under the declared
conditions yields byte-identical artifacts. A functional comparison, normalized
comparison, digest comparison, and byte-for-byte comparison are different
relations. State one before collecting evidence.

Quartz uses the narrowest relation: the output size and SHA-256 content identity
must both match. Its built-in recipe emits a fixed prefix and, for each material
in sorted closure order, a one-byte identifier length, identifier bytes,
four-byte big-endian payload length, and payload bytes. Equal accepted inputs
therefore produce equal output bytes under this model. This says nothing about
whether that recipe is useful for a production build.

### Canonical bytes prevent ambiguous identities

A manifest digest is meaningful only if there is one byte representation for
one accepted record. Quartz accepts ASCII JSON with sorted object keys, no
insignificant whitespace, no duplicate keys, and no non-finite numbers. Arrays
whose order is not semantic—dependencies, roots, and governed materials—must be
sorted and unique. Arrays whose order is part of the schema are explicitly
validated.

The manifest binds these fields:

| Field | Bound fact | Boundary it does not cross |
| --- | --- | --- |
| <code>subject</code>, <code>sequence</code> | selected subject name and monotonic release coordinate | freshness without an external floor |
| <code>materials</code> | id, safe path, exact size, SHA-256, dependencies, provenance id | meaning or benignness of bytes |
| <code>provenance</code> | producer, origin, revision, governed materials, canonical identity | truth of a producer statement |
| <code>environment</code> | supported Python and recipe-engine profile, network forbidden | equivalence of undeclared host state |
| <code>tcb</code> | runtime and replay-model versions, roles, identities | correctness of those components |
| <code>recipe</code>, <code>expected</code> | roots, transformation id, output size and digest | any property not tested by that comparison |

A SHA-256 digest is a stable name for bytes within this model. It is not a
signature, authorization, timestamp, proof of origin, proof of safety, or proof
that a dependency is free of vulnerabilities. If an attacker can replace both
the artifact and the expected digest, digest comparison alone detects nothing.

### The trust anchor must arrive separately

Quartz receives a <code>TrustAnchor</code> outside the bundle. It includes the
expected manifest identity, subject, minimum acceptable sequence, approved
provenance identities, and approved TCB identities. The replayer hashes the raw
canonical manifest and compares it with the anchor before treating manifest
contents as selected policy.

This model deliberately does not specify how the anchor becomes trusted. A
production design might use a pinned local policy, authenticated transparency
log, signed release statement, threshold approval, or hardware-rooted channel.
Each has its own keys, identities, freshness, revocation, and compromise model.
Calling an anchor "trusted" records an assumption and TCB boundary; it does not
prove the channel sound.

The sequence floor makes one rollback pattern visible. If the anchor requires
sequence 7, an authentic sequence-6 manifest is rejected even when all of its
internal digests agree. The floor does not detect every replay or freeze attack:
an external system must update, persist, and protect that state.

### Dependency closure turns a list into an obligation

Suppose <code>sample-data</code> depends on <code>format-spec</code>. Replaying
only the root while silently obtaining the specification from the host would
not be offline or complete. Quartz walks every declared root transitively,
rejects unknown identifiers and cycles, and caps a path at eight dependency
edges. Every declared material must occur in the selected closure; an unused
extra entry is not harmless because it makes the meaning of "the bundle"
unclear.

For every accepted manifest, these sets must be equal:

~~~text
manifest material ids
  = transitive closure of recipe roots
  = material paths present in the archive
  = union of material ids governed by provenance records
~~~

An unknown dependency detects an omitted declaration. A manifest material with
no archive member detects an omitted payload. An archive member with no
manifest material detects an addition. A provenance inventory that disagrees
with material references detects an omitted or substituted provenance edge.
This is structural completeness under the schema, not proof that the author
declared every real-world dependency.

### Archive validation happens before material retention

Archive extraction is a trust boundary. Names such as
<code>../../home/user/.config</code>, absolute paths, symbolic links, hard links,
devices, and duplicate names can make a naive extractor write somewhere or
overwrite something the manifest did not describe. Compression can also hide a
large expanded payload behind a small transfer.

Quartz accepts only uncompressed POSIX USTAR bytes. It manually scans the
512-byte headers and validates header checksums, regular-file type, empty link
target, exact octal size/checksum encodings, mode 0644, zero uid/gid/mtime,
empty owner/group/device/prefix fields, lowercase portable path components,
no Windows device-name stems or trailing-dot aliases, unique names,
sizes, counts, bounds, offsets, zero member padding, a two-block all-zero
terminator, and final zero padding to a 10,240-byte USTAR record. The first member must be
<code>manifest.json</code>; material paths follow in lexical order. It rejects
every link and special entry. It rejects an archive larger than 131,072 bytes,
more than 16 materials, a manifest larger than 16,384 bytes, a material larger
than 4,096 bytes, and total material payload larger than 65,536 bytes.

That complete header pass occurs before any material payload slice is created.
Only the bounded manifest is then retained and compared with the trust anchor.
Only after manifest, closure, provenance, environment, TCB, and archive-path
validation does Quartz retain each material, verify its size and digest, and
write it below a new temporary root. A fresh tree plus prevalidated relative
paths prevents preexisting symlink races inside the teaching workspace. This is
not a general secure archive-extraction library.

### Offline replay makes undeclared retrieval a failure

An offline bundle must contain its declared closure. The replayer must not
"help" by resolving a missing package, tag, compiler, schema, expected output,
or key over a network. Such retrieval changes both the evidence subject and the
trust model. Quartz has no import of a network client and its only recipe is
built in. Missing content is a rejection.

Offline does not mean independent of the host. Quartz relies on the Python
runtime, standard library JSON and hashing implementations, filesystem,
temporary-directory cleanup, operating system, model source, and expected
anchor. Its manifest names the directly measured runtime/model TCB identities;
the result records Python implementation/version and recipe engine. Kernel,
hardware, firmware, filesystem semantics, allocator behavior, and the operator
who selected the anchor remain residual TCB or environmental assumptions.

### Determinism is an engineered property

Reproducible systems control common variation sources:

- timestamps, locale, timezone, current directory, username, and host paths;
- unordered filesystem enumeration, map iteration, and archive member order;
- generated random values and nondeterministic parallel scheduling;
- compiler, linker, dependency resolver, and build-option versions;
- embedded build ids, absolute debug paths, and unstable compression metadata;
- environment variables and undeclared system dependencies; and
- remote resources that change while retaining the same human-readable name.

Quartz controls only its smaller model: canonical JSON, USTAR metadata fixed by
the builder, lexical member and closure order, explicit big-endian framing,
immutable material bytes, a fixed recipe, a pinned runtime/model identity, and
no network. Replaying twice and comparing bytes is useful observation. It is
not a universal proof that every conforming implementation or host produces the
same result.

### Failure sensitivity distinguishes evidence from ceremony

A green replay is informative only if the evidence would turn red when a
relevant assumption is violated. The supplied smoke check independently
observes rejection for:

- archive links, traversal, duplicate paths, extra and missing members, and
  per-member oversize;
- payload bytes changed without changing their declared digest;
- a changed manifest under the previous trusted manifest identity;
- a valid older manifest below the trusted sequence floor;
- unknown dependencies and dependency cycles;
- an expected output digest that does not match replay; and
- a changed provenance identity not approved by the anchor.

It also launches an isolated assertion with an intentionally wrong replay size,
preserves the nonzero status and assertion channel, restores the expectation,
and preserves the zero-status rerun. Deliberate failure does not prove all
failure paths work. It demonstrates sensitivity to one named perturbation.

### Bounds and complexity belong in the evidence

Quartz accepts at most 16 materials of 4,096 bytes each, 16 references per
bounded array, paths of 80 ASCII bytes, ordinary text of 120 ASCII bytes,
dependency depth eight, and sequences from 0 through 2,147,483,647. Its output
cap of 66,560 bytes covers the 65,536-byte payload endpoint plus fixed framing.

For archive bytes <em>B</em>, material/provenance records <em>M</em>, dependency
edges <em>D</em>, and retained payload bytes <em>P</em>, header scanning is
O(B), indexing and closure are O(M + D), hashing and replay are O(P), and
retained payload/output storage is O(P) within the fixed caps. Python object,
interpreter, archive-input, filesystem, and allocator memory are not counted as
exact model bytes.

## Worked example

[replay_bundle.py](examples/replay_bundle.py) implements the bounded model.
[replay_worked.py](examples/replay_worked.py) creates two local materials:
<code>sample-data</code> depends on <code>format-spec</code>, and one provenance
record governs both. It constructs canonical manifest and USTAR bytes in
memory, derives a separately passed anchor, replays the complete closure, and
reports the selected subject, sequence, identities, output, and cleanup.

Run it from any directory:

~~~sh
PYTHONDONTWRITEBYTECODE=1 python3 -B \
  curriculum/modules/ass-103/examples/replay_worked.py
~~~

The expected subject is <code>quartz-record-demo</code>, sequence is 7, closure
is <code>format-spec,sample-data</code>, output size is 90, and
<code>workspace-removed</code> is true. The exact manifest and output digests
also appear. They may change when the reviewed model source changes because its
identity is part of the TCB inventory.

The worked example derives its anchor directly from the manifest for teaching
convenience. A professional verifier must obtain and protect expected identity,
provenance approval, TCB approval, and rollback floor through a separate trusted
selection mechanism.

## Check your understanding

1. Why does a bundle-provided manifest digest fail to authenticate that same
   bundle?
2. Which equality detects an archive material omitted after manifest creation?
3. Why are a symbolic link and a duplicate regular-file path rejected before
   payload retention?
4. What additional external state is needed to reject an authentic older
   release?
5. Why does an approved provenance digest not prove the producer's statement
   true?
6. Name three host facts Quartz still trusts despite performing no network
   access.
7. What exact relation does Quartz compare, and which broader reproducibility
   claims remain unsupported?
8. Why must deliberate failure be followed by restoration and a passing rerun?

## Next step

Complete [the lab](lab.md) by designing an independent bounded replay model,
then take [the assessment](assessment.md). Preserve the passing baseline before
introducing deliberate mutations. Keep every generated bundle, workspace,
output, and evidence record in a fresh temporary directory.

## Sources

- Python 3.11 documentation, [<code>tarfile</code> — Read and write tar archive files](https://docs.python.org/3.11/library/tarfile.html), especially member types and extraction cautions.
- Python 3.11 documentation, [<code>tempfile</code> — Generate temporary files and directories](https://docs.python.org/3.11/library/tempfile.html).
- Python 3.11 documentation, [<code>hashlib</code> — Secure hashes and message digests](https://docs.python.org/3.11/library/hashlib.html).
- The Open Group Base Specifications Issue 7, [<code>pax</code> archive interchange format](https://pubs.opengroup.org/onlinepubs/9699919799/utilities/pax.html).
- SLSA, [Provenance](https://slsa.dev/spec/v1.1/provenance), for a broader supply-chain provenance predicate and its boundaries.
- in-toto, [Specification](https://github.com/in-toto/docs/blob/v1.0/in-toto-spec.md), for supply-chain step and material/product metadata concepts.
