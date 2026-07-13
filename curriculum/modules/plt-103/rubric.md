# Rubric: independent Mica compiler pipeline

## Rubric

The assessment is worth 100 points.

| Criterion | Points | Evidence required |
| --- | ---: | --- |
| Source semantics and lowering | 25 | Independent Mica source contract, scope/types/eager semantics, complete bounds, lowerer invariants, deterministic typed IR, and no partial output |
| IR and artifact integrity | 25 | Single-assignment/use-before-definition validation, exact opcode fields, fixed 14/18-byte layout, all decoder checks, canonical round trip, and validated execution |
| Preservation and boundary evidence | 30 | Hand trace, exact endpoints/one beyond, invalid/corruption cases, 50-case source-to-artifact table, metamorphic relations, matched overflow, and four mutation/restoration pairs |
| Reproducibility and claim discipline | 20 | Temporary isolation, hashes, commands, channels, immediate statuses, resource calculations, evidence classification, and explicit non-claims |
| **Total** | **100** |  |

## Critical criteria

All four critical criteria must pass:

1. **Semantic and lowering integrity:** earn at least 20/25 for source semantics
   and lowering. Scope, types, eager <code>Decide</code>, checked subtraction,
   every source bound, and the returned type/register invariant must agree;
   statically invalid or over-bound source cannot yield IR or an artifact;
   checked arithmetic overflow is the separately matched runtime-failure case.
2. **IR trust-boundary integrity:** earn at least 12/15 of the IR/artifact
   points attributable to IR validation. Destinations must be single,
   contiguous definitions; every operand must be prior and correctly typed;
   every execution and encoding path must revalidate; malformed IR cannot run.
3. **Artifact integrity:** earn at least 8/10 of the IR/artifact points
   attributable to the byte format. Header, records, byte order, exact length,
   sentinels, unused/reserved fields, ordinals, decoded validation, and
   canonical round trip must be enforced at endpoints and under mutation.
4. **Failure-sensitive preservation evidence:** earn at least 24/30 for
   preservation and boundary evidence. The exact/one-beyond cases, 50-case
   table, two metamorphic relations, explicit overflow matching, and all four
   observed failing/restored mutation pairs are required.

A total of 80/100 or more cannot compensate for a failed critical criterion.

## Scoring

- **Source semantics and lowering (25):** 7 for exact source rules and
  independent reference semantics; 6 for lexical scope, type diagnostics, and
  eager behavior; 7 for node/depth/binding/name/instruction caps checked before
  excess work; and 5 for complete lowering invariants and deterministic output.
- **IR and artifact integrity (25):** 8 for exact program/instruction shape and
  contiguous SSA validation; 7 for operand, type, opcode, unused-field, and
  result validation at every trust boundary; 6 for the exact 14/18-byte format,
  length, limits, byte order, sentinels, ordinals, and corruption rejection;
  and 4 for validated execution and canonical decode/re-encode.
- **Preservation and boundary evidence (30):** 6 for a complete hand trace and
  exact instruction/artifact assertions; 7 for isolated endpoints and one
  beyond; 5 for source/type/IR/artifact invalid cases; 7 for the 50-case table,
  overflow classification, and two metamorphic relations; and 5 for all four
  observed mutation/restoration pairs.
- **Reproducibility and claim discipline (20):** 7 for a fresh absolute
  temporary path, Python version, source hashes, commands, channels, and
  immediate statuses; 5 for exact size and justified asymptotic resource
  bounds; 4 for the specification/observation/inference/unsupported matrix;
  and 4 for precise preservation and Orange non-claims.

Pass only with at least 80/100 and all critical criteria.

## Feedback and retry

Feedback identifies the first incorrect source rule, scope edge, typing edge,
unchecked counter, destination, operand, opcode field, byte offset, count,
ordinal, equivalence case, mutation record, or unsupported statement and maps
it to **PLT-103-01**, **PLT-103-02**, or **PLT-103-03**. Preserve the original
submission and evidence before correcting it.

A retry changes the source arithmetic and comparison operators, all four
bounds, the artifact magic/version, at least three field widths or positions,
and ten assessor-selected table cases. The learner must recalculate source
trees, instruction endpoints, artifact sizes, byte mutations, semantic
relations, and resource claims. Revised prose cannot replace executable
evidence for a failed semantic, lowering, validation, encoding, decoding,
equivalence, or failure-sensitivity criterion.
