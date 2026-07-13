# Assessment: S3a typed semantics and reference values

## Instructions

Complete the knowledge check without consulting the lesson. Then build the
exact archived Orange revision and create fresh sources under the disposable
assessment directory. Do not copy or alter the catalog examples. Record every
expected status and stream condition before execution; keep incorrect
predictions visible beside corrections.

A passing submission earns at least 80/100 and satisfies every critical gate
in `rubric.md`.

## Knowledge check

1. **ORG-201-01:** Define the declaration key used for uniqueness. Predict the
   result of every order and pairing of same-spelled `spec` and `impl`
   declarations, including an empty `spec` beside a typed `spec`. State exactly
   what cross-kind acceptance does and does not mean.
2. **ORG-201-02:** For each source form, give acceptance or the first stable
   semantic code and, when accepted, the normalized value:
   `Int { -0x0 }`, `Int { -0b1010 }`, `Word[8] { 0 }`,
   `Word[8] { 0xff }`, `Word[8] { -0 }`, `Word[8] { 256 }`,
   `Word[08] { 1 }`, `Int[8] { 1 }`, and `Byte { 1 }`.
3. **ORG-201-03:** State which declarations enter the Typed Reference Core,
   how their internal IDs and order are determined, and the exact line formats
   for `Int` and `Word[8]`. Explain empty-Core and rejected-source output.
4. **ORG-201-04:** Contrast silent `orangec check` success with successful
   `orangec eval`. List at least ten unsupported claims, including one from
   each of these groups: language expressiveness, spec/impl relationship,
   formal assurance, Core/artifact identity, code generation, security, and
   release or production readiness.

## Independent task

Archive and build revision
`ee0fa66d3d38af5e8e10adaa67555b1f0cebc6f6` without writing to the Orange
source repository. Submit the resolved identity, compiler version, build
command, and assessment-directory path.

Author one small module per boundary unless a combined case is explicitly
required. Your conformance set must include:

- accepted `Int` literals in two radices, including negative zero and one
  negative nonzero value;
- accepted `Word[8]` values at `0` and `255`, plus one interior value written
  in a non-decimal radix;
- rejected `Word[8]` negative zero and value `256`;
- rejected unsupported type, exact-width spelling, and `Int`-with-width cases;
- a same-kind duplicate for each declaration kind and same-spelled cross-kind
  declarations in both source orders;
- a source containing empty declarations interleaved with at least five typed
  specifications whose complete `eval` output you predict in source order;
- an empty-Core source; and
- a rejected `eval` source containing accepted typed specifications both
  before and after the failing declaration.

For each case submit:

1. source bytes or a cryptographic digest plus the archived source file;
2. expected command arguments, exit status, standard output, and standard
   error condition recorded before execution;
3. actual command, status, and separately captured streams;
4. the first stable diagnostic code for rejection; and
5. a one-sentence explanation tied to the exact S3a rule.

Compare successful `eval` output byte for byte with a prewritten expected file.
For the rejected `eval`, demonstrate that standard output is empty. Run one
accepted and one rejected case twice and compare status and both complete
streams.

Finish with a claim matrix covering:

- implemented evidence supported by the exact commit;
- accepted pre-alpha S3a specification and OEP status, plus incomplete S3;
- operators, parameters, calls, implementation values, and spec/impl linking;
- inference, refinement, proof checking, and verification;
- canonical Core, stable IDs, serialization, and artifact identity;
- code generation, compilation correctness, target or ABI behavior;
- constant-time and cryptographic correctness; and
- compatibility, supported release, and production readiness.

Every unsupported row must say “not established,” not merely “not observed.”

## Completion criteria

- **ORG-201-01** is complete when kind-separated exact-name uniqueness is
  predicted and demonstrated without inventing a cross-kind relationship.
- **ORG-201-02** is complete when the exact contextual types, signedness,
  normalization, width, range, and stable failure codes are correct.
- **ORG-201-03** is complete when Core inclusion, source order, exact rendering,
  empty output, and all-or-nothing failure are predicted and reproduced.
- **ORG-201-04** is complete when compiler identity, streams, statuses, and
  specification status are recorded and all excluded claims remain excluded.
- The submission earns at least 80 points and passes all critical gates.
