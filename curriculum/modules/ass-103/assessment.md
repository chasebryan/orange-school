# Assessment: independent Sable replay dossier

## Instructions

Build **Sable**, a new offline replay-dossier verifier. Do not copy, import,
rename, or mechanically translate Quartz or your Ember lab. Use Python 3.11 or
newer and only its standard library. All source, bundles, outputs, mutations,
and evidence must remain below one newly created temporary directory. The
submission must run with no network, package installation, administrator
permission, repository write, or global configuration change.

Sable has its own exact envelope: at most 10 materials, 2,048 bytes per
material, 16,384 total material bytes, 10,240 canonical manifest bytes,
64-byte ASCII paths, 10 references per bounded array, dependency depth five,
and 81,920 uncompressed archive bytes. Text is at most 88 printable ASCII
bytes. Sequence is an exact integer from 0 through 65,535. Its schema is
<code>sable-replay-v2</code>; its one built-in recipe begins with
<code>SBL2</code> and uses your independently specified canonical frames.

Submit:

- <code>sable_replay.py</code> with immutable records, stable diagnostics,
  canonical manifest handling, hostile USTAR validation, closure/provenance/TCB
  checks, temporary replay, deterministic comparison, and cleanup;
- <code>test_sable_replay.py</code> with fixed normal, exact endpoint,
  one-beyond, hostile, supply-chain, comparison, and failure-sensitivity cases;
- <code>format.md</code> with exact accepted header/manifest/frame bytes,
  validation order, invariants, environment profile, and resource accounting;
- <code>claim.md</code> with the exact proposition, scope, exclusions,
  assumptions, TCB, residual risks, and non-claims; and
- <code>evidence.md</code> with hashes, commands, channels, immediate statuses,
  calculations, comparison results, and mutation/restoration records.

An assessor must be able to replay every stated observation from the temporary
submission without access to the course examples.

## Knowledge check

Answer in your own words before writing code:

1. Distinguish reproducible process, reproducible build, byte identity,
   normalized equivalence, and functional equivalence.
2. Explain why hashing a manifest does not authenticate it when the expected
   hash arrives inside the same untrusted dossier.
3. Explain how a protected minimum sequence detects a rollback that internal
   manifest consistency cannot detect.
4. State the equality among root dependency closure, manifest materials,
   archive paths, and provenance-governed materials. Name one real undeclared
   dependency that this equality still cannot discover.
5. Explain why symbolic links, hard links, duplicate paths, nonzero padding,
   and alternate header metadata matter even when every declared file digest
   is correct.
6. State why header scanning must finish before retaining a material payload
   and why manifest authentication must precede trusting its limits or paths.
7. Explain why a provenance content identity establishes neither authorship
   nor truth without an external authorization mechanism.
8. List the environment and TCB state necessary to interpret one deterministic
   replay comparison. Separate captured facts from trusted assumptions.
9. Explain why offline replay forbids fallback dependency retrieval and why
   offline is not the same as host-independent.
10. Give one substitution, omission, addition, rollback, and nondeterminism
    case, naming the exact binding that should reject each.
11. State Sable's time and retained-data complexity with variables for archive
    bytes, records/edges, and material bytes. Identify memory excluded from the
    exact model.
12. Explain why one passing replay plus one deliberate failing mutation is
    evidence for a finite case rather than proof of universal reproducibility,
    supply-chain integrity, safety, or security.

## Independent task

Implement and document Sable with all of these requirements:

1. **Canonical identity — ASS-103-01.** Specify one canonical ASCII JSON
   representation, reject duplicate/unknown keys and noncanonical bytes, bind
   schema/subject/sequence/environment/TCB/material/dependency/provenance/root/
   recipe/expected-output fields, and prove accepted decode/re-encode identity.
2. **Separate selection — ASS-103-03.** Define an immutable out-of-dossier
   anchor with manifest identity, subject, sequence floor, approved provenance
   identities, and approved TCB identities. Check raw manifest identity first.
   No accepted dossier may derive its own authority.
3. **Complete closure — ASS-103-01.** Reject unknown/self/cyclic dependencies
   and paths beyond five edges. Require exact set equality among closure,
   manifest materials, archive paths, and provenance coverage. Reject an unused
   declared material rather than silently changing the subject.
4. **Hostile archive boundary — ASS-103-02.** Manually validate one exact
   uncompressed USTAR profile in a first pass: alignment, headers, checksums and
   their encoding, regular type, no link target, fixed metadata, safe canonical
   ASCII paths, lexical order, unique names, data offsets, zero member padding,
   fixed terminator/final padding, and every bound. Reject all link/special and
   extension member types before retaining payload.
