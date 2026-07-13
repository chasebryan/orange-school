#!/usr/bin/env bash
set -euo pipefail

workdir="$(mktemp -d)"
marker="$workdir/.cmp-102-lab-smoke"
printf 'temporary smoke workspace\n' > "$marker"

cleanup() {
  if test -n "${workdir:-}" && test -f "$marker"; then
    rm -rf -- "$workdir"
  fi
}
trap cleanup EXIT

repo="$workdir/project"
evidence="$workdir/evidence"
replay="$workdir/replay"
mkdir -- "$evidence"

git init --quiet --initial-branch=main "$repo"
git -C "$repo" config --local user.name 'Orange School Smoke Check'
git -C "$repo" config --local user.email 'smoke.invalid@example.invalid'

git -C "$repo" rev-parse --verify 'HEAD^{commit}' \
  > "$evidence/unborn-head.stdout" 2> "$evidence/unborn-head.stderr" && {
    printf 'expected unborn HEAD verification to fail\n' >&2
    exit 1
  }
unborn_status=$?
test "$unborn_status" -ne 0

printf '# Evidence practice\n\nThis repository is local and temporary.\n' \
  > "$repo/README.md"
git -C "$repo" add -- README.md
git -C "$repo" diff --cached --quiet -- README.md && {
  printf 'expected a staged README diff\n' >&2
  exit 1
}
git -C "$repo" commit --quiet -m 'Add practice repository purpose'

printf '1. Inspect status.\n2. Inspect the staged diff.\n3. Record HEAD.\n' \
  > "$repo/review-checklist.txt"
git -C "$repo" add -- review-checklist.txt
git -C "$repo" diff --cached --no-ext-diff --no-textconv \
  -- review-checklist.txt > "$evidence/second.staged.patch"
test -s "$evidence/second.staged.patch"
git -C "$repo" commit --quiet -m 'Add change review checklist'
base="$(git -C "$repo" rev-parse --verify 'HEAD^{commit}')"
printf '%s\n' "$base" > "$evidence/base.sha"
git -C "$repo" log --format='%H %s' --no-decorate > "$evidence/history.txt"

printf '4. Preserve the exact diff.\n' >> "$repo/review-checklist.txt"
git -C "$repo" diff --no-ext-diff --no-textconv \
  -- review-checklist.txt > "$evidence/third.unstaged.patch"
git -C "$repo" diff --cached --no-ext-diff --no-textconv \
  -- review-checklist.txt > "$evidence/third.before-stage.patch"
test -s "$evidence/third.unstaged.patch"
test ! -s "$evidence/third.before-stage.patch"
git -C "$repo" add -- review-checklist.txt
git -C "$repo" diff --cached --no-ext-diff --no-textconv \
  -- review-checklist.txt > "$evidence/third.staged.patch"
test -s "$evidence/third.staged.patch"
git -C "$repo" commit --quiet -m 'Require exact diff preservation'
capture_base="$(git -C "$repo" rev-parse --verify 'HEAD^{commit}')"
printf '%s\n' "$capture_base" > "$evidence/capture-base.sha"

printf '# Evidence practice\n\nThis repository is local, temporary, and replayable.\n' \
  > "$repo/README.md"
git -C "$repo" status --porcelain=v1 --branch > "$evidence/capture.status"
git -C "$repo" diff --no-ext-diff --no-textconv --full-index --binary \
  "$capture_base" -- > "$evidence/change.patch"
git -C "$repo" diff --cached --no-ext-diff --no-textconv \
  -- > "$evidence/capture.cached.patch"
test -s "$evidence/change.patch"
test ! -s "$evidence/capture.cached.patch"
grep -F -- 'README.md' "$evidence/capture.status" > /dev/null

git clone --quiet --no-hardlinks "$repo" "$replay"
git -C "$replay" checkout --quiet --detach "$capture_base"
replay_head="$(git -C "$replay" rev-parse --verify 'HEAD^{commit}')"
test "$replay_head" = "$capture_base"

git -C "$replay" apply --check "$evidence/change.patch" \
  > "$evidence/apply-check.stdout" 2> "$evidence/apply-check.stderr"
git -C "$replay" apply "$evidence/change.patch" \
  > "$evidence/apply.stdout" 2> "$evidence/apply.stderr"
git -C "$replay" diff --no-ext-diff --no-textconv --full-index --binary \
  "$capture_base" -- > "$evidence/replayed.patch"
cmp -s -- "$evidence/change.patch" "$evidence/replayed.patch"

test "$(git -C "$repo" rev-list --count HEAD)" -eq 3
test "$(wc -l < "$evidence/history.txt")" -eq 2
test "$(wc -c < "$evidence/base.sha")" -eq 41
test "$(wc -c < "$evidence/capture-base.sha")" -eq 41
test "$(git -C "$replay" branch --show-current)" = ''

printf 'cmp-102 lab smoke: pass\n'
