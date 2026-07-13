# Tests, debugging, automation, and CI

A failure report becomes useful when another person can reproduce the same
observation, separate the failing condition from nearby conditions, and run a
check whose exit behavior is unambiguous. Continuous integration (CI) can run
such checks at a recorded revision, but a CI label never proves more than the
checks and environment represented by its evidence.

This module uses exact text files and small Bash checkers. It teaches every
shell control construct it requires; no prior programming course or hosted CI
account is assumed.

## Learning objectives

- **CMP-103-01:** Reproduce a failure and isolate the smallest input or
  condition that triggers it.
- **CMP-103-02:** Design and run tests with unambiguous pass or fail exit
  behavior.
- **CMP-103-03:** Interpret a CI check record without extending its result
  beyond the tested scope.

## Prerequisites

Pass <code>cmp-102</code>. Through that path, you should be able to work inside
a fresh temporary directory, preserve stdout, stderr, and immediate exit
status, create focused Git history, inspect a full <code>HEAD</code> revision,
and distinguish observations from claims.

Use the course Bash and Git environment. Check both tools:

~~~sh
bash --version
git --version
~~~

If either command fails, stop and report the environment blocker. The examples
write only below a new path from <code>mktemp -d</code>, use no network or
hosted service, and do not require administrator access, global configuration,
wildcards, permission changes, deletion commands, or prior code.

## Lesson

### Reproduce before explaining

A **symptom** is an observed result: command, stdout, stderr, status, and
affected artifact. A **hypothesis** is a possible explanation. A **cause** is
an explanation supported strongly enough by controlled evidence. Calling the
first plausible idea “the cause” skips the investigation.

A reproducible failure record answers:

1. What exact revision and environment were used?
2. What setup and input existed before the command?
3. What exact command ran, from which directory?
4. What stdout, stderr, exit status, and changed artifacts were observed?
5. Does the same setup produce the same observation on a repeated run?
6. What smaller or contrasting case changes the result?
7. What conclusion follows, and what remains untested?

Preserve the original evidence before trying a fix. Then use this bounded loop:

1. **Reproduce:** rerun the exact recorded case without changing inputs.
2. **Reduce:** remove irrelevant setup while keeping the same symptom.
3. **Contrast:** vary one condition and hold the command, tool, environment,
   and other inputs constant.
4. **Hypothesize:** predict what observation the proposed cause implies.
5. **Check:** run a case that could disprove that prediction.
6. **Record:** separate observation, inference, and remaining uncertainty.

One changed condition gives stronger isolation than many simultaneous edits.
It still may establish only a local mechanism. If correcting one line changes
one checker result, that supports a claim about those fixtures; it does not by
itself explain who introduced the line or whether the same mechanism caused a
production incident.

### A test is an evidence contract

Each test case needs five explicit fields:

- **name:** a stable identifier;
- **fixture:** the exact starting input and environment;
- **action:** the exact command or operation;
- **oracle:** the expected observable result;
- **comparison:** the actual observation and whether it matches the oracle.

An oracle is the rule used to decide the expected result. It must not be copied
from the output under test during the same run, or the test can agree with its
own mistake. This module stores a reviewed expected file separately from each
candidate file.

A good test is deterministic within its declared envelope: the same revision,
fixtures, command, and supported environment should produce the same assessed
observation. Avoid time, random data, shared mutable files, network services,
and unspecified ordering unless the test explicitly controls them.

Positive and negative cases answer different questions:

- A **positive case** supplies valid input and expects success.
- A **negative case** deliberately supplies invalid or unequal input and
  expects the checker to reject it.
- A **harness-error case** verifies that missing setup is reported distinctly
  rather than mislabeled as a product mismatch.

A negative case can pass as a test even though the checker command returns 1.
The case passes when its observed status equals its expected status. The suite
then returns 0 only if every case met its oracle.

### Give exit statuses a documented interface

The checker below compares a candidate file with an independently prepared
oracle. This course checker defines:

- 0: candidate and oracle are byte-for-byte equal;
- 1: both inputs were readable files but their content differs;
- 2: the checker could not perform a valid comparison.

Those meanings belong to this checker. Do not assume every tool assigns the
same nonzero values. A CI provider commonly treats any nonzero top-level step
status as failure, so the suite must translate expected negative-case statuses
into an overall 0 when they match their test plan.

