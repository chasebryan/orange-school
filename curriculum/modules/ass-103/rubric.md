# Rubric: independent Sable replay dossier

## Rubric

The assessment is worth 100 points.

| Criterion | Points | Evidence required |
| --- | ---: | --- |
| Manifest, closure, provenance, environment, and TCB | 25 | Canonical bytes; separate anchor; exact sequence and identities; complete dependency/provenance closure; captured environment; direct TCB comparison |
| Hostile bundle and resource safety | 25 | Complete first-pass USTAR validation; path/type/duplicate/metadata/padding/size rejection before retention; verified writes only in a removed temporary root; exact endpoints |
| Offline deterministic replay and attack detection | 25 | Built-in no-network recipe; exact frames/order/output comparison; substitution/omission/addition/rollback/provenance/TCB/environment matrix; repeated deterministic replay |
| Reproducible failure-sensitive evidence and claims | 25 | Commands, identities, channels, statuses, calculations, resource accounting, five mutation/restoration pairs, calibrated matrix, residual risks, explicit non-claims |
| **Total** | **100** |  |

## Critical criteria

All five critical criteria must pass:

1. **Trusted selection and closure:** earn at least 20/25 for the first
   criterion. Raw canonical manifest bytes must match a separately supplied
   anchor before dossier policy is trusted. Subject, sequence floor,
   provenance/TCB approval, dependency closure, manifest materials, archive
   paths, and provenance coverage must agree. Unknown/cyclic/too-deep or
   structurally omitted support fails closed.
2. **Archive trust boundary:** earn at least 15/18 of the hostile-bundle points
   attributable to the first metadata pass. Every header must be validated
   before any material payload is retained. A link/special type, unsafe or
   duplicate path, extension, wrong/noncanonical metadata or checksum, nonzero
   padding, truncation, terminator error, omission/addition, or resource
   overflow must not reach extraction.
3. **Verified temporary isolation:** earn at least 6/7 of the hostile-bundle
   points attributable to material handling. Only authenticated, size/digest-
   verified regular bytes may be written, every write must remain under a new
   temporary root, and the complete root must be removed before success.
4. **Offline replay and attack sensitivity:** earn at least 20/25 for offline
   replay. The built-in recipe may not execute dossier code or resolve missing
   inputs. Exact deterministic comparison plus the required substitution,
   omission, addition, rollback, provenance, TCB, environment, and
   nondeterminism cases must fail for their intended bindings.
5. **Observed failure/restoration and claim discipline:** earn at least 20/25
   for evidence and claims. All five targeted mutations must have an immediate
   observed nonzero status and exact restoration must have zero status. The
   evidence must preserve identities, commands, channels, calculations, TCB,
   assumptions, residual risks, and every required narrow non-claim.

A total of 80/100 or more cannot compensate for a failed critical criterion.

## Scoring

- **Manifest, closure, provenance, environment, and TCB (25):** 6 for exact
  canonical JSON and stable diagnostics; 6 for an external anchor with subject,
  identity, sequence floor, provenance, and TCB approval; 6 for correct bounded
  dependency/provenance closure and set equalities; 4 for exact environment and
  observed direct TCB capture; and 3 for explaining authenticity, provenance,
  freshness, and undeclared-dependency limits.
- **Hostile bundle and resource safety (25):** 8 for raw USTAR alignment,
  checksum/encoding, type, link-target, metadata, offset, order, padding, and
  terminator validation; 5 for every unsafe/aliased/duplicate path and
  extension/special-type rejection; 5 for isolated exact endpoint/one-beyond
  evidence; 4 for manifest authentication followed by size/digest verification
  before writes; and 3 for fresh-root containment and observed cleanup.
- **Offline deterministic replay and attack detection (25):** 6 for a fully
  specified distinct frame, closure order, output cap, and exact comparison; 4
  for repeated byte-deterministic replay; 6 for material/manifest/combined
  substitution and omission/addition tests; 5 for rollback, provenance, TCB,
  subject, environment, and recipe tests; and 4 for corrupted and deliberately
  nondeterministic output detection.
- **Reproducible failure-sensitive evidence and claims (25):** 7 for absolute
  path, versions, source/input/manifest/dossier/output identities, exact
  commands, both channels, and immediate statuses; 6 for five complete
  mutation/restoration pairs; 5 for endpoint arithmetic and justified
  complexity/retained-data bounds with exclusions; 4 for the calibrated
  evidence matrix, TCB, assumptions, and residual risk; and 3 for all required
  non-claims, including no Orange conclusion.

Pass only with at least 80/100 and all critical criteria.

## Feedback and retry

Feedback identifies the first ambiguous canonical byte, trusted-selection edge,
unknown/omitted dependency, provenance mismatch, TCB/environment mismatch,
header field, unsafe path, duplicate, padding byte, unbounded counter, retained
payload, escaped write, frame byte/order, comparison, mutation record, or
overstated claim. It maps the defect to **ASS-103-01**, **ASS-103-02**,
**ASS-103-03**, or **ASS-103-04** and names the unsupported conclusion.

A retry changes the manifest schema/magic, every resource cap, archive metadata
profile, sequence width, at least two provenance fields, TCB profile, recipe
prefix, frame field order/widths, roots/graph, and assessor-selected hostile and
attack cases. The learner must recalculate every endpoint, digest, closure,
output, mutation, complexity statement, and claim. Revised prose cannot replace
executable normal, boundary, hostile, attack, replay, or failure/restoration
evidence.
