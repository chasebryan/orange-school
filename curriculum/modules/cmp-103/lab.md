# Lab: reproduce, test, and interpret a failed check

## Goal

Reproduce and isolate an exact file-contract failure, build a deterministic
three-case test suite with meaningful exit behavior, prove that the suite can
fail, and interpret a revision-bound offline CI-shaped record without
overclaiming.

## Setup

Open a Bash terminal. Confirm the required tools, create one temporary
workspace, and initialize a local repository:

~~~sh
bash --version
git --version
workdir="$(mktemp -d)"
repo="$workdir/contract-project"
evidence="$workdir/evidence"
mkdir -- "$evidence"
git init --quiet --initial-branch=main "$repo"
git -C "$repo" config --local user.name 'Orange School Learner'
git -C "$repo" config --local user.email 'learner.invalid@example.invalid'
printf 'Temporary workspace: %s\n' "$workdir"
~~~

All writes must stay below <code>$workdir</code>. Use no administrator access,
network command, global Git configuration, wildcard, permission change,
deletion command, or existing repository. Run scripts explicitly with
<code>bash</code>; executable permission changes are unnecessary.

Create three exact fixtures:

~~~sh
printf 'mode=study\n' > "$repo/oracle.txt"
printf 'mode=study\n' > "$repo/candidate-good.txt"
printf 'mode=stduy\n' > "$repo/candidate-bad.txt"
~~~

Create <code>check_file.sh</code> with <code>printf</code>, a tool already used
in <code>cmp-101</code>. Each quoted argument below becomes one literal line;
the final redirection writes only inside the temporary repository.

~~~sh
printf '%s\n' \
  '#!/usr/bin/env bash' \
  'set -u' \
  '' \
  'if test "$#" -ne 2; then' \
  '  printf "%s\n" "ERROR: expected candidate and oracle paths" >&2' \
  '  exit 2' \
  'fi' \
  '' \
  'candidate="$1"' \
  'oracle="$2"' \
  'if test ! -f "$candidate" || test ! -f "$oracle"; then' \
  '  printf "%s\n" "ERROR: an input is not a readable regular file" >&2' \
  '  exit 2' \
  'fi' \
  '' \
  'cmp -s -- "$candidate" "$oracle"' \
  'comparison_status="$?"' \
  'case "$comparison_status" in' \
  '  0)' \
  '    printf "%s\n" "PASS: candidate matches oracle"' \
  '    exit 0' \
  '    ;;' \
  '  1)' \
  '    printf "%s\n" "FAIL: candidate differs from oracle" >&2' \
  '    exit 1' \
  '    ;;' \
  '  *)' \
  '    printf "%s\n" "ERROR: comparison could not run" >&2' \
  '    exit 2' \
  '    ;;' \
  'esac' \
  > "$repo/check_file.sh"
~~~

Inspect the file before trusting it:

~~~sh
cat -- "$repo/check_file.sh"
~~~

## Tasks

1. **Write the test plan before running it.** Create
   <code>$evidence/test-plan.txt</code> with these fields for every row: case
   name, exact fixture, action, expected stdout or stderr class, and expected
   checker status.

   | Case | Candidate | Expected checker status | Expected meaning |
   | --- | --- | ---: | --- |
   | exact-match | <code>candidate-good.txt</code> | 0 | candidate equals oracle |
   | content-mismatch | <code>candidate-bad.txt</code> | 1 | readable files differ |
   | missing-input | <code>absent.txt</code> | 2 | comparison setup is invalid |

   Explain in the plan that all three cases pass only when the observed status
   equals the row's expected status.

2. **Reproduce the direct failure twice.** Work from the repository root and
   preserve every channel independently.

   ~~~sh
   cd -- "$repo"
   bash check_file.sh candidate-bad.txt oracle.txt \
     > "$evidence/reproduce-1.stdout" 2> "$evidence/reproduce-1.stderr"
   reproduce_1_status=$?
   printf '%s\n' "$reproduce_1_status" \
     > "$evidence/reproduce-1.status"

   bash check_file.sh candidate-bad.txt oracle.txt \
     > "$evidence/reproduce-2.stdout" 2> "$evidence/reproduce-2.stderr"
   reproduce_2_status=$?
   printf '%s\n' "$reproduce_2_status" \
     > "$evidence/reproduce-2.status"
   ~~~

   Both statuses must be 1, both stdout files empty, and both stderr files
   identical. Preserve the observation before explaining it.

