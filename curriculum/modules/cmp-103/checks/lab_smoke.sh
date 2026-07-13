#!/usr/bin/env bash
set -euo pipefail

workdir="$(mktemp -d)"
marker="$workdir/.cmp-103-lab-smoke"
printf 'temporary smoke workspace\n' > "$marker"

cleanup() {
  if test -n "${workdir:-}" && test -f "$marker"; then
    rm -rf -- "$workdir"
  fi
}
trap cleanup EXIT

repo="$workdir/contract-project"
evidence="$workdir/evidence"
mkdir -- "$evidence"
git init --quiet --initial-branch=main "$repo"
git -C "$repo" config --local user.name 'Orange School Smoke Check'
git -C "$repo" config --local user.email 'smoke.invalid@example.invalid'

printf 'mode=study\n' > "$repo/oracle.txt"
printf 'mode=study\n' > "$repo/candidate-good.txt"
printf 'mode=stduy\n' > "$repo/candidate-bad.txt"

printf '%s\n' \
  '#!/usr/bin/env bash' \
  'set -u' \
  '' \
  'if test "$#" -ne 2; then' \
  '  printf "%s\n" "ERROR: expected candidate and oracle paths" >&2' \
  '  exit 2' \
  'fi' \
  'candidate="$1"' \
  'oracle="$2"' \
  'if test ! -f "$candidate" || test ! -f "$oracle"; then' \
  '  printf "%s\n" "ERROR: an input is not a readable regular file" >&2' \
  '  exit 2' \
  'fi' \
  'cmp -s -- "$candidate" "$oracle"' \
  'comparison_status="$?"' \
  'case "$comparison_status" in' \
  '  0) printf "%s\n" "PASS: candidate matches oracle"; exit 0 ;;' \
  '  1) printf "%s\n" "FAIL: candidate differs from oracle" >&2; exit 1 ;;' \
  '  *) printf "%s\n" "ERROR: comparison could not run" >&2; exit 2 ;;' \
  'esac' \
  > "$repo/check_file.sh"

printf '%s\n' \
  '#!/usr/bin/env bash' \
  'set -u' \
  '' \
  'if test "$#" -ne 1; then' \
  '  printf "%s\n" "ERROR: expected evidence directory" >&2' \
  '  exit 2' \
  'fi' \
  'evidence="$1"' \
  'if test ! -d "$evidence"; then' \
  '  printf "%s\n" "ERROR: evidence directory is missing" >&2' \
  '  exit 2' \
  'fi' \
  ': > "$evidence/test-summary.txt"' \
  'failures=0' \
  'run_case() {' \
  '  name="$1"' \
  '  expected_status="$2"' \
  '  candidate_path="$3"' \
  '  bash check_file.sh "$candidate_path" oracle.txt > "$evidence/$name.stdout" 2> "$evidence/$name.stderr"' \
  '  actual_status="$?"' \
  '  printf "case=%s expected=%s actual=%s\n" "$name" "$expected_status" "$actual_status" >> "$evidence/test-summary.txt"' \
  '  if test "$actual_status" -eq "$expected_status"; then' \
  '    printf "case=%s result=PASS\n" "$name" >> "$evidence/test-summary.txt"' \
  '  else' \
  '    printf "case=%s result=FAIL\n" "$name" >> "$evidence/test-summary.txt"' \
  '    failures=$((failures + 1))' \
  '  fi' \
  '}' \
  'run_case exact-match 0 candidate-good.txt' \
  'run_case content-mismatch 1 candidate-bad.txt' \
  'run_case missing-input 2 absent.txt' \
  'if test "$failures" -eq 0; then' \
  '  printf "%s\n" "suite=PASS" >> "$evidence/test-summary.txt"' \
  '  exit 0' \
  'fi' \
  'printf "suite=FAIL failures=%s\n" "$failures" >> "$evidence/test-summary.txt"' \
  'exit 1' \
  > "$repo/run_tests.sh"

cd -- "$repo"

for attempt in 1 2; do
  if bash check_file.sh candidate-bad.txt oracle.txt \
    > "$evidence/reproduce-$attempt.stdout" \
    2> "$evidence/reproduce-$attempt.stderr"; then
    printf 'expected direct mismatch attempt %s to fail\n' "$attempt" >&2
    exit 1
  else
    status=$?
  fi
  test "$status" -eq 1
  printf '%s\n' "$status" > "$evidence/reproduce-$attempt.status"
done
cmp -s -- "$evidence/reproduce-1.stdout" "$evidence/reproduce-2.stdout"
cmp -s -- "$evidence/reproduce-1.stderr" "$evidence/reproduce-2.stderr"

