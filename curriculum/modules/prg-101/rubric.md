# Rubric: explicit state and tested decomposition

## Rubric

The assessment is worth 100 points.

| Criterion | Points | Evidence required |
| --- | ---: | --- |
| Expression, state, and control-flow trace | 25 | Every executed step, changing bindings, comparisons, branches, outputs, and correct final prediction |
| Explicit program behavior | 35 | Exact interface, conversion, bounded validation, accepted state transitions, four-value report, stderr failures, and exit statuses |
| Decomposition and testing | 30 | Purposeful functions plus passing normal, boundary, invalid, and command-level tests |
| Reproducible record and clarity | 10 | Environment, directory, commands, three result channels, readable source, and evidence limits |
| **Total** | **100** |  |

## Critical criteria

All three critical criteria must pass:

1. **Trace integrity:** earn at least 20/25 and correctly predict the final
   accepted stock and output. A trace that skips a state-changing statement
   fails this criterion.
2. **State and failure safety:** earn at least 28/35. Valid changes must update
   state in order; underflow, overflow, and malformed input must produce no
   success report and a nonzero status.
3. **Independent test evidence:** earn at least 24/30 and include passing
   normal, boundary, invalid, and command-level tests. A syntax check or copied
   example is not independent behavior evidence.

A score of 80 or more cannot compensate for a failed critical criterion.

## Scoring

- **Trace (25):** 10 for statement order and bindings, 7 for proposed versus
  accepted state, 4 for branch/output decisions, and 4 for final predictions.
- **Program (35):** 7 for the exact interface and conversion, 8 for input
  bounds, 10 for state transitions and extrema, 5 for success output, and 5 for
  stderr/status failure behavior.
- **Decomposition and testing (30):** 8 for purposeful function boundaries, 5
  for normal cases, 7 for boundary cases, 7 for invalid cases, and 3 for a
  command-level three-channel test.
- **Record and clarity (10):** 5 for reproducible commands and observations, 3
  for readable names and structure, and 2 for a truthful evidence limit.

Pass only with at least 80/100 and all critical criteria.

## Feedback and retry

Feedback names the first incorrect state transition, missing validation,
unexercised branch, or unreproducible observation and maps it to an outcome ID.
The learner preserves the original work and adds a correction record.

A retry uses a fresh capacity, starting state, and change sequence supplied by
the assessor. Rerun every affected test class and the command-level check. A
written correction cannot replace fresh execution evidence for a failed
program or testing criterion.
