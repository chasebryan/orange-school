# Assessment: a reliable bounded job request

## Instructions

Work independently in a fresh temporary directory. You may consult the lesson,
Python standard-library documentation, and your own completed lab evidence. Do
not copy the quote example or retry-plan implementation. Use Python 3.11 or
newer, standard-library modules only, and no network or administrator access.

Submit the complete package, tests, `contract.md`, `debug-record.md`, and an
exact transcript showing the focused failure before the repair, the same test
passing after the repair, and the final full suite. Preserve stdout, stderr, and
exit status for each assessed run.

This assessment covers these outcomes:

- **PRG-103-01:** Use type annotations and explicit invariants to define accepted
  inputs and outputs.
- **PRG-103-02:** Turn a reproduced failure into a focused unit test and diagnose
  it systematically.
- **PRG-103-03:** Design explicit error results that fail closed without hiding
  context.

## Knowledge check

1. Explain what a Python type annotation communicates and what it does not
   enforce at runtime. Give one invariant that cannot be expressed by `str`
   alone.
2. Explain the difference between a successful result variant, a structured
   failure variant, `None`, and an uncaught conversion exception at an input
   boundary.
3. This parser violates a contract that forbids surrounding whitespace:

   ```python
   def parse_workers(text: str) -> int:
       return int(text.strip())
   ```

   Give the smallest reproducing input, the focused assertion you would add,
   and one experiment that distinguishes stripping from integer conversion as
   the cause.
4. Put these actions in a defensible order and explain why: edit the boundary,
   minimize the input, run the complete suite, reproduce the failure, write a
   focused test, form a hypothesis, rerun the focused test.
5. Name the minimum context an explicit input error should retain. Give one
   example of context that should be bounded or omitted.

## Independent task

Create a package named `job_request` with a `request.py` module and a
standard-library `unittest` suite. Implement this public boundary exactly:

```python
def build_job_request(job_name: str, worker_count_text: str) -> JobResult:
    ...
```

1. **Annotated contract and invariants — PRG-103-01.** In `contract.md` and the
   function documentation, define and implement all of these rules:

   - `job_name` is text containing 3 through 24 ASCII lowercase letters, ASCII
     digits, or single hyphens;
   - it begins with a lowercase ASCII letter, ends with a lowercase ASCII letter
     or digit, and contains no adjacent hyphens;
   - `worker_count_text` contains one or more ASCII decimal digits representing
     1 through 16, with no whitespace, sign, separator, or non-ASCII digit;
   - leading zeroes are rejected except that the one-character values `1`
     through `9` remain valid;
   - a success records the normalized-free original job name, worker count, and
     `capacity_units == worker_count * 8`; and
   - a failure records one input error and exposes no job request or capacity.

   Use type annotations on every public function and data-class field. Do not
   strip, lowercase, clamp, default, or otherwise repair caller input silently.

2. **Reproduction, focused test, and diagnosis — PRG-103-02.** Before the final
   repair, reproduce the whitespace defect demonstrated by the knowledge-check
   parser with input `" 2"`. Preserve a failing observation showing that the
   boundary accepted it or failed in the wrong way. Convert that observation
   into one focused unit test against `build_job_request` that requires a
   structured `worker_count_text` failure.

   Preserve the focused test's nonzero status before the repair. In
   `debug-record.md`, record the exact input, command, observed result, minimized
   case, violated invariant, at least two hypotheses, one discriminating
   experiment, the resulting diagnosis, and the narrow repair. After the repair,
   preserve status 0 for the same test before running the full suite.

3. **Explicit fail-closed results — PRG-103-03.** Define frozen data classes for
   the success, input error, and failure variants. Define `JobResult` as the
   success-or-failure union. Every invalid caller value, including a runtime
   non-string value, must return the failure variant without constructing a
   partial job request or exposing `capacity_units`.

   An error must contain a stable code, exact field name, explanatory message,
   and bounded `type:value` context produced with `repr`. Limit that context to
   80 characters. Context must make whitespace visible and contain only the
   assessed value and its runtime type; do not add environment or file contents.

4. **Boundary and regression suite.** Include focused tests for:

   - one ordinary success and every valid worker boundary;
   - the job-name length boundaries and values just outside them;
   - invalid first/last characters, adjacent hyphens, uppercase, whitespace,
     and non-ASCII text;
   - empty, whitespace-padded, signed, leading-zero, non-ASCII, and out-of-range
     worker counts;
   - a runtime non-string value for each input field;
   - exact error code and field selection when either input fails;
   - bounded, visible received-value context; and
   - proof by assertion that failure results expose no `capacity_units`.

   Use at least one `subTest` table for cases governed by the same rule. Run the
   focused test first, then the full discovery command:

   ```sh
   python3 -m unittest discover -s tests -v
   ```

5. **Evidence boundary.** End `debug-record.md` with a narrow statement of what
   the passing tests establish and at least three limits. Tests of listed inputs
   do not prove the absence of every defect, validate Python itself, or establish
   correctness for a later C, Rust, or Orange translation.

## Completion criteria

Use the [rubric](rubric.md). A passing submission earns at least 80/100 and
satisfies every critical criterion. It must include:

- an annotated, explicit, and consistently enforced contract for
  **PRG-103-01**;
- a genuinely failing focused test before repair, systematic diagnosis, the
  same test passing after repair, and a green full suite for **PRG-103-02**;
- distinct immutable success and failure variants that reject every named
  invalid case without a partial result while preserving bounded diagnostic
  context for **PRG-103-03**; and
- reproducible test commands, outputs, and statuses with no external package,
  network, elevated, destructive, or unrelated-data-disclosure behavior.

A final passing suite without preserved pre-repair failure evidence does not
demonstrate the debugging outcome.
