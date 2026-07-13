# Assessment: failure isolation, test contract, and CI evidence

## Instructions

Complete the assessment in one fresh temporary workspace without copying the
lab's fixture names, exact content, or test-case names. You may consult the
lesson, Bash documentation, Git documentation, and documentation for the CI
record format supplied by the assessor. No hosted CI account or network access
is required.

Use no administrator access, network command, global Git configuration,
wildcard, permission change, deletion command, or existing repository. Invoke
your scripts explicitly with Bash. Keep the complete workspace for review.

Submit the workspace path, exact transcript, full Git revision, source files,
test plan, per-case observations, suite summaries, preserved failed-run
evidence, CI-record interpretation, and knowledge answers.

This assessment covers:

- **CMP-103-01:** Reproduce a failure and isolate the smallest input or
  condition that triggers it.
- **CMP-103-02:** Design and run tests with unambiguous pass or fail exit
  behavior.
- **CMP-103-03:** Interpret a CI check record without extending its result
  beyond the tested scope.

## Knowledge check

1. Distinguish a symptom, a hypothesis, and a supported cause. Give one example
   of an observation that does not yet establish its cause.
2. List the fields of a reproducible failure record and explain why the exact
   revision and unchanged repeat run both matter.
3. Define fixture, action, oracle, observed result, test-case result, and suite
   result. Explain how a negative case can pass while its checker exits
   nonzero.
4. Explain why the checker and runner must distinguish assertion mismatch,
   invalid setup, and overall suite failure.
5. A record says <code>status=in_progress</code>. What final conclusion is
   supported? A second record says <code>status=completed</code> and
   <code>conclusion=success</code> for revision <code>R</code>. Name five
   broader claims that remain unsupported.
6. Describe one deliberate mutation that would demonstrate that a runner does
   not always return success.

## Independent task

1. **Reproduction and isolation — CMP-103-01.** Create an oracle with the exact
   lines <code>profile=release</code> and <code>retries=2</code>. Create a
   candidate with <code>profile=debug</code> and <code>retries=2</code>. Write a
   checker with documented statuses 0 for equality, 1 for readable-content
   mismatch, and 2 for invalid comparison setup. Record the exact environment,
   revision state, fixtures, directory, command, stdout, stderr, and immediate
   status. Reproduce the mismatch twice without changes and show that the
   result channels agree. Create a control candidate that differs only by
   changing <code>profile=debug</code> to <code>profile=release</code>. Record a
   no-index diff and state the narrow mechanism isolated plus at least two
   possible causes not established.
2. **Test design and execution — CMP-103-02.** Before execution, write a test
   plan with at least four deterministic cases: the matching control from task
   1; the <code>profile=debug</code> mismatch; a second candidate containing
   <code>profile=release</code> and <code>retries=3</code>; and a missing-input
   case. Each row must name its fixture, action, expected channel class,
   expected checker status, and reason. Build a runner that records expected
   and observed status per case and exits 0 only when all expectations match.
   Preserve a passing run. Then alter the retries-mismatch fixture so it equals
   the oracle while the runner still expects status 1, preserve the nonzero
   suite run, restore the exact <code>retries=3</code> fixture explicitly, and
   preserve a second passing run. Keep every case isolated from another case's
   output.
3. Commit the reviewed checker, runner, oracle, and fixtures in one focused
   commit after the final passing run. Preserve its full commit ID, staged
   patch, clean status, Bash version, Git version, and final suite evidence.
4. **CI interpretation — CMP-103-03.** At the committed revision, run the
   checker directly on the <code>profile=debug</code> candidate and oracle,
   preserving its stdout, stderr, and status. Create an offline CI-shaped record
   with the literal provider name <code>Orange School local CI
   simulation</code>, check name <code>profile-direct-negative</code>, full
   current revision, attempt 1, completed status, failure conclusion, exact
   command, observed exit status, and artifact paths. Match its full revision
   to the submitted repository and trace its command to the retained evidence.
   Write the strongest supported conclusion, clearly label any inference, list
   at least five unsupported broader claims, identify missing or contradictory
   evidence, and propose the next two discriminating checks. Explain why this
   is not a hosted run and why the direct check can fail while the full suite
   passes its expected negative case.
5. Provide read-only verification commands and their immediate statuses for
   repeated reproduction, control contrast, planned case coverage, runner
   failure sensitivity, final suite success, exact revision match, and every
   CI artifact used in the interpretation.

## Completion criteria

The [rubric](rubric.md) requires at least 80/100 and every critical criterion.
Passing evidence must show:

- unchanged repeated failure plus a one-condition control and bounded causal
  statement for **CMP-103-01**;
- a prewritten deterministic test plan, distinct checker statuses, per-case
  evidence, a meaningful suite status, and both failure-sensitive and restored
  passing runs for **CMP-103-02**; and
- an exact-revision, provider-aware, artifact-backed interpretation whose
  claims remain within the check record for **CMP-103-03**.

A guessed cause, an always-successful runner, a CI color without revision and
artifacts, or a total score below the threshold cannot pass.
