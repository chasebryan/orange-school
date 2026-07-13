# Rubric: bounded first-match FFI

## Rubric

The assessment is worth 100 points.

| Criterion | Points | Evidence required |
| --- | ---: | --- |
| C memory and Rust ownership comparison | 25 | Accurate normal and invalid traces covering pointer, lifetime, bounds, borrow, aliasing, state, reads, writes, and results |
| Bounded C and Rust implementations | 30 | Correct contracts, validation order, success/absence/error behavior, unchanged error output, and normal/boundary/invalid tests |
| Narrow FFI and unsafe assumptions | 35 | Exact declaration, prevalidation, safe API, result/status checks, one narrow unsafe call, complete assumption ledger, and fail-closed mapping |
| Reproducible host evidence | 10 | Fresh build, exact tools/target/sources/commands/channels/statuses, no external effects, evidence limits, and Orange non-claim |
| **Total** | **100** |  |

## Critical criteria

All three critical criteria must pass:

1. **Memory-contract accuracy:** earn at least 20/25. The submission must not
   claim that non-null proves validity, that C checks arbitrary pointer extent,
   or that Rust ownership enforces the application length limit.
2. **Bounded failure safety:** earn at least 24/30. C must validate before
   dereferencing and leave output unchanged on failure; Rust must reject
   oversized input explicitly; all required normal, boundary, and invalid tests
   must pass.
3. **Unsafe-boundary integrity:** earn at least 28/35. The wrapper must expose
   no raw pointer, contain one justified unsafe call, validate before entry,
   reject impossible output, map unknown statuses to error, and document every
   listed ABI, pointer, lifetime, aliasing, output, retention, callback,
   constant, status, and artifact assumption.

Any unsupported claim that these host tests establish Orange behavior fails
the reproducible-evidence criterion. A score of 80 or more cannot compensate
for a failed critical criterion.

## Scoring

- **Comparison (25):** 10 for C traces, 8 for Rust traces, and 7 for a precise
  side-by-side contract comparison including unconstructible safe-Rust states.
- **Implementations (30):** 10 for C contract and validation, 8 for safe Rust
  result behavior, and 12 for normal, empty, exact-32, oversized, null, absent,
  and unchanged-output tests.
- **FFI (35):** 7 for exact declaration and types, 7 for prevalidation and safe
  wrapper API, 7 for status/index fail-closed logic, and 14 for a complete
  numbered unsafe-assumption ledger adjacent to the call.
- **Evidence (10):** 4 for a contained deterministic build, 3 for exact
  versions/sources/commands/observations, and 3 for evidence limits and an
  explicit Orange non-claim.

Pass only with at least 80/100 and all critical criteria.

## Feedback and retry

Feedback identifies the first invalid memory premise, unchecked bound,
incorrect status/index transition, missing unsafe assumption, or unsupported
evidence claim and maps it to an outcome ID. Preserve the original trace,
source, build record, and test output; add a correction record.

A retry uses a fresh maximum or target sequence supplied by the assessor and a
new temporary build. Rerun every affected C, safe-Rust, and FFI test including
at least one raw-C invalid case. Revised prose alone cannot replace executable
evidence for a failed bound, FFI, or build criterion.