3. **Isolate one condition.** Keep the checker, oracle, directory, and
   environment fixed. Change only the candidate path:

   ~~~sh
   bash check_file.sh candidate-good.txt oracle.txt \
     > "$evidence/control.stdout" 2> "$evidence/control.stderr"
   control_status=$?
   printf '%s\n' "$control_status" > "$evidence/control.status"

   git diff --no-index --no-ext-diff --no-textconv \
     -- candidate-good.txt candidate-bad.txt \
     > "$evidence/fixture.diff" 2> "$evidence/fixture-diff.stderr"
   fixture_diff_status=$?
   printf '%s\n' "$fixture_diff_status" \
     > "$evidence/fixture-diff.status"
   ~~~

   The control status must be 0. The no-index diff status must be 1 because the
   files differ, and its patch must show only <code>study</code> versus
   <code>stduy</code>. This isolates the direct checker's result to the fixture
   content for these cases. It does not establish how the typo arose or what a
   larger system does.

4. **Create the deterministic runner.** This runner preserves each case and
   returns 0 only when all three observed checker statuses match the plan.

   ~~~sh
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
     '' \
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
     '' \
     'run_case exact-match 0 candidate-good.txt' \
     'run_case content-mismatch 1 candidate-bad.txt' \
     'run_case missing-input 2 absent.txt' \
     '' \
     'if test "$failures" -eq 0; then' \
     '  printf "%s\n" "suite=PASS" >> "$evidence/test-summary.txt"' \
     '  exit 0' \
     'fi' \
     'printf "suite=FAIL failures=%s\n" "$failures" >> "$evidence/test-summary.txt"' \
     'exit 1' \
     > "$repo/run_tests.sh"
   ~~~

   Inspect the runner, then run it:

   ~~~sh
   cat -- "$repo/run_tests.sh"
   bash run_tests.sh "$evidence" \
     > "$evidence/suite.stdout" 2> "$evidence/suite.stderr"
   suite_status=$?
   printf '%s\n' "$suite_status" > "$evidence/suite.status"
   cat -- "$evidence/test-summary.txt"
   ~~~

   The suite status must be 0, every case must say <code>result=PASS</code>, and
   the summary must end with <code>suite=PASS</code>. Inspect the individual
   stdout and stderr files to confirm their diagnostic classes.

5. **Prove the runner can fail.** Preserve the original bad fixture, replace it
   temporarily with matching content, run the unchanged suite, then restore
   the exact bad fixture with <code>printf</code>:

   ~~~sh
   cat -- candidate-bad.txt > "$evidence/candidate-bad.original"
   printf 'mode=study\n' > candidate-bad.txt
   bash run_tests.sh "$evidence" \
     > "$evidence/violated-suite.stdout" \
     2> "$evidence/violated-suite.stderr"
   violated_suite_status=$?
   printf '%s\n' "$violated_suite_status" \
     > "$evidence/violated-suite.status"
   cat -- "$evidence/test-summary.txt" \
     > "$evidence/violated-test-summary.txt"
   cat -- "$evidence/candidate-bad.original" > candidate-bad.txt
   ~~~

   The violated suite status must be nonzero. Its summary must show expected 1,
   actual 0 for <code>content-mismatch</code>, plus
   <code>suite=FAIL</code>. After restoring, rerun the suite and require 0 so
   later evidence describes the original fixtures.

6. **Commit the exact test revision.** Review and commit only the five project
   files; external evidence remains untracked by this repository because it is
   a sibling directory.

   ~~~sh
   bash run_tests.sh "$evidence" \
     > "$evidence/final-suite.stdout" 2> "$evidence/final-suite.stderr"
   final_suite_status=$?
   printf '%s\n' "$final_suite_status" > "$evidence/final-suite.status"
   cat -- "$evidence/test-summary.txt" > "$evidence/final-test-summary.txt"

   git status --porcelain=v1 --branch > "$evidence/precommit.status"
   git add -- oracle.txt candidate-good.txt candidate-bad.txt \
     check_file.sh run_tests.sh
   git diff --cached --no-ext-diff --no-textconv \
     -- oracle.txt candidate-good.txt candidate-bad.txt \
     check_file.sh run_tests.sh > "$evidence/test-system.staged.patch"
   git commit --quiet -m 'Add deterministic file contract checks'
   revision="$(git rev-parse --verify 'HEAD^{commit}')"
   printf '%s\n' "$revision" > "$evidence/revision.sha"
   ~~~

   The final suite status must be 0. The full revision now identifies the exact
   checker, runner, and fixtures that produced the preserved record.

