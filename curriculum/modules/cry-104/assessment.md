# Assessment: admit an RFC HMAC vector set

## Instructions

Complete this assessment independently in a fresh temporary directory with
Python 3.11 or newer and only its standard library. Submit source and errata
records, an atomic requirements matrix, a provenance manifest, vector bundle,
strict harness, tests, deliberate failure evidence, and a scoped claim ledger.
Do not copy or rename the module harness.

Use RFC 4231, Standards Track, December 2005, as the transfer source. Its
Section 4 supplies HMAC-SHA test vectors and Section 5 limits what security
those vectors claim. Use Python's <code>hmac</code> and <code>hashlib.sha256</code>;
do not implement HMAC or SHA-256 yourself.

This assessment covers:

- **CRY-104-01:** Classify a standards source, its exact version and status,
  normative language, updates, and errata, then extract atomic requirements
  with stable locations.
- **CRY-104-02:** Preserve standards and vector provenance with bounded
  manifests, content digests, review context, and explicit authenticity limits.
- **CRY-104-03:** Execute positive and negative vectors reproducibly, retain
  failure evidence, and scope claims to what the vectors actually establish.

## Knowledge check

1. Distinguish an algorithm standard, protocol/profile selection, test-vector
   source, algorithm-validation result, and module-validation result.
2. State the RFC 8174 capitalization conditions and explain why normative text
   need not contain BCP 14 key words.
3. Define Reported, Verified, Rejected, and Held for Document Update errata.
   Explain why the observed date is evidence.
4. List the minimum identity fields for a standards artifact and a vector case.
5. Explain what a matching SHA-256 artifact digest does and does not establish.
6. Explain why positive vectors, malformed-input tests, and deliberately wrong
   expected-output tests provide different evidence.
7. Distinguish observed behavior, regression evidence, conformance evidence,
   program validation, and system assurance.
8. Name at least six properties that passing HMAC vectors alone cannot
   establish.

## Independent task

1. **Source and errata intake — CRY-104-01.** Create a source record for RFC
   4231 with exact title, RFC number, Standards Track category, December 2005
   date, stable RFC Editor URL, Sections 2, 4.1, 4.2 through 4.5, and 5 in
   scope. Use the supplied
   [dated errata snapshot](resources/rfc4231-errata-snapshot.md), record its RFC
   Editor query method and observation date, and classify every listed item by
   ID, type, status,
   affected section, and disposition. Never treat a merely Reported item as
   silently incorporated text.
2. Create an atomic requirements matrix covering source identity; exact
   HMAC-SHA-256 selection; hexadecimal key, data, and output encoding; full
   32-byte output for cases 1 through 4; case identity; strict parsing; no
   skipped cases; constant-time comparison API selection; and overall failure
   behavior. Mark whether each requirement comes from RFC 4231, RFC 8174, the
   Python API contract, or your explicitly labeled evidence profile.
3. **Provenance — CRY-104-02.** Create <code>rfc4231-vectors.json</code> with
   cases 1 through 4 and a separate <code>provenance.json</code> that pins its
   exact bytes. Case 1 is:

   ~~~text
   key: 0b repeated 20 times
   data hex: 4869205468657265
   HMAC-SHA-256: b0344c61d8db38535ca8afceaf0bf12b881dc200c9833da726e9376c2e32cff7
   ~~~

   Transcribe cases 2 through 4 from the supplied
   [course data sheet](resources/rfc4231-cases-1-4.md), and verify the sheet
   against the source identity before relying on it. Preserve RFC section and
   test-case identity in every record. Bound files, fields,
   key/data lengths, vector count, identifiers, and output width. State how
   the manifest was reviewed and why its local digest is not independent
   publisher authentication.
4. **Harness — CRY-104-03.** Write <code>run_hmac_vectors.py</code>. Reject
   duplicate JSON keys, unknown or missing fields, duplicate case IDs, unsafe
   artifact paths, wrong artifact digests, non-lowercase or odd-length hex,
   empty or oversized keys/data, outputs other than 32 bytes, zero cases, and
   more than 100 cases. Capture each bounded regular artifact once, verify its
   provenance digest, then decode and execute that same immutable byte capture;
   never hash a path and reopen it for execution. Calculate
   with <code>hmac.new(key, data, hashlib.sha256).digest()</code> and compare
   expected and actual bytes with <code>hmac.compare_digest</code>. Emit one
   verdict per case and exit nonzero if any case fails.
5. Test the pristine four-case bundle, every invalid class above, the maximum
   accepted case count, and a changed expected digest. Tests must confirm that
   malformed cases are rejected rather than skipped. Deliberately change one
   valid expected digest, update the local manifest, preserve the vector
   failure and nonzero status, restore both files, and preserve the passing
   four-case run.
6. **Evidence and claims.** Write <code>evidence.md</code> with exact source and
   errata snapshot, artifact/manifest digests, repository state, Python and
   platform identity, commands, directory, stdout, stderr, statuses, case
   counts, skipped count, mutation, and restoration. State exactly what the run
   supports. Explicitly reject claims of complete RFC conformance, key-storage
   safety, protocol security, constant-time HMAC execution, CAVP/CMVP
   validation, publisher-authenticated vectors, or deployment approval.

## Completion criteria

Use the [rubric](rubric.md). Passing requires at least 80/100 and every critical
criterion. The submission must:

- preserve exact authority, status, location, normative-language, update, and
  errata evidence for **CRY-104-01**;
- pin and validate an unambiguous, bounded four-case artifact while explaining
  authenticity limits for **CRY-104-02**;
- reject malformed or changed evidence, run every valid case, preserve one
  deliberate failure and restoration, and bound every resulting claim for
  **CRY-104-03**; and
- keep all work offline and use the standard library rather than a custom HMAC
  or hash implementation.

A green run with skipped cases, an unpinned vector file, an erratum treated as
accepted without status evidence, or a CAVP/CMVP claim cannot pass.
