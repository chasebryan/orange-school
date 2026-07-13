# Lab: focused history and an exact replay

## Goal

Create a small, focused history in a fresh repository; inspect its repository,
<code>HEAD</code>, status, and diffs; then capture one exact-base patch and prove
that it can be reproduced in a separate local clone.

## Setup

Open a Bash terminal and confirm that Git is available:

~~~sh
git --version
~~~

Create one new temporary workspace with sibling directories for the repository
and external evidence:

~~~sh
workdir="$(mktemp -d)"
repo="$workdir/project"
evidence="$workdir/evidence"
mkdir -- "$evidence"
git init --quiet --initial-branch=main "$repo"
git -C "$repo" config --local user.name 'Orange School Learner'
git -C "$repo" config --local user.email 'learner.invalid@example.invalid'
printf 'Temporary workspace: %s\n' "$workdir"
git -C "$repo" rev-parse --show-toplevel
~~~

The reported repository root must equal <code>$repo</code>. If it does not,
stop. Every write must remain below <code>$workdir</code>. Use no
administrator access, network command, global Git configuration, wildcard,
permission change, history-rewriting command, deletion command, or existing
repository.

## Tasks

1. **Inspect the unborn repository.** Preserve observations, including the
   expected absence of a first commit.

   ~~~sh
   git -C "$repo" branch --show-current > "$evidence/unborn.branch"
   git -C "$repo" status --porcelain=v1 --branch > "$evidence/unborn.status"
   git -C "$repo" rev-parse --verify 'HEAD^{commit}' \
     > "$evidence/unborn-head.stdout" 2> "$evidence/unborn-head.stderr"
   unborn_head_status=$?
   printf '%s\n' "$unborn_head_status" > "$evidence/unborn-head.status"
   cat -- "$evidence/unborn.status"
   cat -- "$evidence/unborn-head.stderr"
   cat -- "$evidence/unborn-head.status"
   ~~~

   The <code>rev-parse</code> status must be nonzero because no commit exists.
   Record this as an unborn-branch observation, not as repository corruption.

2. **Create the first focused commit.** Its sole purpose is to state the
   practice repository's purpose.

   ~~~sh
   printf '# Evidence practice\n\nThis repository is local and temporary.\n' \
     > "$repo/README.md"
   git -C "$repo" status --short --branch
   git -C "$repo" add -- README.md
   git -C "$repo" diff --cached --no-ext-diff --no-textconv -- README.md
   git -C "$repo" commit --quiet -m 'Add practice repository purpose'
   first="$(git -C "$repo" rev-parse --verify 'HEAD^{commit}')"
   printf '%s\n' "$first" > "$evidence/first.sha"
   git -C "$repo" status --porcelain=v1 --branch \
     > "$evidence/after-first.status"
   ~~~

   Read the staged diff before committing. Confirm afterward that
   <code>after-first.status</code> lists the branch but no changed path.

3. **Create the second focused commit.** Its sole purpose is to add a three-step
   review checklist.

   ~~~sh
   printf '1. Inspect status.\n2. Inspect the staged diff.\n3. Record HEAD.\n' \
     > "$repo/review-checklist.txt"
   git -C "$repo" status --short --branch \
     > "$evidence/before-second.status"
   git -C "$repo" add -- review-checklist.txt
   git -C "$repo" diff --cached --no-ext-diff --no-textconv \
     -- review-checklist.txt > "$evidence/second.staged.patch"
   git -C "$repo" commit --quiet -m 'Add change review checklist'
   base="$(git -C "$repo" rev-parse --verify 'HEAD^{commit}')"
   printf '%s\n' "$base" > "$evidence/base.sha"
   git -C "$repo" log --format='%H %s' --no-decorate \
     > "$evidence/history.txt"
   git -C "$repo" status --porcelain=v1 --branch \
     > "$evidence/base.status"
   cat -- "$evidence/history.txt"
   ~~~

   The history must contain exactly two commits, with distinct messages and
   purposes. The full ID on the first history line must equal
   <code>base.sha</code>.

4. **Inspect staged and unstaged state separately.** Change one tracked file,
   observe it unstaged, stage it, observe it staged, and then record it as a
   third focused commit.

   ~~~sh
   printf '4. Preserve the exact diff.\n' >> "$repo/review-checklist.txt"
   git -C "$repo" status --porcelain=v1 --branch \
     > "$evidence/third.unstaged.status"
   git -C "$repo" diff --no-ext-diff --no-textconv \
     -- review-checklist.txt > "$evidence/third.unstaged.patch"
   git -C "$repo" diff --cached --no-ext-diff --no-textconv \
     -- review-checklist.txt > "$evidence/third.before-stage.patch"
   git -C "$repo" add -- review-checklist.txt
   git -C "$repo" status --porcelain=v1 --branch \
     > "$evidence/third.staged.status"
   git -C "$repo" diff --cached --no-ext-diff --no-textconv \
     -- review-checklist.txt > "$evidence/third.staged.patch"
   git -C "$repo" commit --quiet -m 'Require exact diff preservation'
   capture_base="$(git -C "$repo" rev-parse --verify 'HEAD^{commit}')"
   printf '%s\n' "$capture_base" > "$evidence/capture-base.sha"
   ~~~

   <code>third.before-stage.patch</code> must be empty. The unstaged status and
   patch must move to the staged status and patch after <code>git add</code>.

