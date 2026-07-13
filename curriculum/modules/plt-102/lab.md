# Lab: define and execute Glimmer semantics

## Goal

Specify, implement, and test the static and dynamic semantics of a new bounded
expression language. The result must make lexical scope, type rejection,
potential effects, evaluation order, actual effects, resource failures, and
unsupported claims independently auditable.

## Setup

From the repository root, inspect and run the Lumen model:

~~~sh
cd curriculum/modules/plt-102
python3 --version
PYTHONDONTWRITEBYTECODE=1 python3 -B examples/semantics_worked.py
PYTHONDONTWRITEBYTECODE=1 python3 -B checks/lab_smoke.py
~~~

The final command must print <code>plt-102 lab smoke: PASS</code> and exit zero.
Use Python 3.11 or newer and only the standard library.

Create a fresh temporary workspace for learner work:

~~~sh
workdir="$(mktemp -d)"
cd -- "$workdir"
pwd
~~~

Use <code>PYTHONDONTWRITEBYTECODE=1</code> and <code>python3 -B</code> for every
run. Do not import, copy, rename, or mechanically translate the Lumen model.
Glimmer has a distinct contract. No network access, external package,
administrator permission, or repository write is required.

## Tasks

1. **Define Glimmer's AST and values — PLT-102-01.** Use frozen records for
   unsigned integer literals, Boolean literals, variables, multiplication,
   less-than, <code>choose</code>, lexical <code>bind</code>,
   <code>record</code>, and <code>after</code>. Values are integers 0–65,535,
   Booleans, and unit. Names are 1–20 lowercase ASCII bytes matching
   <code>[a-z][a-z0-9_]*</code>. Reject unsupported host objects and cyclic ASTs.
2. **Specify scope — PLT-102-01.** Use lexical nearest-binding resolution.
   State how <code>bind x = a in b</code> handles uses of <code>x</code> in
   <code>a</code> and <code>b</code>. Demonstrate nested shadowing and two
   alpha-equivalent programs. Bound active environments at 20 entries.
3. **Write type-and-effect rules — PLT-102-02.** Use types
   <code>Nat16</code>, <code>Bool</code>, and <code>Unit</code>, plus potential
   effect <code>record</code>. Multiplication takes two
   <code>Nat16</code> operands. Less-than takes two <code>Nat16</code> operands
   and returns <code>Bool</code>. <code>choose</code> requires a Boolean condition
   and equal branch types. <code>record</code> accepts <code>Nat16</code> and
   returns <code>Unit</code>. <code>after</code> requires a <code>Unit</code> first
   expression and returns its second expression's type. Join potential effects
   from every checked child, including both branches.
4. **Implement the checker — PLT-102-02.** Visit at most 192 nodes, follow an
   AST path at most 24 nodes deep, and reject a cap before another visit,
   recursion, or environment extension. Return an immutable judgment containing
   type, potential effects, and visited-node count. Give stable codes for every
   static rejection.
5. **Define evaluation — PLT-102-03.** Use deterministic strict call-by-value
   evaluation, left-to-right child order, nearest-binding lookup, and exactly
   one selected <code>choose</code> branch. <code>record e</code> appends the
   evaluated unsigned integer to an ordered log and returns unit. Check
   multiplication against 0–65,535 instead of inheriting Python's integer
   behavior. Evaluate only after successful type checking.
6. **Bound runtime behavior — PLT-102-03.** Charge one step on entry to each
   evaluated node. Accept explicit integer budgets of 1–192 steps and 1–48 log
   entries; reject Booleans as budgets. Check before consuming the next step or
   retaining the next entry. Use stable runtime codes for multiplication
   overflow, step exhaustion, log exhaustion, and invalid budgets.
7. **Test names and typing — PLT-102-04.** Cover each expression form, free
   names, the name grammar endpoints, nearest-binding shadowing, alpha-renaming,
   wrong operand types, branch mismatch, invalid sequencing, effect-free
   expressions, and conservative effects from an untaken branch. Assert the
   exact type, effect set, static code, and stable message as applicable.
8. **Test dynamics and endpoints — PLT-102-04.** Cover left-to-right logs,
   exactly one selected branch, integer endpoints, multiplication overflow,
   exact and one-beyond AST visits, depth, active bindings, steps, and log
   entries. Construct node and depth endpoints separately so one does not mask
   the other. Include an unsupported node and a deliberately created host-side
   cycle.
9. **Add independent relational evidence — PLT-102-04.** For at least 30 fixed
   pure closed Glimmer ASTs, compare results with a separately written
   mathematical evaluator that does not call the production checker or
   evaluator. Show alpha-renaming preserves all observations. Show inserting an
   unused pure binding preserves observations. Show changing an untaken branch
   to another same-typed expression can change potential effects without
   changing actual output or result. State the exact overlap and the limits of
   each relation.
10. **Prove failure sensitivity — PLT-102-04.** Mutate four expectations one at
    a time: a shadowing result, one operand-type code, left-to-right log order,
    and the exact node-visit endpoint. Preserve stdout, stderr, and immediate
    nonzero status for each mutation. Restore each expectation and preserve its
    zero status.
11. **Record evidence and non-claims.** In <code>evidence.md</code>, record the
    Python version, absolute temporary path, hashes, exact commands, separate
    stdout/stderr, and immediate statuses. Justify checker O(n) time over at
    most 192 visits and evaluator O(k) time over at most 192 steps. Bound model
    collections but do not claim exact Python memory. State that Glimmer is
    independent courseware and establishes no Orange scope, type, effect,
    evaluation, compilation, safety, security, or conformance property.

## Verification

Run the learner test suite from the temporary workspace:

~~~sh
PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest -v \
  >passing.stdout 2>passing.stderr
status=$?
printf 'test status: %s\n' "$status"
~~~

Status zero is necessary but not sufficient. Inspect the implementation and
evidence and verify that:

- every AST form has an explicit scope, type, effect, and evaluation rule;
- type checking examines both branches while evaluation selects exactly one;
- environment lookup realizes the documented nearest-binding rule;
- visit, depth, environment, step, log, name, and integer bounds are checked at
  their declared boundary;
- host Booleans are not silently accepted as integers or budgets;
- static failures prevent evaluation and dynamic failures have distinct codes;
- the independent evaluator shares no production checking or evaluation path;
- all four deliberate mutations fail observably and restored cases pass;
- generated files remain under the temporary workspace; and
- claims distinguish finite executable evidence from a general proof.

Finally rerun the repository smoke as separate evidence that the supplied model
did not change:

~~~sh
cd /absolute/path/to/orange-school/curriculum/modules/plt-102
PYTHONDONTWRITEBYTECODE=1 python3 -B checks/lab_smoke.py
~~~

## Reflection

Write six to eight sentences answering:

- Which occurrence in your shadowing case resolves outside the inner binding?
- Why is potential effect information not the same as an actual log?
- Which rule prevents a conditional's result type from depending on its branch?
- What observation would change if evaluation order changed?
- Which exact endpoint was hardest to isolate from another cap?
- What fault can the independent oracle detect that examples alone might miss?
- Why are your tests not a type-soundness proof?
- Which professionally useful Orange claim remains unsupported?
