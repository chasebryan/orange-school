# Rubric: bounded operation-log records

## Rubric

The assessment is worth 100 points.

| Criterion | Points | Evidence required |
| --- | ---: | --- |
| Fixed-width representation | 20 | Correct u16/i16 ranges, two's-complement interpretation, exact bit/hex forms, explicit endian conversion, and value-versus-pattern explanation |
| Arithmetic, shifts, and conversions | 20 | Separately correct checked, wrapping, and saturating addition; bounded shifts; checked conversions; and contract-based policy justification |
| Record and stream correctness | 30 | Canonical independent codec, strict field validation, subtraction-first span checks, no truncation/trailing/partial acceptance, and correct 0–32 record behavior |
| Bounds and failure-sensitive tests | 20 | Concrete byte/record/work/storage budgets plus positive, endpoints, invalid inputs, maximum stream, and preserved deliberate-failure/recovery evidence |
| Reproducibility and semantic accuracy | 10 | Environment, path, hashes, commands, channels, statuses, readable source, and accurate Python/C17/Rust comparison with source maturity labeled |
| **Total** | **100** |  |

## Critical criteria

All four critical criteria must pass:

1. **Representation integrity:** earn at least 16/20 for fixed-width
   representation. The submission must distinguish mathematical values from
   patterns and correctly handle both signed endpoints and both byte orders.
2. **Explicit operation policy:** earn at least 16/20 for arithmetic, shifts,
   and conversions. Checked, wrapping, and saturating behavior must be separate
   and correct; no accidental Python growth or masking may stand in for an
   unstated policy.
3. **Parser range integrity:** earn at least 24/30 for record and stream
   correctness. Header and subtraction-form range validation must precede
   reads/slices, and malformed input must never return a partial parse.
4. **Bounded failure evidence:** earn at least 16/20 for bounds and tests. Byte
   and record caps, exact maximum cases, invalid cases, and observed deliberate
   failures must all be present.

A total of 80 or more cannot compensate for a failed critical criterion.

## Scoring

- **Fixed-width representation (20):** 5 for range and type validation; 5 for
  exact bit/hex forms; 5 for two's-complement interpretation; and 5 for
  big/little-endian conversion and explanation.
- **Arithmetic, shifts, and conversions (20):** 8 for the three addition modes;
  5 for shift-count and lost-bit checks; 4 for checked conversions; and 3 for
  contract-based policy selection.
- **Record and stream correctness (30):** 10 for canonical single-record
  encoding/decoding; 8 for strict field/type/version/length validation; 8 for
  checked offset progression and complete-failure behavior; and 4 for empty,
  normal, and exact 32-record streams.
- **Bounds and tests (20):** 5 for input and iteration budgets; 5 for honest
  time/storage statements; 6 for positive, endpoint, and invalid tests; and 4
  for preserved deliberate-failure and restored-pass evidence.
- **Reproducibility and accuracy (10):** 5 for version, path, hashes, commands,
  channels, and statuses; 3 for accurate cross-language and source-maturity
  statements; and 2 for readable, independent work and evidence limits.

Pass only with at least 80/100 and all critical criteria.

## Feedback and retry

Feedback identifies the first representation mismatch, unstated arithmetic
policy, unchecked range, parser partial-success path, missing endpoint, or
unsupported semantic claim and maps it to an outcome ID. The learner preserves
the original submission and failed evidence before adding corrections.

A retry uses a fresh magic/version pair, reversed byte order, different payload
cap, and at least one assessor-selected malformed stream. The learner must
recalculate the complete stream budget and update every affected test and
resource statement. Revised prose alone cannot replace executable evidence for
failed arithmetic, range, record, or stream criteria.
