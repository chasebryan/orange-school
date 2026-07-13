# Lab: bounded collection algorithms

## Goal

Choose collections from explicit requirements, trace four small algorithms,
and implement a bounded variant with normal, boundary, and invalid tests.

## Setup

From the repository root, verify the supplied examples:

~~~sh
cd curriculum/modules/prg-102
python3 --version
python3 checks/lab_smoke.py
~~~

The final command must print <code>prg-102 lab smoke: PASS</code> and exit 0.
It uses only local files and the Python standard library.

Create a contained workspace for your code:

~~~sh
workdir="$(mktemp -d)"
cd -- "$workdir"
pwd
~~~

Use a plain-text editor. Keep every new file in the printed path. No network,
administrator, permission-changing, or deletion command is required.

## Tasks

1. **Choose representations.** For each requirement, choose a list, tuple,
   dictionary, or set and justify it with required operations and an invariant:
   - editable readings where order and repeated values matter;
   - one fixed <code>(row, column)</code> coordinate;
   - unique student ID to current score lookup;
   - membership in the set of already processed IDs.
   Then state one way each choice could still be misused.
2. **Trace algorithms.** For values
   <code>["build", "test", "build", "ship"]</code> and target
   <code>"build"</code>, trace:
   - every comparison made by linear first-match search;
   - the count dictionary after each input;
   - <code>seen</code> and result after each stable-deduplication step; and
   - the ordered copy and unchanged original.
3. **Implement a changed case.** Create <code>bounded_tasks.py</code> with
   <code>MAX_TASKS = 20</code> and functions that:
   - reject an empty list, more than 20 labels, or a label that is not 1 through
     12 lowercase ASCII letters;
   - return the first index of a target or <code>None</code>;
   - return a dictionary of label counts;
   - return a first-occurrence-order list without duplicates; and
   - return an ordered tuple without changing the input list.

   Keep validation separate from the four algorithms. In comments or a short
   record, justify every chosen representation.
4. **State bounds before testing.** For input size <code>n</code> and distinct
   count <code>u</code>, state time and extra-space growth for each algorithm.
   Distinguish expected hash-table behavior from a guaranteed worst case.
   Translate <code>MAX_TASKS</code> into a maximum linear-search comparison
   count and maximum collection sizes.
5. **Test the contract.** In <code>test_bounded_tasks.py</code>, use
   <code>unittest</code> or simple assertions to cover:
   - a target at the first position, last position, and absent;
   - repeated labels and all-unique labels;
   - ordering without input mutation;
   - one label, exactly 20 labels, empty input, 21 labels, uppercase text, an
     overlong label, and punctuation.

## Verification

Run:

~~~sh
python3 -m unittest -v
test_status=$?
printf 'test status: %s\n' "$test_status"
~~~

A passing lab has status 0 and evidence that:

- each representation justification names both an operation and invariant;
- the hand traces agree with observed results;
- all four algorithms meet their return contracts;
- ordering leaves the original list unchanged;
- all input bounds are checked before algorithmic processing; and
- normal, exact-boundary, and invalid tests pass.

Also rerun <code>python3 checks/lab_smoke.py</code> from the module directory to
distinguish the unchanged repository examples from your temporary lab code.

## Reflection

Write four to six sentences:

- Which requirement determined each representation?
- Where does expected complexity depend on hashing?
- What concrete work limit follows from <code>MAX_TASKS = 20</code>?
- Which test would expose accidental mutation or loss of first-occurrence
  order?
