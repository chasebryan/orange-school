# Rubric: terminal evidence record

## Rubric

The assessment is worth 100 points.

| Criterion | Points | Evidence required |
| --- | ---: | --- |
| Workspace containment and navigation | 25 | Fresh temporary workspace, required tree, two working directories, inspection, and correct relative and absolute paths |
| Streams and exit status | 30 | Separate stdout/stderr for success and intentional failure, immediate status capture, preserved files, and accurate interpretation |
| Reproducible command record | 30 | Environment, absolute directory, exact inputs, commands, observations, statuses, conclusions, limits, and navigation context |
| Knowledge, clarity, and safe practice | 15 | Correct knowledge answers, readable transcript, traceable files, and compliance with command boundaries |
| **Total** | **100** |  |

## Critical criteria

All three critical criteria must pass:

1. **Containment and navigation:** earn at least 20/25, create every assessed
   file inside one fresh temporary workspace, and correctly demonstrate both a
   relative and an absolute path. Any assessed write outside that workspace
   fails this criterion.
2. **Result integrity:** earn at least 24/30, keep stdout and stderr separate
   for both assessed commands, and capture each command's status before another
   command runs. Invented or overwritten status evidence fails this criterion.
3. **Reproducibility:** earn at least 24/30 and supply enough exact information
   to rerun both assessed commands and compare all three result channels.

Use of administrator access, a deletion command, a network command, a
permission change, or a wildcard during the assessment fails the containment
criterion even if the total would otherwise pass.

## Scoring

Assign points within each row as follows:

- **Workspace containment and navigation (25):** 8 for the correct contained
  tree and input, 7 for exact working-directory evidence, 5 for relative-path
  use, and 5 for absolute-path use.
- **Streams and exit status (30):** 8 for successful-command streams, 8 for
  failure-command streams, 8 for immediate preserved statuses, and 6 for
  interpretations grounded in observations.
- **Reproducible command record (30):** 5 for environment and absolute working
  directory, 6 for exact inputs, 6 for exact commands and navigation context,
  8 for stdout/stderr/status observations, and 5 for narrow conclusions and
  at least two limits.
- **Knowledge, clarity, and safe practice (15):** 8 for the four knowledge
  answers, 4 for a readable and traceable submission, and 3 for following the
  stated safe-command boundary.

Pass the module only with at least 80/100 and all critical criteria.

## Feedback and retry

Feedback identifies the first unreproducible or unsafe step, the affected
outcome ID, and the exact missing observation. The learner preserves the
original record and adds a correction note so the change remains visible.

For a retry, use a new temporary directory, a new three-line input supplied by
the assessor, and a different missing filename. Rerun every criterion affected
by the error. A corrected explanation without fresh command evidence cannot
replace a failed streams, status, containment, or reproducibility criterion.
