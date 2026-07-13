# Git and reproducible change history

Git records related snapshots of a project. A useful Git record does more than
say that a file changed: it identifies the repository, the exact revision, the
state that was not committed, and the commands used to inspect or reproduce
the change. This module begins in a new temporary repository so no existing
project can be altered accidentally.

## Learning objectives

- **CMP-102-01:** Inspect a repository's exact <code>HEAD</code>, worktree
  status, and diff without changing it.
- **CMP-102-02:** Create focused Git history in a fresh temporary repository.
- **CMP-102-03:** Produce a reproducible evidence record tied to an exact
  revision and diff.

## Prerequisites

Pass <code>cmp-101</code>. You should be able to create a temporary directory,
navigate with absolute and relative paths, redirect stdout and stderr, capture
an exit status immediately, and preserve a reproducible command record. No Git
experience is assumed.

Use a course-provided Bash terminal with Git available. Check the tool before
starting:

~~~sh
git --version
~~~

If that command fails, stop and report the environment blocker. Every writing
example below stays inside a path returned by <code>mktemp -d</code>. The
examples use no administrator access, network access, global Git configuration,
history-rewriting command, wildcard, permission change, or deletion command.

## Lesson

### Five pieces of repository state

A Git project has related pieces that must not be confused:

1. The **working tree** is the ordinary files you can read and edit.
2. The **repository** is the <code>.git</code> metadata directory that stores
   objects and references. Do not edit its files by hand.
3. The **index**, often called the staging area, is the proposed content for
   the next commit.
4. A **commit** identifies one stored snapshot plus its parent or parents,
   author metadata, committer metadata, and message.
5. A **branch** is a movable name for a commit. <code>HEAD</code> normally names
   the checked-out branch; that branch then names the current commit.

A hexadecimal commit object ID is stronger evidence than a branch name because
the branch can later move. It is still not a claim that a commit is correct,
reviewed, published, or trustworthy. It identifies stored content and history
in the repository you inspected.

Before the first commit, a repository has an **unborn branch**. Git can report
the branch and file status, but <code>git rev-parse --verify
'HEAD^{commit}'</code> correctly fails because no current commit exists yet.

### Inspect before changing

Git accepts <code>-C PATH</code> before a subcommand. It asks Git to operate as
if it had first changed into that directory. This makes the target repository
visible in every command and avoids relying on an accidental current directory.

| Command | Observation | Changes repository state? |
| --- | --- | --- |
| <code>git -C "$repo" rev-parse --show-toplevel</code> | Absolute working-tree root | No |
| <code>git -C "$repo" rev-parse --verify 'HEAD^{commit}'</code> | Exact current commit, or nonzero if none exists | No |
| <code>git -C "$repo" branch --show-current</code> | Current branch name, if attached | No |
| <code>git -C "$repo" status --porcelain=v1 --branch</code> | Branch plus stable, compact path status | No |
| <code>git -C "$repo" diff --no-ext-diff --no-textconv --</code> | Unstaged tracked changes | No |
| <code>git -C "$repo" diff --cached --no-ext-diff --no-textconv --</code> | Staged changes relative to <code>HEAD</code> | No |
| <code>git -C "$repo" log --oneline --no-decorate</code> | Abbreviated history for reading | No |

The <code>--</code> marks the end of command options. A path after it is treated
as a path even if its name begins with a dash. With no path after it, the diff
commands inspect all relevant tracked paths.

The first column of short status describes the difference between
<code>HEAD</code> and the index. The second describes the difference between the
index and working tree. <code>??</code> marks an untracked path. Human-oriented
<code>git status</code> is helpful for explanation; porcelain version 1 is the
stable form to preserve for scripts and evidence.

These comparisons answer different questions:

- <code>git diff</code>: what tracked work has not been staged?
- <code>git diff --cached</code>: what would the next commit add relative to
  <code>HEAD</code>?
- <code>git diff REVISION --</code>: how does the working tree differ from that
  exact stored revision?
- <code>git show REVISION</code>: what commit and change does that revision
  identify?