~~~sh
#!/usr/bin/env bash
set -u

if test "$#" -ne 2; then
  printf "%s\n" "ERROR: expected candidate and oracle paths" >&2
  exit 2
fi

candidate="$1"
oracle="$2"
if test ! -f "$candidate" || test ! -f "$oracle"; then
  printf "%s\n" "ERROR: an input is not a readable regular file" >&2
  exit 2
fi

cmp -s -- "$candidate" "$oracle"
comparison_status="$?"
case "$comparison_status" in
  0)
    printf "%s\n" "PASS: candidate matches oracle"
    exit 0
    ;;
  1)
    printf "%s\n" "FAIL: candidate differs from oracle" >&2
    exit 1
    ;;
  *)
    printf "%s\n" "ERROR: comparison could not run" >&2
    exit 2
    ;;
esac
~~~

The first line selects Bash when the file is run as a command, although this
module invokes it explicitly as <code>bash check_file.sh</code> and does not
change permissions. <code>set -u</code> reports an unset variable; the argument
count check runs before <code>$1</code> or <code>$2</code> is read.

<code>test</code> evaluates a condition by exit status. The spaces around its
arguments are required. <code>||</code> means “or”: the error branch runs if
either path is not a regular file. <code>case</code> chooses behavior from the
preserved <code>cmp</code> status. Each branch ends with an explicit
<code>exit</code>, which makes the checker's interface reviewable.

The checker does not use <code>set -e</code> because statuses 1 and 2 are
expected observations that must be classified. Blind automatic exit can stop
a script before it records an intentional negative case.

### Make the suite test the checker

A runner should preserve each case independently and return nonzero if any
observed result violates the plan. This Bash function introduces only the
control flow needed for that contract:

~~~sh
run_case() {
  name="$1"
  expected_status="$2"
  candidate_path="$3"

  bash check_file.sh "$candidate_path" oracle.txt \
    > "$evidence/$name.stdout" 2> "$evidence/$name.stderr"
  actual_status="$?"
  printf 'case=%s expected=%s actual=%s\n' \
    "$name" "$expected_status" "$actual_status" \
    >> "$evidence/test-summary.txt"

  if test "$actual_status" -eq "$expected_status"; then
    printf 'case=%s result=PASS\n' "$name" >> "$evidence/test-summary.txt"
  else
    printf 'case=%s result=FAIL\n' "$name" >> "$evidence/test-summary.txt"
    failures=$((failures + 1))
  fi
}
~~~

A function names a reusable group of commands. Its <code>$1</code>,
<code>$2</code>, and <code>$3</code> are the function call's arguments.
<code>$((failures + 1))</code> performs integer arithmetic. Quoting every path
keeps it one argument. The function captures the checker status before
<code>printf</code> can overwrite it. In the complete runner,
<code>: &gt; "$evidence/test-summary.txt"</code> uses Bash's no-op
<code>:</code> command with redirection to create or empty that one summary
file before cases append their results.

The runner initializes <code>failures=0</code>, calls the function once per
planned case, then decides the suite result:

~~~sh
if test "$failures" -eq 0; then
  printf '%s\n' 'suite=PASS' >> "$evidence/test-summary.txt"
  exit 0
fi

printf 'suite=FAIL failures=%s\n' "$failures" \
  >> "$evidence/test-summary.txt"
exit 1
~~~

The suite's status is itself part of the interface. Test the test system: make
one fixture violate its expected result and confirm that the runner returns
nonzero. A runner that always returns 0 can make every CI display green while
detecting nothing.

### Read a CI record without strengthening it

CI providers differ, so use the provider's documented fields and semantics. A
useful completed check record normally identifies:

- provider, repository, check name, run or attempt, and trigger;
- full revision tested, not merely a branch label;
- status such as queued, in progress, or completed;
- final conclusion such as success, failure, canceled, skipped, or timed out;
- exact command or workflow revision and runner environment;
- logs, annotations, test summary, and retained artifacts;
- start and completion times.

