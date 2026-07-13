# Lab: trace, run, and test a stateful program

## Goal

Trace program state, run two bounded Python examples, and build a test record
that distinguishes normal, boundary, and invalid input.

## Setup

From the repository root, enter this module and verify the supplied examples:

~~~sh
cd curriculum/modules/prg-101
python3 --version
python3 checks/lab_smoke.py
~~~

The last command must print <code>prg-101 lab smoke: PASS</code> and exit 0.
The smoke check uses only local files and the standard library.

For your editable work, create a fresh temporary directory and copy one example:

~~~sh
workdir="$(mktemp -d)"
cp -- examples/reading_goal.py "$workdir/"
cd -- "$workdir"
pwd
~~~

Use a plain-text editor to open the copied file. All edits and new files in
this lab stay in the printed temporary directory. No network, administrator,
permission-changing, or deletion command is needed.

## Tasks

1. **Trace before running.** For <code>goal = 4</code> and readings
   <code>[2, 4, 7]</code>, make a table with one row before the loop and one per
   iteration. Record <code>pages</code>, <code>total_pages</code>, the
   comparison result, and <code>days_meeting_goal</code>. Predict the returned
   pair.
2. **Run and compare.** Execute:

   ~~~sh
   python3 reading_goal.py 4 2 4 7 > normal.stdout 2> normal.stderr
   normal_status=$?
   printf '%s\n' "$normal_status" > normal.status
   ~~~

   Compare the observed total and count with the trace. If they differ, inspect
   the first differing state rather than changing the expected answer.
3. **Exercise a branch boundary.** Predict and run a one-day reading exactly
   equal to the goal. Preserve all three result channels in files beginning
   with <code>boundary.</code>. Explain why equality follows the “met” branch.
4. **Exercise invalid input.** Run one non-integer goal and one negative
   reading. Preserve stdout, stderr, and status for each. Confirm that neither
   invalid run prints a report to stdout, both diagnostics explain the input
   contract, and both statuses are nonzero.
5. **Inspect decomposition.** In your copy, identify:
   - the function that converts one text input;
   - the function that validates and updates state;
   - the function that formats output; and
   - the function that coordinates the command line.

   For each, write one sentence describing its inputs, result, and reason for
   existing separately.
6. **Make one controlled change.** Add a report line named
   <code>pages remaining today</code>. It should be zero when the final reading
   meets the goal and otherwise be <code>goal - final reading</code>. Put the
   calculation in a function. Add and run one normal, one equality-boundary,
   and one invalid case. Preserve the before-and-after command record.

## Verification

Your lab record is complete when:

- the original smoke check exits 0;
- the hand trace and normal run agree at every state transition;
- the equality boundary takes the expected branch;
- invalid input writes a diagnostic to stderr, no report to stdout, and exits
  nonzero;
- each function has one stated job; and
- the changed copy passes its three new cases without changing the supplied
  repository example.

Run Python's syntax compiler on your edited copy:

~~~sh
python3 -m py_compile reading_goal.py
syntax_status=$?
printf 'syntax check: %s\n' "$syntax_status"
~~~

This creates a local cache inside the temporary directory. A zero status means
the file is syntactically valid; it does not replace the behavior tests.

## Reflection

Write four to six sentences:

- Which trace row first determined the final answer?
- Which state was mutable, and which values stayed unchanged?
- Which test would have caught an incorrect <code>&gt;</code> in place of
  <code>&gt;=</code>?
- What does your test record still not establish?