An empty diff means no difference in the comparison that was requested. It
does not prove that every file is tracked, that another branch is identical,
or that the project is correct. Pair a diff with status and the named revision.

### Build focused commits

Create a repository only inside a new temporary workspace:

~~~sh
workdir="$(mktemp -d)"
repo="$workdir/project"
evidence="$workdir/evidence"
mkdir -- "$evidence"
git init --quiet --initial-branch=main "$repo"
git -C "$repo" config --local user.name 'Orange School Learner'
git -C "$repo" config --local user.email 'learner.invalid@example.invalid'
~~~

The two configuration commands write only to this repository. A commit requires
author metadata, but locally configured text is not proof of a person's legal
identity. Never substitute course exercise values in a professional record
without stating that they are exercise metadata.

A focused commit has one purpose that a reviewer can describe and verify. Use
this loop:

1. Make one coherent change.
2. Inspect status and the unstaged diff.
3. Stage only the paths for that purpose with <code>git add -- PATH</code>.
4. Inspect the staged diff with <code>git diff --cached -- PATH</code>.
5. Commit with a message that states the result, not the act of typing.
6. Confirm status, <code>HEAD</code>, and the new history.

For example:

~~~sh
printf '# Practice project\n' > "$repo/README.md"
git -C "$repo" status --short --branch
git -C "$repo" diff --no-ext-diff --no-textconv -- README.md
git -C "$repo" add -- README.md
git -C "$repo" diff --cached --no-ext-diff --no-textconv -- README.md
git -C "$repo" commit --quiet -m 'Add project purpose'
git -C "$repo" rev-parse --verify 'HEAD^{commit}'
~~~

An untracked file has no earlier tracked content, so ordinary unstaged
<code>git diff</code> does not print its contents. Status reveals the untracked
path; after staging, <code>git diff --cached</code> shows the proposed addition.

Do not use <code>git add .</code> in this exercise. Naming the intended path
makes the boundary reviewable. Do not use <code>git commit -a</code>, because it
combines staging and committing and can hide which tracked paths were selected.

### Record and reproduce an exact change

A useful revision-and-diff evidence bundle contains at least:

- the Git version and absolute repository root;
- the full 40-character base commit ID;
- the branch name as an observation, not as a substitute for that ID;
- porcelain status at the time of capture;
- the exact diff command and an unedited patch;
- stdout, stderr, and exit status from verification;
- a narrow conclusion and explicit untested limits.

For a portable full-index patch from an exact base, use:

~~~sh
base="$(git -C "$repo" rev-parse --verify 'HEAD^{commit}')"
printf '%s\n' "$base" > "$evidence/base.sha"
git -C "$repo" status --porcelain=v1 --branch > "$evidence/status.txt"
git -C "$repo" diff --no-ext-diff --no-textconv --full-index --binary \
  "$base" -- > "$evidence/change.patch"
~~~

<code>--full-index</code> retains full object names in patch headers when they
are present. <code>--binary</code> permits binary changes to be represented.
<code>--no-ext-diff</code> and <code>--no-textconv</code> prevent optional diff
helpers from replacing the repository's direct comparison. A patch is still
only evidence for its named base and paths.

Verify reproducibility in a separate local clone:

~~~sh
replay="$workdir/replay"
git clone --quiet --no-hardlinks "$repo" "$replay"
git -C "$replay" checkout --quiet --detach "$base"
git -C "$replay" apply --check "$evidence/change.patch"
check_status=$?
printf '%s\n' "$check_status" > "$evidence/apply-check.status"
git -C "$replay" apply "$evidence/change.patch"
git -C "$replay" diff --no-ext-diff --no-textconv --full-index --binary \
  "$base" -- > "$evidence/replayed.patch"
cmp -s -- "$evidence/change.patch" "$evidence/replayed.patch"
compare_status=$?
printf '%s\n' "$compare_status" > "$evidence/patch-compare.status"
~~~

The clone source is the local path in <code>$repo</code>; no network is used.
<code>--no-hardlinks</code> gives the replay clone its own object files.
Detached <code>HEAD</code> makes the exact base explicit. <code>git apply
--check</code> checks applicability without changing files. The following
<code>git apply</code> changes only the replay working tree. <code>cmp -s</code>
returns 0 when the two patch files are byte-for-byte identical and nonzero
otherwise.

