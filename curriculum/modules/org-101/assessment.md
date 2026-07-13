# Assessment: pin and run Orange Today

## Instructions

Work independently from the Orange School repository root. Use the exact
archive procedure from the lab; do not modify or build inside the Orange source
repository. Submit copyable commands, observations, and explanations. A
screenshot alone is not sufficient. This assessment requires at least 80% and
every critical criterion in `rubric.md`.

## Knowledge check

1. **ORG-101-01:** Give the full pinned Orange revision and Rust toolchain
   channel. Explain why resolving and archiving the commit object gives a more
   exact compiler input than either `orangec --version` or an arbitrary working
   tree.
2. **ORG-101-02:** List the phases performed by `orangec check`. State its
   expected standard output, standard error, and status for accepted source,
   then contrast source rejection with a CLI usage error.
3. **ORG-101-03:** Explain the narrow meaning of `orangec eval` in S3a and list
   at least six capabilities that successful `check` and `eval` results do not
   establish. Include proof checking and code generation.

## Independent task

Create a fresh assessment directory outside the Orange source repository. In
it, author one new Orange source with:

- `edition 2026` and a new ASCII module name;
- one empty declaration;
- one `spec` returning an `Int` literal; and
- one later `spec` returning a `Word[8]` literal from 0 through 255.

Use fresh function names and literal values rather than copying the pinned
fixture. Do not modify the catalog example or any file in `ORANGE_REPO`.

Submit:

1. the source text and its `sha256sum` digest;
2. the full resolved commit, `rustc --version`, fresh archive path, and archive
   command;
3. the complete `cargo +1.96.1 run --quiet --locked --offline` commands used to
   invoke both `orangec check` and `orangec eval` with a quoted absolute source
   path;
4. the observed standard output, standard error, and exit status from each
   command;
5. a prediction made before `eval`, followed by a comparison with the exact
   two value lines in source order; and
6. a claim record containing:
   - one sentence describing exactly what silent successful `check` supports;
   - one sentence describing exactly what the `eval` lines support; and
   - at least six explicit non-claims, including arbitrary execution,
     compilation/code generation, proof checking, canonical Core or verified
     lowering, target/ABI behavior, and production readiness.

Also state that this exact capability is a bounded pre-alpha S3a slice used
provisionally by the course, not a supported release or a stable compatibility
promise. Record that unresolved outbound license and working-name decisions do
not authorize redistribution.

If the exact commit object or Rust toolchain is unavailable, submit the exact
blocker instead of fetching into, checking out, cleaning, resetting, or building
inside the Orange source repository.

## Completion criteria

- **ORG-101-01** is complete when revision
  `ee0fa66d3d38af5e8e10adaa67555b1f0cebc6f6`, Rust `1.96.1`, and the fresh
  archive input are recorded without changing the source repository.
- **ORG-101-02** is complete when the fresh valid source is checked with status
  `0`, both empty output streams are recorded, and the conclusion names lexing,
  parsing, bounded semantic validation, and Typed Reference Core construction.
- **ORG-101-03** is complete when the exact source-ordered reference values,
  the bounded pre-alpha S3a identity, and at least six accurate non-capabilities
  are recorded without calling the observation general execution, compilation,
  proof, or production verification.
- The submission earns at least 80 points and passes every critical criterion.
