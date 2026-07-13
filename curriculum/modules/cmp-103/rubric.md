# Rubric: failure isolation, test contract, and CI evidence

## Rubric

The assessment is worth 100 points.

| Criterion | Points | Evidence required |
| --- | ---: | --- |
| Failure reproduction and isolation | 25 | Exact environment and command record, two unchanged matching reproductions, one-condition control, direct fixture diff, and bounded causal statement |
| Test design, automation, and exit behavior | 35 | Prewritten four-case plan, distinct checker outcomes, isolated artifacts, expected-versus-observed summary, nonzero violated run, restored passing run, and exact committed test revision |
| CI check interpretation | 25 | Provider semantics, final-state and full-revision match, command and artifact trace, narrow conclusion, labeled inference, unsupported claims, and discriminating next checks |
| Knowledge, clarity, and safe practice | 15 | Correct knowledge answers, complete transcript, traceable evidence, and compliance with temporary-workspace boundaries |
| **Total** | **100** |  |

## Critical criteria

All three critical criteria must pass:

1. **Reproduction integrity:** earn at least 20/25 and provide two unchanged
   reproductions with matching result channels plus a control that changes only
   one declared condition. Invented output, changed unrecorded setup, or calling
   a hypothesis a proven cause fails this criterion.
2. **Test integrity:** earn at least 28/35, define expected results before the
   assessed run, distinguish mismatch from invalid setup, return nonzero when
   an expectation is violated, and return 0 after exact restoration. A runner
   that succeeds regardless of observed results or an oracle copied from the
   same run's output fails this criterion.
3. **CI evidence integrity:** earn at least 20/25, match the record's full
   revision, status, conclusion, command, and artifacts using the provider's
   stated semantics, and keep the conclusion within those observations.
   Treating a branch label, color, or conclusion alone as proof of correctness
   or production readiness fails this criterion.

Any assessed write outside the fresh temporary workspace, use of administrator
access, a network command, global Git configuration, a wildcard, a permission
change, or a deletion command fails the reproduction-integrity criterion.
Misrepresenting an offline exercise record as a hosted CI run fails the CI
evidence-integrity criterion.

## Scoring

Assign points within each row as follows:

- **Failure reproduction and isolation (25):** 5 for exact environment,
  revision state, fixtures, directory, and command; 7 for two preserved and
  matching failure observations; 6 for a valid one-condition control and
  direct diff; 4 for separating symptom, hypothesis, and supported mechanism;
  and 3 for explicit remaining uncertainty.
- **Test design, automation, and exit behavior (35):** 7 for a pre-execution
  four-case plan, 7 for checker status and diagnostic contracts, 7 for isolated
  per-case actual-versus-expected records, 6 for a truthful overall runner, 5
  for preserved nonzero mutation and restored success, and 3 for the exact
  committed revision and staged test-system review.
- **CI check interpretation (25):** 4 for provider and field semantics, 5 for
  final-state and full-revision verification, 5 for command and artifact
  tracing, 5 for the strongest bounded conclusion and labeled inference, 3 for
  at least five unsupported claims, and 3 for two useful next checks.
- **Knowledge, clarity, and safe practice (15):** 9 for six correct knowledge
  answers, 3 for a readable, complete, traceable submission, and 3 for
  following the safe-command boundary.

Pass the module only with at least 80/100 and all critical criteria.

## Feedback and retry

Feedback names the first unreproduced observation, ambiguous exit contract, or
overstated CI claim; identifies the affected outcome ID; and points to the
missing or contradictory artifact. Preserve the original evidence and append a
correction note so changed reasoning remains visible.

For a retry, use a new temporary directory, a different oracle and boundary
fixtures from the assessor, and a different offline check record. Rebuild and
rerun all affected cases, including a new deliberate expectation violation and
restored passing run. A rewritten explanation cannot replace missing raw
result channels, a failure-sensitive suite, exact revision evidence, or the
provider record used for interpretation.