bash check_file.sh candidate-good.txt oracle.txt \
  > "$evidence/control.stdout" 2> "$evidence/control.stderr"
test ! -s "$evidence/control.stderr"

if bash check_file.sh absent.txt oracle.txt \
  > "$evidence/missing.stdout" 2> "$evidence/missing.stderr"; then
  printf 'expected missing-input check to fail\n' >&2
  exit 1
else
  missing_status=$?
fi
test "$missing_status" -eq 2

if git diff --no-index --no-ext-diff --no-textconv \
  -- candidate-good.txt candidate-bad.txt \
  > "$evidence/fixture.diff" 2> "$evidence/fixture-diff.stderr"; then
  printf 'expected fixtures to differ\n' >&2
  exit 1
else
  fixture_diff_status=$?
fi
test "$fixture_diff_status" -eq 1
grep -F -- 'study' "$evidence/fixture.diff" > /dev/null
grep -F -- 'stduy' "$evidence/fixture.diff" > /dev/null

bash run_tests.sh "$evidence" \
  > "$evidence/suite.stdout" 2> "$evidence/suite.stderr"
grep -F -- 'case=exact-match result=PASS' "$evidence/test-summary.txt" \
  > /dev/null
grep -F -- 'case=content-mismatch result=PASS' "$evidence/test-summary.txt" \
  > /dev/null
grep -F -- 'case=missing-input result=PASS' "$evidence/test-summary.txt" \
  > /dev/null
grep -F -- 'suite=PASS' "$evidence/test-summary.txt" > /dev/null

printf 'mode=study\n' > candidate-bad.txt
if bash run_tests.sh "$evidence" \
  > "$evidence/violated-suite.stdout" \
  2> "$evidence/violated-suite.stderr"; then
  printf 'expected runner to reject a violated test expectation\n' >&2
  exit 1
else
  violated_status=$?
fi
test "$violated_status" -eq 1
grep -F -- 'case=content-mismatch result=FAIL' "$evidence/test-summary.txt" \
  > /dev/null
grep -F -- 'suite=FAIL failures=1' "$evidence/test-summary.txt" > /dev/null

printf 'mode=stduy\n' > candidate-bad.txt
bash run_tests.sh "$evidence" \
  > "$evidence/final-suite.stdout" 2> "$evidence/final-suite.stderr"
grep -F -- 'suite=PASS' "$evidence/test-summary.txt" > /dev/null

git add -- oracle.txt candidate-good.txt candidate-bad.txt \
  check_file.sh run_tests.sh
git diff --cached --quiet -- && {
  printf 'expected staged test-system changes\n' >&2
  exit 1
}
git commit --quiet -m 'Add deterministic file contract checks'
revision="$(git rev-parse --verify 'HEAD^{commit}')"
test "$(wc -c <<< "$revision")" -eq 41
test -z "$(git status --porcelain=v1)"

if bash check_file.sh candidate-bad.txt oracle.txt \
  > "$evidence/ci-direct.stdout" 2> "$evidence/ci-direct.stderr"; then
  printf 'expected direct negative CI-shaped check to fail\n' >&2
  exit 1
else
  ci_direct_status=$?
fi
test "$ci_direct_status" -eq 1

printf 'provider=Orange School local CI simulation\n' \
  > "$evidence/ci-check-record.txt"
printf 'check=contract-direct-negative\n' >> "$evidence/ci-check-record.txt"
printf 'revision=%s\n' "$revision" >> "$evidence/ci-check-record.txt"
printf 'attempt=1\n' >> "$evidence/ci-check-record.txt"
printf 'status=completed\n' >> "$evidence/ci-check-record.txt"
printf 'conclusion=failure\n' >> "$evidence/ci-check-record.txt"
printf 'command=bash check_file.sh candidate-bad.txt oracle.txt\n' \
  >> "$evidence/ci-check-record.txt"
printf 'exit_status=%s\n' "$ci_direct_status" \
  >> "$evidence/ci-check-record.txt"
printf 'artifact=%s/ci-direct.stderr\n' "$evidence" \
  >> "$evidence/ci-check-record.txt"

grep -F -- "revision=$revision" "$evidence/ci-check-record.txt" > /dev/null
grep -F -- 'status=completed' "$evidence/ci-check-record.txt" > /dev/null
grep -F -- 'conclusion=failure' "$evidence/ci-check-record.txt" > /dev/null
grep -F -- 'exit_status=1' "$evidence/ci-check-record.txt" > /dev/null
test -s "$evidence/ci-direct.stderr"

printf 'cmp-103 lab smoke: pass\n'
