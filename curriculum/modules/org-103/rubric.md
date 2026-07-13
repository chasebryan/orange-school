# Rubric: Orange 2026 grammar and phase-aware conformance

## Rubric

| Criterion | Objective | Points |
| --- | --- | ---: |
| Complete additive grammar and production boundaries | ORG-103-01 | 30 |
| Positive, parser-negative, semantic-negative, and repeatable evidence | ORG-103-02 | 40 |
| Recovery, phase, and nonclaim discipline | ORG-103-03 | 30 |
| **Total** |  | **100** |

## Critical criteria

All of the following are mandatory:

- The compiler comes from a disposable archive resolving exactly to
  `ee0fa66d3d38af5e8e10adaa67555b1f0cebc6f6`; no build output modifies the
  Orange source repository.
- All eight productions admit exactly one edition declaration, one module,
  zero or more declarations, legacy empty `spec` and `impl`, and the single
  typed-literal alternative on `spec` only.
- At least one typed accepted source, three distinct parser rejections, and
  three syntactically valid semantic rejections are predicted before execution
  and demonstrated with the correct statuses, streams, and code families.
- A typed `impl` is classified as a parser rejection. Generic `parsed_type`
  syntax is not confused with support for arbitrary types or widths.
- Same-kind duplicate syntax reaches semantic `ORC0201`, while a same-spelled
  cross-kind pair passes without any claimed linking or conformance relation.
- Parser recovery is never accepted. A semantic diagnostic creates no partial
  accepted Core. Silent `check` success is correctly described as lexical,
  syntactic, semantic, and Core-construction success for the narrow S3a slice.
- No result is described as general expression support, implementation
  execution, reference evaluation, refinement, proof checking, canonical Core,
  code generation, constant-time evidence, cryptographic correctness, or
  production readiness.

## Scoring

- **27–30 grammar points:** every production and exact boundary is correct;
  **24–26:** one non-critical notation or explanation error; **0–23:** the
  accepted grammar is materially widened, narrowed, or left at the old empty-
  body-only form.
- **36–40 conformance points:** accepted, parser-negative, semantic-negative,
  prediction, stream, status, code, and repeatability evidence are complete;
  **32–35:** one non-critical evidence field is incomplete; **0–31:** failures
  are not routed by phase or distinct boundaries are not demonstrated.
- **27–30 discipline points:** recovery, parser success, semantic failure,
  current `check`, and the claim matrix are precise; **24–26:** one
  non-critical exclusion is missing; **0–23:** parse evidence is promoted to
  semantics, `check` is called parser-only, or any unsupported execution,
  proof, codegen, security, or production claim is made.

A passing result is at least **80/100** and satisfies every critical criterion.

## Feedback and retry

Feedback identifies the first production, phase transition, expected code, or
claim-matrix boundary that is wrong. A retry uses fresh source variants for
every failed boundary, preserves new predictions before execution, and
explains why the original reasoning crossed or missed the lexical, parser, or
semantic gate.
