# Rubric: RFC HMAC standards evidence

## Rubric

The assessment is worth 100 points. Passing requires at least 80/100 and every
critical criterion.

| Criterion | Points | Evidence required |
| --- | ---: | --- |
| Source, requirements, and errata interpretation | 25 | Exact RFC identity/status/locations, BCP 14 handling, dated errata dispositions, and atomic source-labeled requirements |
| Provenance and vector schema | 25 | Bounded exact artifact, independent manifest, byte digest verification, strict fields/encodings/IDs, review record, and authenticity limits |
| Harness, negative evidence, and replay | 35 | Provenance-first execution, all four correct HMAC cases, strict rejection tests, no skips, deliberate changed-result failure, restoration, exact commands/channels/statuses |
| Claim discipline and communication | 15 | Layered claim ledger, environment and repository identity, explicit non-claims, readable evidence, and next-evidence requirements |
| **Total** | **100** |  |

## Critical criteria

All four critical criteria must pass:

1. **Authority integrity:** earn at least 20/25. The exact RFC, Standards Track
   status, sections, requirement sources, RFC 8174 context, and dated errata
   dispositions must be traceable. Invented source authority or silently
   applying a merely Reported erratum fails this criterion.
2. **Artifact integrity:** earn at least 20/25. Every case must have an
   unambiguous bounded schema and the vector file must match its manifest
   before execution. Missing provenance, path escape, ambiguous hex, or an
   authenticity claim based only on adjacent writable files fails it.
3. **Failure-sensitive execution:** earn at least 28/35. All four cases must run,
   malformed cases must be rejected rather than skipped, the deliberate wrong
   digest must fail after matching local provenance, restoration must pass, and
   results must retain channels and statuses. A runner that can report zero
   cases or a skipped case as success fails it.
4. **Claim boundary:** earn at least 12/15. The final claim must remain limited
   to the actual source, artifact, environment, implementation API, and cases.
   Claiming proof, full conformance, constant-time behavior, CAVP/CMVP
   validation, publisher authentication, or deployment approval fails it.

A total at or above 80 cannot compensate for a failed critical criterion.

## Scoring

- **Source, requirements, and errata (25):** 7 for exact source identity and
  document relationships, 5 for correct normative-language interpretation, 5
  for dated errata search/dispositions, and 8 for atomic requirements with
  source, location, preconditions, failure, evidence, and open questions.
- **Provenance and schema (25):** 6 for complete artifact and retrieval fields,
  5 for exact digest calculation and comparison, 7 for strict bounded
  case/encoding/path schema, 4 for review/repository identity, and 3 for a
  precise trust-root and authenticity analysis.
- **Harness and replay (35):** 8 for provenance-first bounded loading, 8 for
  correct HMAC API use and all four case verdicts, 8 for exhaustive malformed
  and boundary tests, 5 for failure-sensitive no-skip behavior, and 6 for
  retained mutation/restoration commands, outputs, channels, and statuses.
- **Claims and communication (15):** 6 for exact replay environment, 5 for
  observed/regression claims and explicit non-claims, and 4 for readable
  artifacts plus evidence needed to strengthen each rejected claim.

## Feedback and retry

Feedback names the first unsupported source interpretation, errata disposition,
schema ambiguity, provenance break, skipped case, wrong HMAC result, or
overstated claim; maps it to an outcome ID; and identifies the missing evidence.
Preserve the original submission and append a correction record.

A retry uses a different assessor-supplied standards/vector source and at least
four cases with different field shapes, including one rejection case. Rebuild
the source record, requirement mapping, artifact digest, strict parser, negative
tests, deliberate failure, replay record, and claim ledger. Rewording an
unsupported claim without repairing its evidence chain is not a successful
retry.
