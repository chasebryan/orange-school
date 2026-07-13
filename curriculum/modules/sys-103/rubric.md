# Rubric: independent native artifact and ABI audit

## Rubric

The assessment is worth 100 points. A passing score is at least 80/100 and all
critical criteria must pass.

| Criterion | Points | Evidence required |
| --- | ---: | --- |
| Translation units, objects, and linking | 20 | Correct artifact graph; separate compilation; definitions, references, relocations, archive/direct-object selection, final links, and static/dynamic distinctions grounded in observed artifacts |
| Target ABI and layout | 25 | Exact target/tool record; fixed-width boundary rationale; C/Rust size, alignment, and every offset for both structures; padding analysis; calling-convention and guarantee/observation distinction |
| FFI ownership, failure, and unwinding | 30 | Bounded C contract; validation before access; unchanged error output; safe Rust API; one narrow unsafe call; complete assumption ledger; fail-closed status/result handling; no pointer escape or unwind |
| Tests and failure-sensitive evidence | 15 | Positive, endpoint, checked-invalid, maximum-length, missing-definition link, harmless layout mismatch, hostile provider, restored pass, and immediate status/channel evidence |
| Reproducibility and evidence limits | 10 | Fresh temporary build; capability detection; exact sources, hashes, versions, target, commands, outputs, statuses, bounds, optional-tool gaps, and explicit non-Orange/non-portability limits |
| **Total** | **100** |  |

## Critical criteria

All four critical criteria must pass:

1. **Artifact and link integrity:** earn at least 16/20 for translation units,
   objects, and linking. The submission must keep provider, probe, and consumer
   translation units separate; distinguish compile from link; bind the intended
   definition; and preserve an observed unresolved-symbol link failure.
2. **ABI compatibility integrity:** earn at least 20/25 for target ABI and
   layout. C and Rust must agree on size, alignment, and every field offset for
   both structures on the recorded target. The submission must not call
   <code>repr(Rust)</code> C-compatible, treat observed padding as universal,
   or claim fixed width alone proves the calling ABI.
3. **Boundary safety:** earn at least 24/30 for FFI ownership, failure, and
   unwinding. C must validate before access and preserve output on failure. The
   safe wrapper must expose no raw pointer, reject before unsafe entry, contain
   one justified call, retain ownership, validate success output, fail closed
   on unknown status, and forbid pointer escape and unwinding.
4. **Failure-sensitive evidence:** earn at least 12/15 for tests and evidence.
   Required normal, exact endpoint, checked-invalid, missing-definition,
   harmless-layout-mismatch, hostile-provider, and restored-pass cases must be
   observed and preserved. Undefined behavior is never an acceptable negative
   test.

A total of 80/100 or more cannot compensate for a failed critical criterion.
Any unsupported claim that one target build proves another target or Orange
behavior fails the reproducibility criterion.

## Scoring

- **Translation units, objects, and linking (20):** 5 points for an exact
  source-to-object-to-executable graph; 5 for definitions, unresolved
  references, and relocations; 5 for correct archive/direct-object linking and
  intended-provider identity; and 5 for distinguishing C linkage, symbol
  visibility, static archives, and observed dynamic metadata.
- **Target ABI and layout (25):** 5 points for exact compilers, flags, target,
  and ABI scope; 8 for matching sizes, alignments, and every request offset; 6
  for the independent padding-witness comparison; and 6 for accurate
  fixed-width, calling-convention, language-guarantee, and target-observation
  reasoning.
- **FFI ownership, failure, and unwinding (30):** 8 points for C validation
  order, bounds, status meanings, and unchanged output; 7 for the prevalidating
  safe Rust API and correct optional-result translation; 10 for the complete
  numbered artifact/type/pointer/lifetime/aliasing/output/retention/callback
  assumption ledger; and 5 for unknown/impossible-result failure plus explicit
  panic/unwind policy.
- **Tests and failure-sensitive evidence (15):** 6 points for normal, absent,
  empty, exact-24, 25th-value, numeric endpoint, field, pointer, and preserved
  output cases; 3 for missing-definition link evidence; 2 for harmless layout
  mismatch evidence; 2 for hostile-provider result validation; and 2 for clean
  restored reruns.
- **Reproducibility and limits (10):** 4 points for a fresh offline temporary
  build and capability-aware optional tools; 3 for source/artifact hashes,
  exact commands, versions, target, stdout, stderr, and statuses; and 3 for the
  24-item work bound, evidence taxonomy, inspection gaps, and explicit
  non-Orange/non-cross-target limits.

Pass only with at least 80/100 and every critical criterion.

## Feedback and retry

Feedback identifies the first incorrect artifact edge, unresolved or multiply
defined symbol, incompatible layout measurement, unsafe pointer premise,
unchecked status/result, unwind gap, missing endpoint, or unsupported evidence
claim and maps it to **SYS-103-01**, **SYS-103-02**, **SYS-103-03**, or
**SYS-103-04**. Preserve the original sources, object hashes, commands, failed
outputs, and target record before making a correction.

A retry uses an assessor-selected field order, payload bound, status value, or
additional translation unit. It must build in a new temporary directory,
recompute every affected layout and artifact hash, rerun the raw C and safe Rust
cases, reproduce at least one safe deliberate failure, and update the artifact
graph and assumption ledger. Prose changes alone cannot replace executable
evidence for a failed link, layout, boundary, endpoint, or fail-closed
criterion.