This verification supports the claim: “This captured patch reapplied to this
exact base in this local replay, and the resulting direct diff was identical.”
It does not prove that the change is correct, that it applies to another base,
that tests pass, or that any remote contains the commit.

## Worked example

Continue from the temporary repository created above. Make two independent
commits and then capture one uncommitted change:

~~~sh
printf 'Review each staged diff.\n' > "$repo/review.txt"
git -C "$repo" status --short --branch
git -C "$repo" add -- review.txt
git -C "$repo" diff --cached --no-ext-diff --no-textconv -- review.txt
git -C "$repo" commit --quiet -m 'Add review rule'

printf 'Record the full revision.\n' > "$repo/evidence.txt"
git -C "$repo" status --short --branch
git -C "$repo" add -- evidence.txt
git -C "$repo" diff --cached --no-ext-diff --no-textconv -- evidence.txt
git -C "$repo" commit --quiet -m 'Add evidence rule'

git -C "$repo" log --oneline --no-decorate
git -C "$repo" status --porcelain=v1 --branch
base="$(git -C "$repo" rev-parse --verify 'HEAD^{commit}')"
printf 'Record the full revision and the exact command.\n' > "$repo/evidence.txt"
git -C "$repo" diff --no-ext-diff --no-textconv -- evidence.txt
~~~

The history contains two purposes: a review rule and an evidence rule. The last
edit remains unstaged, so status places it in the working-tree column,
<code>git diff</code> displays it, and <code>git diff --cached</code> remains
empty. Capture and replay that change with the evidence commands from the
previous section.

## Check your understanding

1. What do the working tree, index, <code>HEAD</code>, and current branch each
   name?
2. Why can <code>git rev-parse --verify 'HEAD^{commit}'</code> fail in a valid
   newly initialized repository?
3. Which command shows an unstaged tracked change? Which shows the proposed
   next commit?
4. Why is a branch name weaker revision evidence than a full commit ID?
5. A patch reapplies cleanly and produces a byte-identical diff. What does that
   prove, and what does it leave untested?
6. Why does the module configure <code>user.name</code> and
   <code>user.email</code> with <code>--local</code>?

**Answers:** (1) the working tree holds ordinary files, the index holds staged
content, <code>HEAD</code> identifies the checked-out branch or direct commit,
and a branch is a movable reference to a commit; (2) the unborn branch has no
commit yet; (3) <code>git diff</code> and <code>git diff --cached</code>,
respectively; (4) a branch can move; (5) it proves replay from the recorded base
for that patch and environment, but not correctness, tests, other bases, or
publication; (6) to avoid changing user-wide Git settings and to keep exercise
identity metadata inside the temporary repository.

## Next step

Complete the [lab](lab.md) in a new temporary directory, preserving the
repository and its sibling evidence directory for review. Then complete the
[independent assessment](assessment.md). Passing requires at least 80/100 and
every critical criterion in the [rubric](rubric.md).

## Sources

- Git project, [<code>git status</code> documentation](https://git-scm.com/docs/git-status),
  repository, index, working-tree, branch, short, and porcelain status.
- Git project, [<code>git diff</code> documentation](https://git-scm.com/docs/git-diff),
  working-tree, staged, revision, full-index, binary, and no-index comparisons.
- Git project, [<code>git rev-parse</code> documentation](https://git-scm.com/docs/git-rev-parse)
  and [<code>git revisions</code> documentation](https://git-scm.com/docs/gitrevisions),
  repository roots, references, commit peeling, and revision syntax.
- Git project, [<code>git commit</code> documentation](https://git-scm.com/docs/git-commit)
  and [Git user manual](https://git-scm.com/docs/user-manual), commits,
  branches, the index, and history.
- Git project, [<code>git apply</code> documentation](https://git-scm.com/docs/git-apply),
  patch checking and application.
- [Assessment system](../../../docs/assessment-system.md), evidence integrity
  and module pass policy.
