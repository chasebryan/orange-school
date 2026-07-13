# Assessment: Northstar update dossier

## Instructions

Build **Northstar**, an independent bounded claim-record and closure checker for
a fictional offline update-manifest verifier. Do not import, copy, or edit the
Keystone model or Beacon lab records. Your data types, validation paths,
canonicalization function, graph traversal, status derivation, and test oracle
must be independently implemented with Python 3.11 standard-library code.

Work offline in a fresh temporary directory. Submit source, tests, generated
reports, hashes, exact commands, stdout, stderr, immediate statuses, a short
design note, and the calibrated final dossier. Keep failed evidence before
restoring a pass.

## Knowledge check

Answer before running your implementation:

1. Rewrite "the update system is trustworthy" into two separately falsifiable
   claims with exact subjects, versions, scopes, and exclusions.
   **ASS-101-01**
2. Distinguish evidence identity, artifact integrity, provenance, authenticity,
   correctness, and freshness. Give one non-implication for each.
   **ASS-101-02**
3. Explain why a passing signature-check claim and a passing rollback-check
   claim do not prove the composed updater installs only authorized newer
   images. **ASS-101-03**
4. Define dependency closure and show how inherited assumptions and TCB entries
   change a root claim's inventory. **ASS-101-03**
5. Give distinct Northstar examples of <code>INVALID</code>,
   <code>REFUTED</code>, <code>UNSUPPORTED</code>, and <code>SUPPORTED</code>.
   **ASS-101-04**
6. Explain why a proof kernel, theorem encoding, frozen expected-output file,
   and identity-distribution channel may belong in an assurance TCB.
   **ASS-101-02**, **ASS-101-04**
7. A digest matches but an assumption is unverified. What status is justified,
   and why is neither supported nor refuted necessarily correct?
   **ASS-101-04**
8. List at least six Orange properties that an independent Northstar Python
   model cannot establish. **ASS-101-04**

## Independent task

Implement and assess the Northstar dossier:

1. Define immutable, exact-type records for claims, evidence, assumptions, TCB
   entries, findings, and reports. A claim names a subject, version, proposition,
   scope, exclusions, direct evidence, dependencies, assumptions, and TCB.
   Reject mutable collections, host Booleans in integer fields, duplicate or
   noncanonical references, unsupported enum values, and malformed digests with
   stable diagnostics. **ASS-101-01**
2. Define evidence kinds for test, analysis, formal result, inspection, and
   provenance. Each evidence record includes a result, artifact SHA-256,
   producer, subject, method, assumptions, TCB, and sorted facts. Document one
   appropriate conclusion and two non-proofs per kind. **ASS-101-02**
3. Define a canonical UTF-8 JSON schema named
   <code>northstar-evidence-v1</code>: sorted object keys, no insignificant
   whitespace, ASCII escaping, canonical arrays, and the result included.
   Compute <code>sha256:&lt;hex&gt;</code>, recompute it during evaluation, and reject
   a syntactically valid substituted identity. Prove determinism with a
   separately written byte-construction oracle for at least 12 fixed records.
   **ASS-101-02**
4. Use independent caps of 28 claims, 48 evidence records, 24 assumptions, 24
   TCB entries, 14 references or facts, 240 characters per text field, and
   seven dependency edges from a root. Isolate every endpoint and smallest
   overflow: 28/29, 48/49, 24/25, 14/15, 240/241, and depth 7/8. Report before
   retaining or traversing the first excessive item. **ASS-101-03**,
   **ASS-101-04**
5. Detect duplicate identifiers, unknown references, self-dependency, cycles,
   depth overflow, identity mismatch, and missing inherited assumption or TCB
   inventory. Return stable sorted findings and immutable counterexample paths.
   Include a two-node cycle, a seven-edge passing chain, and the smallest
   eight-edge failure. **ASS-101-03**
6. Build component claims for exact-manifest signature verification and
   monotonic version checking. Build an install-authorization claim depending
   on both. With no direct integration evidence, assert
   <code>UNSUPPORTED</code> and an exact non-composition reason. Add direct
   evidence covering manifest/image binding, version comparison, error
   propagation, and the install decision; only then may the integration claim
   become <code>SUPPORTED</code>. **ASS-101-03**
7. Derive statuses rather than storing them. Invalid structure produces
   <code>INVALID</code>; direct failed evidence produces <code>REFUTED</code>;
   missing or inconclusive evidence, unconfirmed assumptions, non-reviewed TCB,
   or non-supported dependencies produce <code>UNSUPPORTED</code>; all declared
   obligations passing produces <code>SUPPORTED</code>. The bundle uses the
   most conservative present status. **ASS-101-04**
8. Test at least 18 adversarial mutations, including swapped artifact digest,
   changed result under an old identity, duplicate fact, unknown evidence,
   false and unverified assumptions, unreviewed and compromised TCB entries,
   dependency refutation, omitted inherited inventory, noncanonical ordering,
   and resource overflow. For each, assert a precise result and preserve the
   first counterexample. **ASS-101-02** through **ASS-101-04**
9. Preserve five deliberate-failure/restored-pass pairs: direct signature
   failure, missing integration evidence, changed canonical fact, unverified
   rollback-state assumption, and omitted TCB dependency. Record exact command,
   stdout, stderr, and immediate status. A final restored run must be byte
   identical under <code>PYTHONHASHSEED=0</code> and 29. **ASS-101-04**
10. Submit <code>northstar-dossier.md</code> with scoped claims, evidence table,
    assumptions and falsifiers, transitive closure, TCB inventory, derived
    statuses, model bounds, complexity, trust boundary, non-proofs, and residual
    risks. State that the result proves neither the Python runtime nor the
    external updater and establishes no Orange syntax, semantics, compiler,
    runtime, library, proof, safety, security, conformance, or release claim.
    **ASS-101-01** through **ASS-101-04**

## Completion criteria

Earn at least 80/100 under <code>rubric.md</code> and pass every critical
criterion. The assessor must reproduce the assessment offline on Python 3.11
or newer from a fresh temporary directory. Every endpoint, overflow,
adversarial mutation, closure path, evidence identity, deliberate failure,
restored pass, status, and non-proof must be observable from submitted commands
and immutable evidence.