5. **Create a change to capture, but do not commit it.** This change has one
   deliberate line replacement.

   ~~~sh
   printf '# Evidence practice\n\nThis repository is local, temporary, and replayable.\n' \
     > "$repo/README.md"
   git -C "$repo" status --porcelain=v1 --branch \
     > "$evidence/capture.status"
   git -C "$repo" diff --no-ext-diff --no-textconv --full-index --binary \
     "$capture_base" -- > "$evidence/change.patch"
   git -C "$repo" diff --cached --no-ext-diff --no-textconv \
     -- > "$evidence/capture.cached.patch"
   ~~~

   Confirm that status identifies <code>README.md</code> as an unstaged tracked
   change, <code>change.patch</code> is nonempty, and
   <code>capture.cached.patch</code> is empty.

6. **Replay from the exact base.** A local clone copies committed history but
   not the source repository's uncommitted working-tree edit.

   ~~~sh
   replay="$workdir/replay"
   git clone --quiet --no-hardlinks "$repo" "$replay"
   git -C "$replay" checkout --quiet --detach "$capture_base"
   replay_head="$(git -C "$replay" rev-parse --verify 'HEAD^{commit}')"
   printf '%s\n' "$replay_head" > "$evidence/replay-before.sha"

   git -C "$replay" apply --check "$evidence/change.patch" \
     > "$evidence/apply-check.stdout" 2> "$evidence/apply-check.stderr"
   apply_check_status=$?
   printf '%s\n' "$apply_check_status" > "$evidence/apply-check.status"

   git -C "$replay" apply "$evidence/change.patch" \
     > "$evidence/apply.stdout" 2> "$evidence/apply.stderr"
   apply_status=$?
   printf '%s\n' "$apply_status" > "$evidence/apply.status"

   git -C "$replay" diff --no-ext-diff --no-textconv --full-index --binary \
     "$capture_base" -- > "$evidence/replayed.patch"
   cmp -s -- "$evidence/change.patch" "$evidence/replayed.patch"
   patch_compare_status=$?
   printf '%s\n' "$patch_compare_status" > "$evidence/patch-compare.status"
   ~~~

   All three recorded statuses must be 0. The two SHA files must contain the
   same full ID. If a command reports nonzero, preserve its files and diagnose
   it; do not replace the observation with 0.

7. **Write the evidence record.** Create
   <code>$evidence/revision-diff-record.txt</code> with your transcript or with
   repeated <code>printf</code> commands. Include:

   - Git version and absolute paths for <code>$repo</code> and
     <code>$replay</code>;
   - the full capture-base and replay <code>HEAD</code> IDs;
   - current branch observations for the source and detached replay;
   - the exact status, diff, clone, checkout, apply-check, apply, and comparison
     commands;
   - the unedited contents or named paths of every evidence file used;
   - observed stdout, stderr, and statuses, including empty streams; and
   - the narrow supported claim plus at least three untested limits.

## Verification

Run these read-only checks. Each must finish with status 0:

~~~sh
test "$(git -C "$repo" rev-parse --show-toplevel)" = "$repo"
test "$(git -C "$repo" rev-list --count HEAD)" -eq 3
test "$(wc -l < "$evidence/history.txt")" -eq 2
test "$(cat -- "$evidence/capture-base.sha")" = \
  "$(cat -- "$evidence/replay-before.sha")"
test -s "$evidence/change.patch"
test ! -s "$evidence/capture.cached.patch"
test "$(cat -- "$evidence/apply-check.status")" -eq 0
test "$(cat -- "$evidence/apply.status")" -eq 0
test "$(cat -- "$evidence/patch-compare.status")" -eq 0
cmp -s -- "$evidence/change.patch" "$evidence/replayed.patch"
test -s "$evidence/revision-diff-record.txt"
~~~

Then inspect, rather than merely count, every submitted file. Verify that the
record identifies <code>capture-base.sha</code>, that the source status names
the uncommitted path, and that its conclusion does not claim correctness,
tests, publication, or compatibility with another revision.

## Reflection

Add answers to the revision-and-diff record:

- How did status distinguish the same path before and after staging?
- Why did the local clone start from committed content rather than the source
  repository's uncommitted file?
- Why is the full capture-base ID essential even though the branch was named
  <code>main</code>?
- What new evidence would be needed to claim that the captured change is
  correct and professionally ready?
