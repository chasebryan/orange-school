# Programming from first principles

A program is a precise process: it receives input, changes state according to
written rules, and produces output. This module uses Python so you can see those
ideas without first managing a large toolchain. The concepts transfer to later
languages, including Orange when its executable surface exists.

## Learning objectives

- **PRG-101-01:** Trace expressions, variables, functions, and control flow and
  predict the next program state.
- **PRG-101-02:** Write and run a Python program with explicit input, output,
  and state.
- **PRG-101-03:** Decompose a problem into functions and test normal, boundary,
  and invalid cases.

## Prerequisites

Pass <code>cmp-101</code>. You should be able to open a terminal, identify the
working directory, run a bounded command, and record stdout, stderr, and exit
status. No prior programming is assumed.

Check the interpreter before starting:

~~~sh
python3 --version
~~~

The module examples use only the Python standard library and work with Python
3.11 or newer. If the command is missing or reports an older version, stop and
record the environment blocker.

## Lesson

**Source and execution.** Python source is plain text saved in a
<code>.py</code> file. Running <code>python3 program.py</code> asks the
interpreter to execute statements from top to bottom. Python distinguishes
uppercase from lowercase and uses indentation to group statements.

This program has a literal value, an expression, a variable, and output:

~~~python
price_cents = 250
quantity = 3
total_cents = price_cents * quantity
print(total_cents)
~~~

<code>250</code> and <code>3</code> are integer values. Multiplication is an
expression that produces another value. Assignment with <code>=</code> binds a
name to a value. A variable's current binding is part of program **state**.
<code>print</code> sends text to stdout.

Trace code one statement at a time. After each assignment, record every name
whose value changed:

| Step | Statement | <code>price_cents</code> | <code>quantity</code> | <code>total_cents</code> | Output |
| ---: | --- | ---: | ---: | ---: | --- |
| 1 | <code>price_cents = 250</code> | 250 | not bound | not bound | none |
| 2 | <code>quantity = 3</code> | 250 | 3 | not bound | none |
| 3 | multiplication and assignment | 250 | 3 | 750 | none |
| 4 | <code>print(total_cents)</code> | 250 | 3 | 750 | <code>750</code> |

“Not bound” is different from zero. Using a name before it is bound is an
error.

Python strings put text in quotes, such as <code>"small"</code>. A list puts a
sequence of values in square brackets, such as <code>[8, 10, 12]</code>.
<code>len(values)</code> returns its item count, and
<code>values.append(item)</code> adds one item to that list. A function call
uses parentheses; the dot in <code>values.append</code> selects an operation
provided by that value.

**Functions name one job.** A function receives parameters, performs a small
process, and may return a value:

~~~python
def total_cost(unit_cents, quantity):
    return unit_cents * quantity


bill = total_cost(250, 3)
~~~

When the call begins, <code>unit_cents</code> is 250 and
<code>quantity</code> is 3 inside the function. <code>return</code> sends 750
back to the caller, which assigns it to <code>bill</code>. Prefer functions
whose names and parameters expose their purpose. A main function can coordinate
input and output while smaller functions implement rules.

**Control flow chooses or repeats statements.** A Boolean value is
<code>True</code> or <code>False</code>. Comparisons such as
<code>quantity &gt; 0</code> produce Booleans.

~~~python
if bill == 0:
    label = "free"
elif bill < 1_000:
    label = "small"
else:
    label = "large"
~~~

Exactly one branch runs. Test boundary values at the points where a comparison
changes outcome: here, 0, 1, 999, and 1,000 are revealing cases.

A loop repeats its body:

~~~python
total = 0
for pages in [8, 10, 12]:
    total = total + pages
~~~

The loop variable <code>pages</code> takes the next list value on each
iteration. The state of <code>total</code> is 0, then 8, then 18, then 30.
That sequence is a loop trace. State that changes each iteration is often
called an accumulator.

A function can return two values separated by a comma. Python packages them as
a fixed pair called a tuple; the caller can bind both at once:

~~~python
total, count = analyze_readings(10, [8, 10, 12])
~~~

**Make input and output explicit.** The module examples read command-line text
from <code>sys.argv</code>. For this command:

~~~sh
python3 examples/temperature_advice.py 20
~~~

