# Assessment: explicit state and tested decomposition

## Instructions

Complete this assessment independently in a fresh temporary directory using
Python 3.11 or newer and only the standard library. Submit source, tests, a
command/result record, and the trace requested below. Do not copy or rename the
module examples.

This assessment covers:

- **PRG-101-01:** Trace expressions, variables, functions, and control flow and
  predict the next program state.
- **PRG-101-02:** Write and run a Python program with explicit input, output,
  and state.
- **PRG-101-03:** Decompose a problem into functions and test normal, boundary,
  and invalid cases.

## Knowledge check

1. Trace this code with one row per executed statement. Record
   <code>change</code>, <code>stock</code>, and output:

   ~~~python
   stock = 3
   for change in [2, -1, 0]:
       stock = stock + change
       if stock == 0:
           print("empty")
       elif stock < 3:
           print("low")
       else:
           print("ready")
   ~~~

2. Explain assignment, function parameter, return value, and Boolean branch in
   your own words.
3. Explain why command-line input must be converted and validated before it
   changes program state.
4. Distinguish a normal, boundary, and invalid test, and state the evidence
   limit of three passing tests.

## Independent task

Create <code>stock_report.py</code> with this exact interface:

~~~text
python3 stock_report.py CAPACITY START CHANGE [CHANGE ...]
~~~

1. **Trace — PRG-101-01.** Before running your program, trace capacity 10,
   start 4, and changes <code>3 -2 5</code>. For every iteration record the
   proposed stock, branch decision, accepted state, lowest state, and highest
   state. Predict stdout and exit status.
2. **Program — PRG-101-02.**
   - Convert all inputs from command-line text to integers.
   - Accept capacity from 1 through 10,000, start from 0 through capacity, and
     from 1 through 20 changes. Each change must be from -10,000 through
     10,000.
   - Begin mutable stock state at <code>START</code>. Apply changes in order.
     Initialize lowest and highest stock from <code>START</code>, then update
     them after each accepted change.
     A change that would put stock below zero or above capacity is invalid:
     print a precise diagnostic to stderr, print no report to stdout, and exit
     nonzero without accepting that state.
   - On success, print exactly four labeled values to stdout: number of accepted
     changes, final stock, lowest stock, and highest stock. Exit 0.
3. **Decomposition and tests — PRG-101-03.** Separate conversion, input
   validation, state transition, report formatting, and command-line
   coordination into functions with explicit parameters and results. Use
   <code>unittest</code> or simple assertions in a separate
   <code>test_stock_report.py</code>. Include:
   - at least two normal cases;
   - boundary cases for empty/full stock, an exact-capacity transition, and the
     maximum accepted change count;
   - invalid cases for non-integer text, invalid capacity, invalid start, no
     changes, too many changes, an out-of-range change, underflow, and
     overflow; and
   - at least one command-level test that checks stdout, stderr, and status.
4. Run the tests from the submitted directory. Record Python version, absolute
   working directory, exact commands, stdout, stderr, statuses, and a statement
   of what the tests do not establish.

## Completion criteria

Use [the rubric](rubric.md). Passing requires at least 80/100 and every critical
criterion. The submission must:

- produce a correct statement-by-statement trace for **PRG-101-01**;
- implement explicit, bounded input, output, and state transitions for
  **PRG-101-02**;
- use purposeful functions and passing normal, boundary, and invalid tests for
  **PRG-101-03**;
- fail without a success report when an input or transition is invalid; and
- include runnable standard-library-only evidence with no network access.
