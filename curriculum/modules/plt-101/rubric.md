# Rubric: independent Chalk language frontend

## Rubric

The assessment is worth 100 points.

| Criterion | Points | Evidence required |
| --- | ---: | --- |
| Source and lexical contract | 20 | Exact UTF-8/source-position policy, token rules, immutable records, deterministic diagnostics, spelling and source/token caps, and strict invalid-input behavior |
| Grammar, precedence, and AST | 25 | Chalk grammar implemented independently, correct precedence/associativity, concrete-versus-abstract explanation, complete AST shape, and no invented syntax |
| Bounds and recovery integrity | 20 | Enforced source/token/depth/node/diagnostic caps, progress arguments, bounded synchronization, and complete-or-none program result |
| Test quality and failure sensitivity | 25 | Positive, exact endpoint, one-beyond, malformed, recovery, metamorphic, independent differential, and three observed mutation/recovery pairs |
| Reproducibility and claim discipline | 10 | Temporary workspace, versions, hashes, commands, channels, immediate statuses, honest complexity/storage model, and explicit frontend/Orange non-claims |
| **Total** | **100** |  |

## Critical criteria

All four critical criteria must pass:

1. **Lexical and position integrity:** earn at least 16/20 for source and
   lexical contract. Byte offsets, code-point columns, token boundaries, exact
   limits, and structured diagnostics must agree on valid and invalid input.
2. **Grammar and AST integrity:** earn at least 20/25 for grammar, precedence,
   and AST. The required Chalk grammar, left associativity, precedence, and
   concrete-to-abstract mapping must be correct; malformed syntax cannot
   produce a valid program.
3. **Bounded complete-or-none behavior:** earn at least 16/20 for bounds and
   recovery. Source, tokens, depth, nodes, and diagnostics must be capped before
   excess work/retention; recovery must progress and must never expose a partial
   executable AST.
4. **Failure-sensitive evidence:** earn at least 20/25 for tests. Exact
   endpoints and one-beyond cases, invalid/recovery cases, metamorphic and
   independent differential checks, and all three observed deliberate failures
   with restored passes are required.

A total of 80/100 or more cannot compensate for a failed critical criterion.

## Scoring

- **Source and lexical contract (20):** 5 for strict UTF-8 and exact position
  units; 6 for token and spelling rules; 5 for deterministic diagnostic fields;
  and 4 for source/token/spelling endpoint enforcement.
- **Grammar, precedence, and AST (25):** 8 for the exact grammar and complete
  consumption; 7 for precedence/associativity; 6 for immutable AST design and
  concrete/abstract distinction; and 4 for accurate syntax-only claims.
- **Bounds and recovery integrity (20):** 8 for depth/node checks before excess
  recursion or retention; 6 for bounded diagnostic synchronization and progress;
  and 6 for program absence on every lexical or parse diagnostic.
- **Test quality and failure sensitivity (25):** 7 for positive and exact
  endpoints; 6 for one-beyond, malformed, and multiple-error recovery; 6 for
  meaningful metamorphic and independent differential cases; and 6 for three
  preserved deliberate-failure/restored-pass pairs.
- **Reproducibility and claim discipline (10):** 5 for temporary path, version,
  hashes, commands, stdout, stderr, and statuses; 3 for justified complexity and
  honest Python storage limits; and 2 for independence and Orange non-claims.

Pass only with at least 80/100 and all critical criteria.

## Feedback and retry

Feedback identifies the first incorrect source unit, token boundary, precedence
edge, unchecked cap, non-progress recovery path, partial-AST escape, unstable
diagnostic, missing endpoint, or unsupported claim and maps it to
**PLT-101-01**, **PLT-101-02**, or **PLT-101-03**. Preserve the original
submission and its evidence before correcting it.

A retry uses fresh keywords and a new two-character binding token, swaps braces
for another assessor-selected grouping pair, changes every numeric bound, and
adds two assessor-selected malformed streams. The learner must recalculate
endpoint programs, source byte positions, token/node counts, differential
overlap, and complexity statements. Revised prose cannot replace executable
evidence for a failed lexer, parser, bound, recovery, diagnostic, or test
criterion.
