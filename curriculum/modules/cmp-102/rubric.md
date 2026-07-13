# Rubric: repository history and revision evidence

## Rubric

The assessment is worth 100 points.

| Criterion | Points | Evidence required |
| --- | ---: | --- |
| Repository, <code>HEAD</code>, status, and diff inspection | 25 | Correct repository root, unborn and committed <code>HEAD</code> evidence, branch observation, porcelain status, and distinct staged and unstaged diffs |
| Focused temporary history | 30 | One new contained repository, exactly three single-purpose commits, path-specific staging, inspected staged diffs, full-ID history, and accurate messages |
| Exact revision record and replay | 30 | Full capture base, external evidence, direct full-index patch, independent detached local replay, apply evidence, byte-identical regenerated diff, and bounded claim |
| Knowledge, clarity, and safe practice | 15 | Correct knowledge answers, complete transcript, traceable artifacts, local-only configuration, and compliance with command boundaries |
| **Total** | **100** |  |

## Critical criteria

All three critical criteria must pass:

1. **State integrity:** earn at least 20/25, identify the intended repository
   and full committed <code>HEAD</code>, and correctly distinguish unborn,
   unstaged, and staged evidence. Editing Git metadata by hand, concealing a
   changed path, or presenting a branch name as an immutable revision fails
   this criterion.
2. **History integrity:** earn at least 24/30 and supply exactly three truthful,
   separately reviewable commits made in the fresh repository. Combining
   requirements into one commit, staging an unintended path, rewriting the
   assessed history, or fabricating command evidence fails this criterion.
3. **Replay integrity:** earn at least 24/30, identify the full capture base,
   detach the independent local replay at that base, and demonstrate successful
   patch checking, application, and byte-identical diff regeneration. A replay
   from an unnamed or different revision fails this criterion.

Any assessed write outside the fresh temporary workspace, use of administrator
access, a network command, global Git configuration, a wildcard, a permission
change, or a deletion command fails the state-integrity criterion. A
history-rewriting command fails the history-integrity criterion.

## Scoring

Assign points within each row as follows:

- **Repository, <code>HEAD</code>, status, and diff inspection (25):** 5 for
  absolute root and branch observations, 5 for accurate unborn
  <code>HEAD</code> evidence, 7 for unstaged status and diff, 6 for staged status
  and diff, and 2 for bounded interpretations.
- **Focused temporary history (30):** 5 for contained initialization and local
  identity metadata, 12 for three separately staged single-purpose changes, 6
  for inspecting each staged diff before commit, 4 for distinct accurate
  messages, and 3 for a correct full-ID history.
- **Exact revision record and replay (30):** 5 for full base and direct patch
  options, 5 for external status and command evidence, 5 for independent local
  clone and exact detached <code>HEAD</code>, 6 for apply-check and apply result
  channels, 5 for byte-identical diff regeneration, and 4 for a narrow claim
  plus four limits.
- **Knowledge, clarity, and safe practice (15):** 8 for five correct knowledge
  answers, 4 for a readable and traceable transcript, and 3 for following the
  safe-command boundary.

Pass the module only with at least 80/100 and all critical criteria.

## Feedback and retry

Feedback names the first state transition or evidence claim that cannot be
verified, the affected outcome ID, and the missing or contradictory artifact.
The learner preserves the original submission and appends a correction note;
silently replacing failed evidence is not acceptable.

For a retry, use a new temporary directory and a new three-requirement brief
from the assessor. Recreate all history rather than rewriting the assessed
repository. The assessor also supplies a different final edit so the learner
must capture a new base and patch. Rerun every criterion affected by the error.
A prose explanation cannot replace missing status, diff, commit, or replay
evidence.