the script name is followed by the text <code>"20"</code>. The program converts
that text with <code>int</code>, validates its supported range, and prints a
classification. Valid results go to stdout. Usage and validation diagnostics
go to stderr, and invalid input produces a nonzero exit status.

All command-line input begins as text. Conversion can fail, so handle
<code>ValueError</code> at the input boundary:

~~~python
try:
    value = int(text)
except ValueError:
    print("error: value must be an integer", file=sys.stderr)
    return 2
~~~

Do not catch every possible error merely to hide it. Handle invalid user input
you understand; let unexpected programmer errors remain visible during
development.

<code>import sys</code> makes Python's standard <code>sys</code> module
available. A conventional command-line entry point keeps coordination explicit:

~~~python
def main(arguments):
    # convert, validate, calculate, and print
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
~~~

<code>sys.argv[1:]</code> is the list of arguments after the script name.
<code>main</code> returns the desired exit status, and
<code>SystemExit</code> gives it to the shell. The name check prevents
command-line work from running when a test loads the file to call one function.

**Decompose before coding.** Turn a problem statement into contracts:

1. List exact inputs, their types, and allowed ranges.
2. List exact outputs and which stream receives each one.
3. Name the state that changes.
4. Give each independent rule a function with clear parameters and result.
5. Define invalid input behavior and exit status.
6. Write tests before trusting the result.

Use at least three test classes:

- A **normal case** represents common valid use.
- A **boundary case** sits at or beside a minimum, maximum, empty/nonempty
  transition, or branch threshold.
- An **invalid case** violates the stated input contract and must fail in the
  stated way.

A test is evidence for the exact cases run. It is not proof that every input is
correct.

## Worked example

Trace this function for <code>goal = 10</code> and
<code>readings = [8, 10, 12]</code>:

~~~python
def analyze(goal, readings):
    total = 0
    met = 0
    for pages in readings:
        total = total + pages
        if pages >= goal:
            met = met + 1
    return total, met
~~~

| Iteration | <code>pages</code> | <code>total</code> after assignment | Comparison | <code>met</code> |
| ---: | ---: | ---: | --- | ---: |
| start | not bound | 0 | not evaluated | 0 |
| 1 | 8 | 8 | <code>8 &gt;= 10</code> is false | 0 |
| 2 | 10 | 18 | <code>10 &gt;= 10</code> is true | 1 |
| 3 | 12 | 30 | <code>12 &gt;= 10</code> is true | 2 |

The function returns 30 and 2. A normal test uses these three readings. A
boundary test could use a reading exactly equal to the goal. Invalid tests
belong at the validation boundary, such as a non-integer goal, no readings, or
a negative reading.

The complete [reading-goal example](examples/reading_goal.py) separates parsing,
analysis, formatting, and command-line coordination. The
[temperature example](examples/temperature_advice.py) provides a smaller branch
trace.

## Check your understanding

1. In <code>count = count + 1</code>, which side is evaluated first, and what
   state changes?
2. What is the final value of <code>total</code> after looping over
   <code>[2, 0, 5]</code> and adding each value?
3. Why should parsing command-line text and calculating a result be separate
   functions?
4. For a supported range from 1 through 10, name one normal, two boundary, and
   two invalid values.
5. What is wrong with claiming “the program is correct” after one test passes?

**Answers:** (1) the right side reads the old value, adds one, then assignment
changes <code>count</code>; (2) 7; (3) separation makes each rule easier to
trace, reuse, and test without starting a subprocess; (4) for example normal 5,
boundaries 1 and 10, invalid 0 and 11; (5) the observation covers only the
tested environment and input.

## Next step

Complete the [lab](lab.md), including its normal, boundary, and invalid runs.
Keep your command and result record. Then complete the
[independent assessment](assessment.md). Passing requires at least 80/100 and
every critical criterion in the [rubric](rubric.md).

## Sources

- Python Software Foundation, [The Python Tutorial, Python
  3.11](https://docs.python.org/3.11/tutorial/), sections 3 through 5 and 8,
  for values, control flow, functions, data, and errors.
- Python Software Foundation, [Python 3.11 library documentation:
  <code>sys</code>](https://docs.python.org/3.11/library/sys.html), command-line
  arguments, stdout, stderr, and exit status.
- [Assessment system](../../../docs/assessment-system.md), independent evidence,
  scoring, and retry rules.
