# Rubric: portable image-row dispatch

## Rubric

The assessment is worth 100 points.

| Criterion | Points | Evidence required |
| --- | ---: | --- |
| Target and artifact integrity | 25 | Complete validated tuple, exact toolchain/configuration, correct ISA/ABI/OS/object-format distinctions, and every claim classified by evidence source |
| SIMD semantic correctness | 20 | Correct u8 lane count and saturating behavior, alignment/bounds/tail/reduction analysis, strict model, and positive/endpoint/invalid tests without a code-generation claim |
| Baseline and dispatch safety | 25 | Bounded C17 baseline, mandatory feature-free fallback, complete build/runtime truth table, largest eligible vector-width selection with separate lane semantics, tuple match, and no unsupported instruction path |
| Build, cross-target, and failure evidence | 20 | Native compile/link/run, artifact hash and inspection, honest non-host attempt/matrix, four observed deliberate failures, and restored pass |
| Reproducibility and communication | 10 | Temporary-only workspace, hashes, exact commands/channels/statuses, resource bounds, readable independent work, and guarantee-versus-observation language |
| **Total** | **100** |  |

## Critical criteria

All four critical criteria must pass:

1. **Artifact identity:** earn at least 20/25 for target and artifact integrity.
   The native tuple must separate target, ISA, ABI, OS, object format,
   endianness, and pointer width, and no observation may be promoted to a
   language guarantee.
2. **Operation integrity:** earn at least 16/20 for SIMD semantic correctness.
   Sixteen u8 lanes must use per-lane saturation, with bounds and tail handling
   explicit; wrapping or cross-lane carry is a failure.
3. **Unsupported-feature exclusion:** earn at least 20/25 for baseline and
   dispatch safety. A feature-free baseline must remain reachable, and every
   accelerated result must require both built inclusion and all positive
   runtime evidence for the matching tuple. Executing an unchecked optional
   instruction fails the assessment.
4. **Failure-sensitive portability evidence:** earn at least 16/20 for build,
   cross-target, and failure evidence. Native behavior, artifact inspection,
   cross-target status, and all four deliberate failures/restorations must be
   preserved without inventing a build, link, or run result.

A total of 80 or more cannot compensate for a failed critical criterion.

## Scoring

- **Target and artifact integrity (25):** 10 for validated tuple and toolchain;
  8 for correct conceptual distinctions; 4 for evidence classification; and 3
  for rejecting invalid metadata and tuple mismatch.
- **SIMD semantics (20):** 8 for exact lane/saturation behavior; 4 for strict
  input validation; 5 for alignment, bounds, tails, and reductions; and 3 for
  positive, endpoint, and invalid model tests.
- **Baseline and dispatch (25):** 8 for bounded C17 correctness; 9 for complete
  fail-closed dispatch and baseline; 5 for widest-eligible and tail tests; and 3
  for accurate build-time versus runtime reasoning.
- **Build, cross-target, and failures (20):** 6 for native build/link/run; 4 for
  hashed inspection; 5 for capability matrix and honest non-host evidence; and
  5 for the four deliberate failures and restored run.
- **Reproducibility (10):** 5 for exact commands, channels, immediate statuses,
  hashes, and temporary containment; 3 for resource/evidence limits; and 2 for
  clear independent implementation and precise claims.

Pass only with at least 80/100 and all critical criteria.

## Feedback and retry

Feedback identifies the first tuple conflation, lane-semantic error, unchecked
feature path, missing endpoint, cross-target overclaim, or unobserved failure
and maps it to one SYS-104 outcome. Preserve the original submission and failed
evidence before making corrections.

A retry uses 32 saturating u16 lanes, a 2,048-element bound, two assessor-chosen
feature requirement sets, and a different non-host target. The learner must
recalculate vector widths and tails, regenerate the artifact tuples and hashes,
and repeat native, cross-target, inspection, invalid, and failure-sensitive
evidence. Prose changes cannot replace an executable or observed requirement.
