# Types, errors, tests, and systematic debugging

Reliable software makes its boundary visible. A caller should be able to tell
which inputs are accepted, which result forms can be returned, and why a request
was rejected. A maintainer should be able to reproduce a failure with one small
test before changing the program.

This module uses Python 3.11 or newer and only the standard library. The habits
transfer to later C, Rust, and Orange work even though their type systems and
error models differ.

## Learning objectives

- **PRG-103-01:** Use type annotations and explicit invariants to define accepted
  inputs and outputs.
- **PRG-103-02:** Turn a reproduced failure into a focused unit test and diagnose
  it systematically.
- **PRG-103-03:** Design explicit error results that fail closed without hiding
  context.

## Prerequisites

Pass `prg-101` and `cmp-103`. You should be able to write a Python function with
conditionals, run a Python file, use Git to inspect changes, and capture a failed
test's output and exit status. `prg-102` is not required; this module uses only
small records, straight-line validation, and bounded test cases.

Verify the interpreter before continuing:

```sh
python3 --version
```

Use Python 3.11 or newer. Every command in this module reads local files or
writes only inside a learner-created working copy. No command requires network
access, administrator privileges, or external packages.

## Lesson

### An annotation is a contract statement, not a runtime guard

Consider this signature:

```python
def calculate_quote(quantity_text: str, unit_price_cents_text: str) -> QuoteResult:
    ...
```

It tells readers and analysis tools that both inputs are text and that the
function returns one of the variants represented by `QuoteResult`. Python does
not automatically reject a caller that passes an integer. A boundary function
must still validate runtime input when an unchecked caller can reach it.

A useful contract names more than broad types. It also states **invariants**:
conditions that must be true for every accepted value or produced result. The
quote example uses these invariants:

- `quantity_text` contains one or more ASCII decimal digits and represents an
  integer from 1 through 100;
- `unit_price_cents_text` contains one or more ASCII decimal digits and
  represents an integer from 0 through 1,000,000;
- a successful result has `total_cents == quantity * unit_price_cents`; and
- a failed result contains one error and no computed total.

These rules answer boundary questions that `str` and `int` alone cannot answer.
Write them near the public function and encode important output invariants in
constructors and tests.

### Accepted input should not grow by accident

Python's `str.isdigit()` accepts more than ASCII `0` through `9`. That behavior
is useful for some international text, but it is too broad when a file format or
protocol explicitly requires ASCII decimal text. This predicate records the
narrower policy:

```python
text.isascii() and text.isdecimal()
```

The empty string is rejected because `isdecimal()` is false for empty text.
Whitespace, signs, separators, and non-ASCII decimal characters are also
rejected. The point is not that ASCII is universally preferable. The point is
that implementation and tests should match the stated boundary exactly.

### Make success and failure different result variants

Returning `None` for every problem hides which field failed and why. Raising an
uncaught conversion exception exposes an implementation detail and may skip the
caller's normal failure path. Silently replacing bad input with zero is worse:
it converts a rejected request into a plausible result.

The example instead uses two immutable data classes:

```python
@dataclass(frozen=True)
class QuoteSuccess:
    quantity: int
    unit_price_cents: int
    total_cents: int

@dataclass(frozen=True)
class QuoteFailure:
    error: InputError

QuoteResult = QuoteSuccess | QuoteFailure
```

This design **fails closed**: invalid input returns `QuoteFailure`, and that
variant has no `total_cents` attribute that a caller could mistake for an
approved quote. The nested `InputError` preserves a stable code, the rejected
field, bounded representation of the received value, and an explanatory
message.

Context must also have a boundary. Do not place secrets, credentials, or
unbounded hostile text into diagnostics. The example uses `repr` to make spaces
and control characters visible, includes the runtime type, and truncates the
rendering to 80 characters. This preserves useful local context without turning
the diagnostic into a second uncontrolled output channel.

### Diagnose before repairing

A systematic debugging loop is small and evidence-driven:

1. **Reproduce** the observed failure with exact input, command, output, and exit
   status.
2. **Minimize** the reproduction so one behavior fails for one reason.
3. **Protect** it with a focused unit test that fails before the repair.
4. **Form a hypothesis** about the violated invariant.
5. **Run one discriminating experiment**, such as comparing `isascii()`,
   `isdecimal()`, and `isdigit()` on the exact input.