7. **Create a failing CI-shaped exercise record.** Rerun the exact negative
   comparison directly at the committed revision:

   ~~~sh
   bash check_file.sh candidate-bad.txt oracle.txt \
     > "$evidence/ci-direct.stdout" 2> "$evidence/ci-direct.stderr"
   ci_direct_status=$?
   printf '%s\n' "$ci_direct_status" > "$evidence/ci-direct.status"

   printf 'provider=Orange School local CI simulation\n' \
     > "$evidence/ci-check-record.txt"
   printf 'check=contract-direct-negative\n' \
     >> "$evidence/ci-check-record.txt"
   printf 'revision=%s\n' "$revision" \
     >> "$evidence/ci-check-record.txt"
   printf 'attempt=1\n' >> "$evidence/ci-check-record.txt"
   printf 'status=completed\n' >> "$evidence/ci-check-record.txt"
   printf 'conclusion=failure\n' >> "$evidence/ci-check-record.txt"
   printf 'command=bash check_file.sh candidate-bad.txt oracle.txt\n' \
     >> "$evidence/ci-check-record.txt"
   printf 'exit_status=%s\n' "$ci_direct_status" \
     >> "$evidence/ci-check-record.txt"
   printf 'artifact=%s/ci-direct.stderr\n' "$evidence" \
     >> "$evidence/ci-check-record.txt"
   cat -- "$evidence/ci-check-record.txt"
   ~~~

   This is an offline exercise record, not a hosted run. Write
   <code>$evidence/ci-interpretation.txt</code> with:

   - the exact provider, check, revision, status, conclusion, command, status,
     and artifact observation;
   - the strongest supported one-sentence conclusion;
   - at least five claims the record does not establish; and
   - the next two pieces of evidence you would collect.

   Explain why the direct negative check concludes failure while the full test
   suite concludes success: the suite expected that particular checker status
   and translated the matched expectation into a passing case.

## Verification

Run these read-only checks and preserve their statuses. <code>grep -F -- TEXT
FILE</code> searches for the exact fixed text in one file: status 0 means it was
found, 1 means it was not found, and a larger status reports a search error.
It prints a matching line, so its output is also visible evidence here.

~~~sh
test "$(cat -- "$evidence/reproduce-1.status")" -eq 1
test "$(cat -- "$evidence/reproduce-2.status")" -eq 1
cmp -s -- "$evidence/reproduce-1.stdout" "$evidence/reproduce-2.stdout"
cmp -s -- "$evidence/reproduce-1.stderr" "$evidence/reproduce-2.stderr"
test "$(cat -- "$evidence/control.status")" -eq 0
test "$(cat -- "$evidence/fixture-diff.status")" -eq 1
test "$(cat -- "$evidence/violated-suite.status")" -ne 0
grep -F -- 'suite=FAIL' "$evidence/violated-test-summary.txt"
test "$(cat -- "$evidence/final-suite.status")" -eq 0
grep -F -- 'suite=PASS' "$evidence/final-test-summary.txt"
test "$(git rev-parse --verify 'HEAD^{commit}')" = \
  "$(cat -- "$evidence/revision.sha")"
test "$(cat -- "$evidence/ci-direct.status")" -eq 1
grep -F -- 'status=completed' "$evidence/ci-check-record.txt"
grep -F -- 'conclusion=failure' "$evidence/ci-check-record.txt"
test -s "$evidence/ci-interpretation.txt"
~~~

Do not treat the checks' silence as a complete review. Open the plan, all
result channels, summaries, patch, CI-shaped record, and interpretation.
Confirm that the evidence distinguishes checker rejection, harness error, test
case result, suite result, and CI-record conclusion.

## Reflection

Append answers to <code>ci-interpretation.txt</code>:

- Which single changed condition isolated the direct failure, and what causal
  claim remains unsupported?
- Why is the expected checker status different from the test case result for a
  negative case?
- How did you demonstrate that the runner is capable of reporting failure?
- Which fields bind the CI-shaped record to an exact run, and what would a real
  provider need to authenticate or retain?
