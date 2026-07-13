# Assessment: repository history and revision evidence

## Instructions

Complete this assessment in a fresh Bash session without copying the lab's
file names, commit messages, or content. You may consult the lesson and Git's
documentation. Use one new path from <code>mktemp -d</code>, with a repository
and evidence directory beneath it. Use local Git identity configuration only.

Do not use administrator access, network commands, global Git configuration,
wildcards, permission changes, deletion commands, history-rewriting commands,
or an existing repository. Keep the temporary workspace for review.

Submit the workspace path, exact command transcript, repository, external
evidence directory, and written answers. The assessor must be able to inspect
all commits and replay the captured patch without guessing.

This assessment covers:

- **CMP-102-01:** Inspect a repository's exact <code>HEAD</code>, worktree
  status, and diff without changing it.
- **CMP-102-02:** Create focused Git history in a fresh temporary repository.
- **CMP-102-03:** Produce a reproducible evidence record tied to an exact
  revision and diff.

## Knowledge check

1. Define working tree, repository, index, commit, branch, and
   <code>HEAD</code>. Explain how a branch can move while a full commit ID
   continues to identify the same stored commit.
2. Explain what each comparison observes: <code>git diff</code>,
   <code>git diff --cached</code>, and <code>git diff REVISION --</code>.
3. A valid new repository reports a branch but
   <code>git rev-parse --verify 'HEAD^{commit}'</code> exits nonzero. Explain
   why this can be expected.
4. A replay patch applies cleanly to its recorded base. Give one claim that
   evidence supports and four claims it does not support by itself.
5. Explain why this assessment requires <code>git config --local</code>, named
   paths with <code>git add -- PATH</code>, and evidence outside the repository.

## Independent task

1. **Repository inspection — CMP-102-01.** Initialize a repository on branch
   <code>main</code> inside the temporary workspace and configure exercise
   identity locally. Before the first commit, preserve the repository root,
   branch, porcelain status, and stdout, stderr, and status from trying to
   verify <code>HEAD</code>. Explain the nonzero result. During later work,
   preserve evidence of one tracked path while unstaged and again while staged.
   Preserve both corresponding diffs and explain their columns and boundaries.
2. **Focused history — CMP-102-02.** Create exactly three commits from this
   three-requirement brief. First add <code>purpose.txt</code> with the exact
   line <code>Evidence identifies an exact revision.</code>. Second add
   <code>review.txt</code> with the exact lines <code>Inspect status.</code> and
   <code>Inspect the staged diff.</code>. Third add
   <code>boundaries.txt</code> with the exact line <code>A passing replay does
   not prove correctness.</code>. Put each requirement in its own commit.
   Before each commit, preserve status and the staged diff for only its intended
   path. Write a distinct outcome-oriented message. Submit a full-ID history
   and explain why each commit has one reviewable purpose.
3. **Exact revision and diff record — CMP-102-03.** Record the full third-commit
   ID as the capture base. Make one uncommitted change by appending the exact
   line <code>Tests are separate evidence.</code> to
   <code>boundaries.txt</code>. Capture porcelain status and a direct
   full-index binary patch from that exact base with external and
   text-conversion helpers disabled. Clone the repository to a second local
   directory without hardlinks, detach at the exact capture base, check the
   patch, apply it, regenerate the diff with the same options, and compare the
   two patch files byte for byte. Preserve every command, output channel, and
   immediate status.
4. Create a self-contained revision-and-diff record. Include the Git version,
   absolute source and replay roots, full base and replay IDs, observed branch
   and status, exact commands, named evidence artifacts, verification results,
   one narrowly supported conclusion, and at least four explicit limits. Keep
   evidence outside both repositories but inside the temporary workspace.
5. Run read-only checks showing that the source has exactly three commits, the
   two base IDs match, the original patch is nonempty, all apply and comparison
   statuses are 0, and the regenerated patch is byte-identical. Preserve the
   checks and their statuses.

## Completion criteria

The [rubric](rubric.md) requires at least 80/100 and every critical criterion.
Passing evidence must show:

- correct, non-mutating repository, <code>HEAD</code>, status, and diff
  inspection for **CMP-102-01**, including the unborn state and staged versus
  unstaged comparison;
- exactly three focused, inspect-before-commit changes in a new contained
  repository for **CMP-102-02**; and
- a full exact-base record and successful independent local replay with
  byte-identical regenerated diff for **CMP-102-03**.

A clean status alone, an abbreviated commit ID, a branch name without the full
base, or an undocumented successful replay is insufficient.