Status and conclusion are not interchangeable. A queued check has no final
test conclusion. A completed failure at revision <code>R</code> supports the
narrow claim that the provider recorded that check as failed for that run of
<code>R</code>. The label alone does not identify the failing assertion, prove
the code is defective, show whether setup failed, establish that another
revision behaves the same, or say whether other checks passed.

Likewise, a completed success supports only the tests actually run in the
recorded envelope. It does not prove absence of defects, complete test
coverage, security, production readiness, or success on a newer branch tip.

Use this interpretation order:

1. Confirm the provider and its definitions.
2. Confirm the record is completed and note its conclusion.
3. Match the full tested revision to the revision under discussion.
4. Read the exact failed step, command, exit status, and first relevant
   diagnostic.
5. Check whether logs or artifacts are complete enough to reproduce it.
6. State one supported claim, label any inference, list missing evidence, and
   choose the next discriminating check.

The lab creates an offline **CI-shaped exercise record**. It is not a hosted CI
run. Its purpose is to practice field-by-field interpretation without an
account or network dependency.

## Worked example

Suppose a check record says:

~~~text
provider=Orange School local CI simulation
check=contract-direct-negative
revision=0123456789abcdef0123456789abcdef01234567
attempt=1
status=completed
conclusion=failure
command=bash check_file.sh candidate-bad.txt oracle.txt
exit_status=1
artifact=evidence/direct-negative.stderr
~~~

The corresponding artifact says that the candidate differs from the oracle.
A precise interpretation is:

> The completed simulated check recorded status 1 for the named comparison at
> the full listed revision, and its retained diagnostic classifies a content
> mismatch.

That record does not prove why the content differs, who changed it, whether the
runner suite as a whole fails, whether another platform behaves the same, or
whether a hosted provider ran it. The next check is to reproduce the exact
command at the listed revision, preserve all result channels, and compare a
one-condition control fixture.

## Check your understanding

1. Distinguish symptom, hypothesis, and supported cause.
2. What fields make a failure reproducible?
3. Why can a negative test case pass when its checker exits 1?
4. Why should a checker distinguish “content differs” from “input was
   missing”?
5. How do you prove that a test runner can detect a violated expectation?
6. A check is <code>in_progress</code>. What final claim can you make?
7. A completed check says <code>success</code> for revision <code>R</code>.
   Name four broader claims that are not established.

**Answers:** (1) a symptom is observed, a hypothesis is a proposed explanation,
and a cause requires discriminating evidence; (2) exact revision, environment,
setup, inputs, directory, command, stdout, stderr, status, artifacts, repeat
observation, and limits; (3) the case expects rejection and passes when actual
status 1 matches that oracle, while the suite translates the match to overall
success; (4) product mismatch and invalid test setup require different action;
(5) deliberately violate one expected result and observe the suite return
nonzero; (6) only that the check has not reached a final recorded conclusion;
(7) it does not establish complete coverage, absence of defects, security,
production readiness, or behavior of another revision or environment.

## Next step

Complete the [lab](lab.md) in one fresh temporary workspace. Preserve both the
successful suite record and the direct failing check record. Then complete the
[independent assessment](assessment.md). Passing requires at least 80/100 and
every critical criterion in the [rubric](rubric.md).

## Sources

- IEEE/The Open Group, [POSIX.1-2024 Shell Command
  Language](https://pubs.opengroup.org/onlinepubs/9799919799/utilities/V3_chap02.html),
  command exit status, conditionals, functions, and shell execution.
- Free Software Foundation, [GNU Bash Reference
  Manual](https://www.gnu.org/software/bash/manual/bash.html), Bash 5 shell
  parameters, functions, conditionals, arithmetic expansion, and exit status.
- Free Software Foundation, [GNU Coreutils <code>cmp</code>
  manual](https://www.gnu.org/software/diffutils/manual/html_node/Invoking-cmp.html),
  byte comparison and result statuses.
- GitHub Docs, [Setting exit codes for
  actions](https://docs.github.com/en/actions/how-tos/create-and-publish-actions/set-exit-codes)
  and [REST API endpoints for check
  runs](https://docs.github.com/en/rest/checks/runs), one concrete provider's
  exit-code, status, conclusion, revision, and check-record semantics. Other
  providers require their own documentation.
- [Assessment system](../../../docs/assessment-system.md), observable evidence,
  critical criteria, and retry policy.
