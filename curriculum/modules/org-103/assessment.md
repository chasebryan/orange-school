# Assessment: Orange 2026 grammar and phase-aware conformance

## Instructions

Complete the knowledge check without consulting the lesson. Then archive and
build the exact canonical revision for an independent conformance task. Record
each lexical, syntactic, and semantic prediction before running the compiler.
Corrections are allowed only when the original prediction remains visible and
the revised phase reasoning is explained.

A passing submission earns at least 80/100 and meets every critical criterion
in `rubric.md`.

## Knowledge check

1. **ORG-103-01:** Write the complete Orange 2026 grammar as eight production
   rules. Explain the exact edition spelling, the only repetition, both `spec`
   tails, the optional type width, and the optional literal sign.
2. **ORG-103-02:** For each change, predict lexical validity, syntactic
   validity, semantic validity when reached, and the first stable diagnostic
   family: missing edition semicolon, `edition 2_026;`, reserved module name,
   one parameter, typed `impl`, `Byte`, `Word[08]`, negative `Word[8]`, two
   same-kind names, same-spelled cross-kind names, and a second module.
3. **ORG-103-03:** Explain the evidence meaning of (a) a recovered tree with
   parser diagnostics, (b) a semantic diagnostic such as `ORC0203`, and (c)
   silent `check` success. For each, state what it supports and why it
   establishes no parser-correctness proof, implementation execution,
   refinement, proof checking, code generation, constant-time property, or
   cryptographic correctness.

## Independent task

Build canonical revision `ee0fa66d3d38af5e8e10adaa67555b1f0cebc6f6`
from a disposable Git archive, leaving the Orange source repository unchanged.
Submit the resolved identity, compiler version, archive/build commands, and
evidence-directory path.

Create fresh cases rather than copying the catalog examples. Include:

- three accepted sources covering an empty module, both legacy empty
  declarations, and every typed grammar component with mixed integer radices;
- one rejection at the edition boundary;
- two distinct declaration-shape parser rejections, including typed `impl`;
- one reserved-name or reserved-declaration parser rejection;
- one trailing-source parser rejection;
- three syntactically valid but semantically rejected type or literal forms;
- one same-kind duplicate semantic rejection; and
- one same-spelled cross-kind pair that passes all `check` gates.

For every case submit the source bytes or digest, predicted result at each
reached phase, predicted first code, exact command, actual status, and separately
captured standard output and standard error. Run one accepted source, one
parser rejection, and one semantic rejection twice and compare the complete
results.

Finish with two artifacts:

1. an annotation of every token and grammar production used by the richest
   accepted source; and
2. a claim matrix containing source identity, lexical validity, syntactic
   validity, S3a semantic validity, Typed Reference Core construction,
   reference values, implementation execution, proof or refinement, canonical
   Core identity, generated code, and cryptographic correctness.

The matrix must distinguish parser-only evidence from complete `check`
evidence and must not treat any rejected source as partially accepted.

## Completion criteria

- **ORG-103-01** is complete when all eight productions and their exact
  repetition, alternatives, and optionals are correct.
- **ORG-103-02** is complete when positive and negative cases cover distinct
  grammar boundaries and correctly route parser-shaped versus semantic-shaped
  failures.
- **ORG-103-03** is complete when recovery, parser success, semantic failure,
  and full `check` success are scoped precisely without stronger claims.
- Predictions precede execution; statuses and streams are preserved and
  repeatable at the canonical revision.
- The submission earns at least 80 points and passes all critical criteria.
