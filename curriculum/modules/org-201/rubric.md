# Rubric: S3a typed semantics and reference values

## Rubric

| Criterion | Objective | Points |
| --- | --- | ---: |
| Declaration namespaces and exact-name uniqueness | ORG-201-01 | 25 |
| `Int` and `Word[8]` semantic boundaries | ORG-201-02 | 25 |
| Typed Reference Core and exact `eval` evidence | ORG-201-03 | 25 |
| Reproducibility, accepted pre-alpha status, and nonclaim discipline | ORG-201-04 | 25 |
| **Total** |  | **100** |

## Critical criteria

All of the following critical gates are mandatory regardless of total score:

- The compiler is built from an archive resolving exactly to
  `ee0fa66d3d38af5e8e10adaa67555b1f0cebc6f6`; build output does not modify the
  Orange source repository.
- Same-kind duplicate `spec` and duplicate `impl` cases fail with `ORC0201`,
  while both source orders of a same-spelled cross-kind pair pass without any
  claimed linking, matching, call, or conformance relationship.
- Accepted and rejected `Int` and `Word[8]` boundaries are correct, including
  negative-zero normalization for `Int`, rejection of negative zero for
  `Word[8]`, exact width spelling, and rejection above `255`.
- Expected command arguments, status, standard output, and standard error are
  recorded before every execution; actual streams are captured separately.
- Successful `eval` values match a prewritten expected file byte for byte in
  typed-spec source order, with normalized decimal `Int` and two-digit
  lowercase hexadecimal `Word[8]` rendering.
- Empty-Core `eval` writes zero bytes, and a rejected `eval` returns status `1`
  with no partial values even when valid typed specifications precede the
  failure.
- The Typed Reference Core is described as internal and noncanonical. No
  refinement, proof, serialization, stable-ID, artifact-identity, codegen,
  compilation, target, security, compatibility, release, or production claim
  is inferred.

## Scoring

- **23–25 namespace points:** every pairing, order, empty/typed collision, and
  `ORC0201` result is correct; **20–22:** one non-critical explanation is
  incomplete; **0–19:** namespaces are merged, duplicates are misclassified,
  or cross-kind acceptance is promoted into a relationship.
- **23–25 type points:** all type, width, radix, signedness, normalization,
  endpoint, and diagnostic results are correct; **20–22:** one non-critical
  case or rationale is incomplete; **0–19:** `Int` or `Word[8]` behavior is
  materially widened, narrowed, wrapped, or coerced.
- **23–25 Core/evaluation points:** inclusion, source order, exact rendering,
  empty Core, all-or-nothing failure, and repeatability are fully evidenced;
  **20–22:** one non-critical evidence field is incomplete; **0–19:** output is
  not predicted byte for byte, empty declarations are assigned values, or a
  rejected source is treated as partially evaluable.
- **23–25 discipline points:** identity and streams are reproducible, accepted
  pre-alpha S3a and incomplete-S3 status are accurate, and every nonclaim
  boundary is explicit;
  **20–22:** one non-critical exclusion or provenance field is incomplete;
  **0–19:** evidence is unpinned, OEP-0003 is called final, the Core is called
  canonical, or an unsupported proof, codegen, security, release, or production
  claim is made.

A passing result is at least **80/100** and satisfies every critical gate.

## Feedback and retry

Feedback identifies the first wrong namespace key, type boundary, expected
value byte, stream assertion, or claim-matrix classification. A retry uses new
names and literal spellings for every failed case, preserves new predictions
before execution, and explains why the earlier reasoning crossed the S3a
boundary. Compiler identity and all critical gates are checked again.
