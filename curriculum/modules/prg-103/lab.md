# Lab: build and debug a fail-closed retry plan

## Goal

Build a small Python package whose annotated boundary accepts a task name and a
retry count, returns distinct success or failure records, and preserves useful
error context. Reproduce one overly broad input check, convert it into a focused
unit test, diagnose it, repair it, and retain before-and-after evidence.

## Setup

Start at the repository root. Verify the provided example before creating your
working copy:

```sh
cd curriculum/modules/prg-103
python3 checks/lab_smoke.py
baseline_status=$?
printf 'baseline smoke status: %s\n' "$baseline_status"
```

Stop if the status is nonzero. Read the reported failing test instead of working
around it.

Create a private temporary workspace and copy the example only as a reference:

```sh
module_dir="$PWD"
workdir="$(mktemp -d)"
printf 'lab workspace: %s\n' "$workdir"
cp -R "$module_dir/example" "$workdir/reference-example"
cd "$workdir"
mkdir -p retry_plan tests evidence
touch retry_plan/__init__.py tests/__init__.py
```

All lab writes must remain under the printed temporary path. Use Python 3.11 or
newer and standard-library modules only. Do not use package installation,
network commands, administrator access, or deletion commands.

## Tasks

1. **Write the contract before the implementation — PRG-103-01.** Create
   `contract.md` with this exact public signature:

   ```python
   def build_retry_plan(task_name: str, retry_count_text: str) -> PlanResult:
       ...
   ```

   Record these invariants:

   - `task_name` is 1 through 32 characters, uses ASCII letters, ASCII digits,
     or `-`, and begins with an ASCII letter;
   - `retry_count_text` is one or more ASCII decimal digits representing 0
     through 5;
   - a success contains the validated name, retry count, and
     `total_attempts == retry_count + 1`; and
   - a failure contains an error code, field, bounded received-value context,
     and message, but no plan or total-attempt count.

   State whether leading zeroes in the retry count are accepted. Either policy
   is allowed, but implementation and tests must agree with it.

2. **Reproduce an overly broad predicate — PRG-103-02.** In
   `evidence/reproduce.py`, define this training-only predicate:

   ```python
   def broad_name_check(text: str) -> bool:
       return bool(text) and text.replace("-", "").isalnum()
   ```

   Use a direct assertion to show that it incorrectly accepts at least one
   non-ASCII name under your contract. Run the script, preserve its nonzero exit
   status and traceback in `evidence/before.txt`, and record the exact input.
   Minimize the input if a shorter value reproduces the same rule violation.

3. **Turn the reproduction into one focused unit test — PRG-103-02.** Create
   `tests/test_retry_plan.py`. Before repairing the boundary, add a test that
   calls the public function with the minimized input and asserts the required
   failure variant, code, and field. Run only that test and preserve the failing
   command, output, and status in `evidence/focused-before.txt`.

   In `evidence/diagnosis.md`, record:

   - observed result;
   - violated invariant;
   - hypothesis about `str.isalnum()`;
   - one experiment comparing the relevant string predicates; and
   - conclusion and proposed narrow repair.

4. **Implement explicit result variants — PRG-103-01 and PRG-103-03.** In
   `retry_plan/plan.py`, create frozen data classes for a successful plan, an
   input error, and a failure result. Define `PlanResult` as the union of success
   and failure. Implement `build_retry_plan` so every invalid input returns a
   failure before a plan is constructed.

   Preserve field, stable code, bounded `repr`-style received context, and a
   useful message. Do not silently strip whitespace, replace invalid input,
   default the retry count, return a partial plan, or catch every exception with
   a generic message. Keep diagnostic context at 80 characters or fewer and do
   not include any secret value.

5. **Complete the focused repair and boundary suite.** Make the smallest change
   that enforces the ASCII name invariant. Run the focused test and save its
   passing output and status in `evidence/focused-after.txt`. Then add tests for:

   - one normal success and both retry-count boundaries;
   - empty and overlength names;
   - a name whose first character is not a letter;
   - whitespace in either field;
   - empty, signed, non-ASCII, and out-of-range retry counts;
   - a runtime non-string value reaching the unchecked boundary; and
   - a failure whose code, field, value context, and absence of a plan are all
     asserted.

   Use `subTest` for inputs that exercise the same rule. Use separate test
   methods for different failure causes.

6. **Run the full suite and summarize the evidence.** Run:

   ```sh
   python3 -m unittest discover -s tests -v > evidence/full.stdout 2> evidence/full.stderr
   full_status=$?
   printf '%s\n' "$full_status" > evidence/full.status
   ```

   Create `evidence/summary.md` naming the contract, reproduced failure, focused
   test, diagnosis, repair, full-suite result, and at least two limits of the
   evidence.

## Verification

Confirm that the final full-suite status is zero and inspect both output files:

```sh
cat evidence/full.stdout
cat evidence/full.stderr
cat evidence/full.status
test "$(cat evidence/full.status)" = "0"
```

Then run these direct checks from the workspace root, adjusting only the imported
class names to match your package:

```sh
python3 - <<'PY'
from retry_plan.plan import PlanFailure, PlanSuccess, build_retry_plan

success = build_retry_plan("compile-1", "2")
assert isinstance(success, PlanSuccess)
assert success.total_attempts == success.retry_count + 1

failure = build_retry_plan("compile-1", " 2")
assert isinstance(failure, PlanFailure)
assert failure.error.field == "retry_count_text"
assert not hasattr(failure, "total_attempts")
print("direct contract checks passed")
PY
```

Finally verify that `evidence/focused-before.txt` records a nonzero test status
and `evidence/focused-after.txt` records zero for the same focused test. A final
green suite without the reproduced failure and diagnosis does not complete the
lab.

## Reflection

Answer in `evidence/summary.md`:

1. Which annotation and invariants define the public boundary, and which checks
   enforce them at runtime?
2. What observation distinguished the real cause from your first hypothesis?
3. Why can the failure variant not be mistaken for an approved retry plan?
4. Which context did you retain, and what context would be unsafe or excessive?
5. What does the passing suite establish, and which inputs or integrations
   remain outside its evidence?
