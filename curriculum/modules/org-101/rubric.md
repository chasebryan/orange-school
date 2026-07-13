# Rubric: pin and run Orange Today

## Rubric

| Criterion | Objective | Points |
| --- | --- | ---: |
| Exact repository, archive, and Rust identity | ORG-101-01 | 30 |
| Reproducible `check` and `eval` evidence | ORG-101-02 | 35 |
| Accurate S3a boundary and explicit non-claims | ORG-101-03 | 35 |
| **Total** |  | **100** |

## Critical criteria

All of the following are mandatory regardless of total points:

- The submission resolves revision
  `ee0fa66d3d38af5e8e10adaa67555b1f0cebc6f6` and uses Rust `1.96.1`, or
  reports the exact identity blocker.
- Compiler input is extracted from that exact commit into a fresh archive
  directory. No command fetches into, checks out, resets, cleans, or builds
  inside the Orange source repository.
- The accepted-source `check` observation includes status `0`, explicitly
  records empty standard output and standard error, and names lexing, parsing,
  bounded semantic validation, and Typed Reference Core construction.
- The accepted-source `eval` observation includes status `0`, empty standard
  error, and exact normalized value lines in source order.
- The submission describes `eval` as closed-literal reference evaluation, not
  general program execution.
- The claim record identifies only a bounded pre-alpha S3a capability and does
  not claim proof checking, verified lowering, canonical Core, code generation,
  target/ABI behavior, cryptographic assurance, stable compatibility, or
  production readiness.
- The archived snapshot is not represented as a supported release or as
  permission to redistribute Orange source or binaries.

## Scoring

- **27–30 identity points:** full commit, Rust toolchain, exact archive command,
  and fresh snapshot path are correctly recorded; **20–26:** one non-critical
  identity detail is incomplete; **0–19:** the compiler input identity is not
  established or the source repository is rewritten.
- **32–35 evidence points:** source and digest, exact commands, both output
  streams, statuses, prediction, and source-ordered `eval` values are
  reproducible; **24–31:** the runs are valid but one non-critical record field
  is incomplete; **0–23:** semantic acceptance or reference evaluation is not
  independently demonstrated.
- **32–35 boundary points:** the supported claims name the exact `check` and
  `eval` surfaces and at least six non-capabilities are accurate; **24–31:** the
  S3a scope is correct with at least four accurate non-capabilities; **0–23:**
  the claim crosses into unsupported execution, proof, compilation, canonical
  Core, target, release, or production behavior.

A passing result is at least **80/100** and satisfies every critical criterion.

## Feedback and retry

Feedback names the missing identity, command evidence, output record, or claim
boundary. For a retry, create a new assessment source with fresh ASCII names and
different accepted literals, archive the same exact revision into a new
temporary directory, and rerun. If identity verification was blocked, retry
only after the exact object or toolchain is provisioned; do not alter a shared
Orange repository to conceal the blocker.