6. **Change one boundary**, then run the focused test.
7. **Run the complete suite** to detect collateral regressions.
8. **Record the conclusion and limits**; a passing test covers its stated cases,
   not every possible input.

Avoid changing code before reproducing the failure. A change that merely makes
the symptom disappear can widen another input boundary or destroy the evidence
needed to understand the defect.

### Focused tests are executable claims

The standard-library `unittest` module groups setup, action, and observations:

```python
def test_rejects_non_ascii_decimal_digits(self) -> None:
    result = calculate_quote("\u0661", "250")

    self.assertIsInstance(result, QuoteFailure)
    self.assertEqual(result.error.code, "not_ascii_decimal")
    self.assertEqual(result.error.field, "quantity")
```

This test is focused because one input exercises one invariant and the
assertions check the exact public result. It would be weaker to assert only that
“an error happened.” It would be brittle to assert a traceback line number or a
private helper's local variable.

Test normal cases, both range boundaries, one representative case for each
rejection class, and the structure of failure results. A table with
`subTest(...)` is useful when several inputs exercise the same rule; separate
test methods are clearer when failures have different causes.

## Worked example

From the repository root, inspect and check the provided package:

```sh
cd curriculum/modules/prg-103
python3 checks/lab_smoke.py
python3 -m unittest discover -s example/tests -v
```

Both commands should exit with status 0. `lab_smoke.py` checks the annotated
boundary, success invariant, structured failure, and the Unicode-digit
regression. `unittest` runs the broader boundary suite.

Now reproduce the reason a naïve check is insufficient without changing the
provided package:

```sh
python3 - <<'PY'
text = "\u0661"
print("isascii:", text.isascii())
print("isdecimal:", text.isdecimal())
print("isdigit:", text.isdigit())
raise SystemExit(0 if text.isascii() and text.isdecimal() else 1)
PY
status=$?
printf 'reproduction status: %s\n' "$status"
```

The exact character is an Arabic-Indic digit one. `isdecimal()` and `isdigit()`
recognize it as a numeric character, while `isascii()` is false. The deliberate
nonzero status records that it is outside this example's accepted ASCII
boundary; it does not claim that the character is invalid in every application.

Open `example/reliable_quote/quote.py` and follow the invalid quantity path. It
returns before parsing the price or calculating a total. Then open
`example/tests/test_quote.py` and connect each assertion in
`test_rejects_non_ascii_decimal_digits` to a documented invariant.

## Check your understanding

1. Why does `quantity_text: str` not by itself reject an integer at runtime?
2. Name the four pieces of context carried by `InputError`.
3. Why is `return QuoteSuccess(total_cents=0)` unsafe for malformed price text?
4. What must you observe before changing code during a debugging investigation?
5. Why should the focused regression test run again as part of the full suite?
6. Does rejecting `"\u0661"` prove that all invalid quote inputs are rejected?

**Answers:** (1) Python annotations are not automatic runtime enforcement; (2)
stable code, field, bounded received value, and message; (3) it hides rejection
as a plausible approved value; (4) the exact failure with reproducible input,
command, output, and status; (5) to keep the repaired case protected while
checking for collateral failures; (6) no, it supplies evidence for one named
class and the surrounding tests cover additional stated cases.

## Next step

Complete the [lab](lab.md) in a temporary working copy, then complete the
[independent assessment](assessment.md). Passing requires at least 80/100 and
every critical criterion in the [rubric](rubric.md).

Later modules apply the same habits to C, Rust, Orange diagnostics, and
claim-bearing artifacts. The syntax changes; the discipline of explicit
boundaries, reproducible failures, and honest evidence does not.

## Sources

- Python Software Foundation, [typing — Support for type
  hints](https://docs.python.org/3/library/typing.html), annotation and type-hint
  vocabulary.
- Python Software Foundation, [Built-in
  Types](https://docs.python.org/3/library/stdtypes.html), `str.isascii()`,
  `str.isdecimal()`, and `str.isdigit()` behavior.
- Python Software Foundation, [dataclasses — Data
  Classes](https://docs.python.org/3/library/dataclasses.html), generated record
  methods and frozen instances.
- Python Software Foundation, [unittest — Unit testing
  framework](https://docs.python.org/3/library/unittest.html), test cases,
  assertions, discovery, and command exit behavior.
- [Assessment system](../../../docs/assessment-system.md), evidence and module
  pass policy.
