# Rubric: independent owned-region transfer

## Rubric

The assessment is worth 100 points. A passing score is at least 80/100.

| Criterion | Points | Evidence required |
| --- | ---: | --- |
| C lifetime, allocation, and provenance | 20 | Accurate storage/lifetime traces, allocation state machine, validation order, original-base release, and precise undefined-behavior boundaries |
| Rust ownership, borrowing, and slices | 20 | One owner, valid moves, nonoverlapping shared/exclusive access, bounded construction, raw-slice premises, and compile-fail alias evidence |
| Bounded C implementation and tests | 20 | Correct import/count/scrub/release behavior plus empty, normal, exact-48, over-limit, null, inconsistent-state, unchanged-output, scrub, and reset tests |
| Safe FFI ownership boundary | 25 | Exact declarations, prevalidation, private raw state, fail-closed statuses, allocator pairing, narrow unsafe operations, and complete assumption ledgers |
| Destruction truth and reproducibility | 15 | Selected-region wipe evidence, independent copy inventory, accurate evidence limits, failure/recovery records, exact offline build identities, and Orange non-claim |
| **Total** | **100** |  |

## Critical criteria

All four critical criteria must pass:

1. **Lifetime and provenance integrity:** earn at least 16/20 for C lifetime,
   allocation, and provenance. No submission may claim that non-null plus length
   proves a live allocation, that shape validation discovers arbitrary pointer
   extent, or that invalid release is a recoverable C error.
2. **Ownership and alias integrity:** earn at least 16/20 for Rust ownership,
   borrowing, and slices. The wrapper must have one allocation owner, must not
   expose raw state, and must not permit shared and exclusive access to overlap
   through its safe API.
3. **Allocation and FFI integrity:** earn at least 16/20 for the bounded C
   implementation and at least 20/25 for the safe FFI boundary. Allocation must
   transfer only on success; failure must preserve owners and outputs; release
   must use the original matching base exactly once; unknown statuses must fail
   closed; and every unsafe operation must have its required premises.
4. **Destruction-claim integrity:** earn at least 12/15 for destruction truth
   and reproducibility. The submission must explicitly deny that one source
   wipe, volatile store, zero readback, destructor, or <code>free</code> proves
   all copies or physical representations were erased, and it must preserve
   both deliberate failures and corrected reruns.

A total of 80 or more cannot compensate for a failed critical criterion.

## Scoring

- **C lifetime, allocation, and provenance (20):** 5 for storage-duration and
  lifetime distinctions; 6 for import/success/failure/release ownership traces;
  5 for original-base, extent, and effective-access requirements; and 4 for
  precise undefined-behavior classification.
- **Rust ownership, borrowing, and slices (20):** 5 for moves and one-owner
  design; 5 for shared/exclusive borrowing and mutation; 6 for raw slice,
  null-empty, allocation, alignment, initialization, lifetime, and provenance
  premises; and 4 for observed compile-fail and corrected borrow evidence.
- **Bounded C implementation and tests (20):** 6 for validation and unchanged
  failure state; 5 for allocation and counting; 4 for scrub/release/reset; and
  5 for positive, empty, exact-48, length-49, null, occupied, inconsistent, and
  deliberate-failure cases.
- **Safe FFI ownership boundary (25):** 5 for exact C layout and declarations;
  5 for prevalidation/private raw state; 5 for status and output handling; 5
  for transfer, allocator pairing, Drop, and explicit release; and 5 for local
  unsafe ledgers covering every listed premise.
- **Destruction truth and reproducibility (15):** 5 for selected-allocation
  scrub/readback and unchanged-source observations; 4 for copy inventory and
  NIST-calibrated limits; 3 for exact versions, target, hashes, commands,
  channels, and statuses; and 3 for contained offline builds, model bounds, and
  explicit Orange non-claim.

Pass only with at least 80/100 and all critical criteria.

## Feedback and retry

Feedback identifies the first false lifetime premise, ownership duplication,
overlapping safe alias, unchecked allocation transition, missing unsafe
obligation, unobserved failure, or overstated destruction claim and maps it to
one of <code>SYS-102-01</code> through <code>SYS-102-04</code>. Preserve the
original submission and evidence before adding a correction record.

A retry uses an assessor-selected maximum from 24 through 64, a different
status-number assignment, a different counting target, and at least one new
invalid descriptor shape. Recalculate bounds, regenerate the C/Rust boundary,
and rerun all affected positive, endpoint, invalid, compile-fail, runtime-fail,
scrub, and release cases in a fresh workspace. Prose changes alone cannot
replace executable evidence for a failed lifetime, alias, FFI, allocation, or
destruction criterion.
