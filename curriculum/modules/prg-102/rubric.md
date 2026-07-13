# Rubric: bounded event summary

## Rubric

The assessment is worth 100 points.

| Criterion | Points | Evidence required |
| --- | ---: | --- |
| Representation choices and invariants | 25 | Purposeful list, tuple, dictionary, and set use, each justified by required operations and maintained invariant |
| Algorithms and tests | 35 | Correct first search, counting, stable deduplication, copied ordering, no mutation, and independent behavior tests |
| Bounds and failure behavior | 30 | Stated time/space assumptions, concrete limits, validation before processing, stderr diagnostics, and nonzero invalid status |
| Reproducibility and clarity | 10 | Environment, directory, commands, observations, statuses, readable code, and test-evidence limits |
| **Total** | **100** |  |

## Critical criteria

All three critical criteria must pass:

1. **Representation integrity:** earn at least 20/25. Every required structure
   must serve its stated operation and maintain its invariant; incidental use
   merely to name all four types does not pass.
2. **Algorithm correctness:** earn at least 28/35. Search, count, stable
   deduplication, and ordering must pass normal and boundary tests, and ordering
   must not mutate the input.
3. **Bounded failure:** earn at least 24/30. Item and code bounds must be
   enforced before reporting algorithms run; invalid input must produce no
   success report and a nonzero status. Complexity claims must distinguish
   expected hashing behavior.

A total of 80 or more cannot compensate for a failed critical criterion.

## Scoring

- **Representations (25):** 5 each for purposeful list, tuple, dictionary, and
  set choices, plus 5 for precise invariants and misuse analysis.
- **Algorithms (35):** 7 each for first search, counting, stable
  deduplication, and copied ordering, plus 7 for independent tests including
  absence, repetition, order, and non-mutation.
- **Bounds (30):** 8 for input validation, 7 for concrete 1/64/65 and code
  boundary tests, 8 for time and space statements with assumptions, and 7 for
  diagnostic/stdout/status failure behavior.
- **Reproducibility (10):** 5 for exact environment, commands, and observed
  channels; 3 for readable source and tests; and 2 for truthful evidence
  limits.

Pass only with at least 80/100 and all critical criteria.

## Feedback and retry

Feedback names the first representation mismatch, incorrect algorithm state,
missing bound, or unsupported complexity claim and maps it to an outcome ID.
The learner preserves the original work and adds a correction record.

A retry uses a fresh event sequence and target supplied by the assessor,
including a different boundary or invalid case. Rerun every affected algorithm
and command-level test. Revised prose alone cannot replace execution evidence
for failed correctness or bound enforcement.