5. **Verified temporary write — ASS-103-02.** Authenticate/validate the bounded
   manifest after header validation, then verify each material's size/digest
   before writing beneath a fresh temporary root. Create no links, never write
   outside the root, and remove the complete workspace before success returns.
6. **Deterministic replay — ASS-103-03.** Specify Sable's distinct
   <code>SBL2</code> frame fields, widths, byte order, closure ordering, and
   output cap. Execute only the built-in recipe, with no bundle code or remote
   resolver. Compare complete output bytes plus exact size and SHA-256.
7. **Environment and TCB — ASS-103-01.** Bind and observe exact Python
   implementation/version, Sable model hash/version, and recipe engine. Record
   parser, hash implementation, OS/filesystem/temp cleanup, anchor channel,
   operator, kernel, and hardware boundaries. Reject a declared/observed direct
   TCB mismatch.
8. **Normal determinism — ASS-103-03.** Replay one fixed two-level dossier at
   least twice in separate fresh workspaces. Assert canonical manifest bytes,
   dossier bytes, closure order, output bytes/size/digest, observed direct TCB,
   and cleanup are equal where the contract requires equality.
9. **Endpoints and one beyond — ASS-103-02.** Independently cover sequences
   0/65,535 and -1/65,536; paths 1/64/65 bytes; materials 0/1/10/11; payloads
   0/2,048/2,049 bytes; totals exactly 16,384/16,385; references 10/11;
   dependency depth 5/6; manifest 10,240/10,241; and dossier 81,920/81,921.
   Where no valid object reaches an exact byte endpoint, construct a direct
   parser input and explain why. Isolate counters so an earlier error cannot
   mask the intended boundary.
10. **Hostile dossier matrix — ASS-103-02.** Test wrong header checksum and
    encoding, nonzero uid/gid/mode/mtime variant, symbolic link, hard link,
    directory, FIFO/device, PAX/GNU extension, absolute/traversal/backslash/
    aliased paths, uppercase or Windows device-name components, trailing-dot
    aliases, duplicate/unsorted names, nonzero member padding, truncated
    header/payload, missing/short terminator, noncanonical final padding,
    omitted declared member, and undeclared extra member. Assert stable code and
    complete message with no payload retention.
11. **Supply-chain matrix — ASS-103-03.** Test altered material bytes, changed
    size, changed manifest under the old anchor, altered payload plus updated
    digest under the old anchor, unknown dependency, cycle, unclosed material,
    omitted/extra provenance edge, changed provenance identity, unapproved TCB,
    observed TCB mismatch, wrong subject, sequence rollback, unsupported
    environment, unknown recipe, and wrong output bytes/size/digest.
12. **Deliberate failure/restoration — ASS-103-04.** Preserve five isolated
    pairs: wrong expected output, skipped path-traversal rejection, skipped
    manifest-anchor comparison, <code>&lt;=</code> changed to <code>&lt;</code> at
    one size endpoint, and nondeterministic closure ordering. Each mutation's
    targeted test must exit nonzero with preserved stdout/stderr; each exact
    restoration must exit zero. Source weakening or test skipping is failure.
13. **Evidence discipline — ASS-103-04.** Record the absolute temporary root,
    Python/platform/model identities, all input/manifest/dossier/output/source
    hashes, exact commands, channels and immediate statuses, endpoint arithmetic,
    five mutation pairs, and a specification/observation/inference/unsupported
    matrix. State O(B + M + D + P) work and O(P) retained model bytes only if
    your implementation and counters justify them.
14. **Claim discipline — ASS-103-04.** State exactly what the finite Sable
    evidence supports. Explicitly deny universal reproducibility, build
    equivalence, provenance truth, authorship, freshness without anchor state,
    malicious-code safety, cryptographic signature verification, transparency,
    revocation, host independence, constant-time behavior, correctness, safety,
    security, and every Orange property.

## Completion criteria

Use [the rubric](rubric.md). Passing requires at least 80/100 and every critical
criterion. A complete submission must:

- meet the exact canonical manifest, closure, provenance, environment, TCB, and
  separately anchored selection contract for **ASS-103-01**;
- reject the complete hostile USTAR and resource matrix before payload retention
  and write verified bytes only in a removed temporary root for **ASS-103-02**;
- detect substitution, omission, addition, rollback, TCB/provenance drift, and
  nondeterministic or incorrect output under a no-network built-in replay for
  **ASS-103-03**;
- preserve all normal, endpoint, one-beyond, hostile, supply-chain, comparison,
  and five observed failure/restoration records for **ASS-103-04**; and
- limit conclusions to the exact Sable model, dossier, environment, anchor, and
  observations without making an Orange capability claim.
