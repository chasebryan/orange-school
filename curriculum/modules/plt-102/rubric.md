# Rubric: independent Slate static and dynamic semantics

## Rubric

The assessment is worth 100 points.

| Criterion | Points | Evidence required |
| --- | ---: | --- |
| Names, scope, and AST integrity | 20 | Exact immutable Slate AST, name policy, lexical binding, free-name rejection, shadowing, alpha-equivalence, host-field validation, and bounded/cycle-safe traversal |
| Type-and-effect semantics | 25 | Written judgments and faithful checker for every form, exact operand and branch requirements, conservative effect joins, immutable result, and stable static errors |
| Dynamic semantics and resource integrity | 25 | Deterministic left-to-right call-by-value evaluation, selected-branch behavior, exact I32 arithmetic, ordered actual effects, environment/step/note bounds, and stable runtime failures |
| Test quality and failure sensitivity | 20 | Exact endpoints and one-beyond cases, invalid cases, relational properties, independent pure oracle, deterministic repetitions, and five observed mutation/restoration pairs |
| Reproducibility and claim discipline | 10 | Temporary workspace, versions, hashes, commands, channels, immediate statuses, justified complexity/storage model, and explicit theorem/Orange non-claims |
| **Total** | **100** |  |

## Critical criteria

All four critical criteria must pass:

1. **Scope integrity:** earn at least 16/20 for names, scope, and AST integrity.
   Lexical resolution, the binder's scope boundary, shadowing, free-name
   rejection, node/depth/environment limits, and cycle handling must match the
   specification.
2. **Static semantic integrity:** earn at least 20/25 for type-and-effect
   semantics. Every Slate form must implement its declared judgment, reject
   mismatches before evaluation, and conservatively retain potential effects
   from both conditional branches.
3. **Dynamic and bound integrity:** earn at least 20/25 for dynamic semantics.
   Evaluation order, selected branch, I32 behavior, note order, and all bounds
   must be exact; no failure may expose a partial success result.
4. **Failure-sensitive evidence:** earn at least 16/20 for tests. Exact and
   one-beyond limits, invalid paths, relational checks, an actually independent
   oracle, and all five observed deliberate failures with restored passes are
   required.

A total of 80/100 or more cannot compensate for a failed critical criterion.

## Scoring

- **Names, scope, and AST integrity (20):** 6 for the exact frozen AST and field
  checks; 7 for lexical scope, binder boundary, shadowing, and alpha-renaming;
  and 7 for stable name/free-name, visit/depth/environment, unsupported-node,
  and cycle rejection.
- **Type-and-effect semantics (25):** 8 for complete written rules; 9 for a
  faithful syntax-directed checker; 5 for conservative effect joins and
  potential/actual distinction; and 3 for immutable deterministic judgments.
- **Dynamic semantics and resource integrity (25):** 8 for call-by-value order,
  branch choice, and lexical environment; 7 for exact I32 values and overflow;
  6 for ordered notes and step/note caps; and 4 for deterministic failures
  without partial results.
- **Test quality and failure sensitivity (20):** 5 for positive/static/dynamic
  examples; 5 for isolated endpoints, one-beyond, malformed, and deterministic
  cases; 5 for meaningful relations and a separate oracle; and 5 for preserved
  five-pair mutation evidence.
- **Reproducibility and claim discipline (10):** 5 for temporary path, version,
  hashes, exact commands, channels, and immediate statuses; 3 for justified
  time/retention bounds without exact Python-memory claims; and 2 for precise
  model, theorem, and Orange non-claims.

Pass only with at least 80/100 and all critical criteria.

## Feedback and retry

Feedback names the first wrong binding edge, typing premise, effect join,
evaluation-order observation, arithmetic boundary, unchecked resource cap,
unstable error, dependent oracle, missing deliberate failure, or unsupported
claim. It maps that evidence to **PLT-102-01**, **PLT-102-02**,
**PLT-102-03**, or **PLT-102-04**. Preserve the original submission and evidence
before correcting it.

A retry uses assessor-selected AST forms, a different identifier grammar,
renamed types and effects, changed integer and resource bounds, and two new
shadowing/effect-order cases. The learner must restate rules, recalculate
endpoint shapes, update the independent overlap, and produce new observed
failure/restoration evidence. Revised prose cannot replace executable evidence
for a failed scope, type, effect, evaluation, bound, or test criterion.
