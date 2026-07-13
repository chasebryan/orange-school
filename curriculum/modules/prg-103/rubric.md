# Rubric: a reliable bounded job request

## Rubric

The assessment is worth 100 points.

| Criterion | Points | Evidence required |
| --- | ---: | --- |
| Annotated contract and invariants | 25 | Exact public annotations, explicit input/output invariants, immutable records, and implementation that matches the written boundary |
| Reproduction, focused test, and diagnosis | 30 | Preserved pre-repair failure, minimized case, focused regression test, systematic diagnosis, narrow repair, focused pass, and full-suite pass |
| Explicit fail-closed error design | 30 | Distinct success/failure variants, no partial result on error, stable field/code/message, bounded visible context, and complete named rejection behavior |
| Test breadth, evidence, and clarity | 15 | Boundary suite, `subTest` use, reproducible commands and statuses, readable package, knowledge answers, and honest evidence limits |
| **Total** | **100** |  |

## Critical criteria

All three critical criteria must pass:

1. **Contract integrity — PRG-103-01:** earn at least 20/25. The exact public
   function has input and return annotations, all required invariants are stated,
   and the implementation neither accepts a forbidden representation nor
   silently normalizes it. Missing output variants or a written contract that
   disagrees with the code fails this criterion.
2. **Reproduced and diagnosed regression — PRG-103-02:** earn at least 24/30.
   Evidence must show the same focused test failing before the repair and passing
   afterward, with the exact input, command, output, status, violated invariant,
   hypothesis, discriminating experiment, diagnosis, and narrow repair. A test
   written only after the code already passes fails this criterion.
3. **Fail-closed error boundary — PRG-103-03:** earn at least 24/30. Every named
   invalid input must return a structured failure with the correct field and
   code, no failure may expose `capacity_units` or a partial request, and context
   must be useful, `repr`-visible, at most 80 characters, and limited to the
   assessed value and its runtime type. Silent defaults, broad exception
   suppression, or invented success values fail this criterion.

Use of a network service, non-standard package, administrator access, destructive
command, or diagnostic that discloses unrelated environment or file data fails
the applicable critical criterion even if the point total would otherwise pass.

## Scoring

Assign points within each rubric row as follows:

- **Annotated contract and invariants (25):** 6 for the exact annotated public
  signature and annotated record fields; 8 for complete accepted-input and
  result invariants; 7 for runtime checks that match those invariants without
  normalization; and 4 for constructor or test enforcement of success-state
  consistency.
- **Reproduction, focused test, and diagnosis (30):** 6 for exact pre-repair
  reproduction evidence; 6 for a minimal focused test that fails for the named
  rule; 8 for observation, hypotheses, experiment, and evidence-backed diagnosis;
  5 for a narrow repair; and 5 for the same focused test plus full suite passing
  with preserved statuses.
- **Explicit fail-closed error design (30):** 8 for distinct immutable success,
  error, and failure records; 8 for early rejection with no partial result; 8
  for stable correct codes, fields, and messages across named cases; and 6 for
  bounded, visible, safe received-value context.
- **Test breadth, evidence, and clarity (15):** 6 for the required normal,
  boundary, malformed, Unicode, and runtime-type cases; 3 for appropriate
  `subTest` grouping and public-result assertions; 3 for reproducible commands,
  outputs, and statuses; and 3 for correct knowledge answers, readable code, and
  at least three accurate evidence limits.

Pass the module only with at least 80/100 and all critical criteria.

## Feedback and retry

Feedback identifies the first violated invariant or missing evidence item, its
outcome ID, and the smallest test that exposes it. Preserve the original failed
run and diagnosis; append corrections rather than rewriting the record into an
apparently uninterrupted success.

For a retry, the assessor supplies a different safe boundary defect, such as an
off-by-one range, wrong-field diagnostic, Unicode acceptance, or accidental
normalization. The learner must reproduce that defect, add a new focused test,
diagnose it, make a narrow repair, and rerun every affected boundary case plus
the complete suite. Unchanged criteria may retain their earlier points, but all
three critical criteria and the 80/100 threshold still apply.
