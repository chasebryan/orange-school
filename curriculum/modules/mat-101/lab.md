# Lab: a proof and finite-evidence dossier

## Goal

Translate precise integer statements, classify implication truth cases, produce
counterexamples, write one argument with each required proof technique, and
compare those arguments with bounded Python checks whose assumptions and scope
remain explicit.

## Setup

From the repository root, verify the course example:

```sh
cd curriculum/modules/mat-101
python3 checks/lab_smoke.py
smoke_status=$?
printf 'MAT-101 smoke status: %s\n' "$smoke_status"
```

Stop and inspect the named failing test if the status is nonzero. Otherwise make
a temporary working copy:

```sh
module_dir="$PWD"
workdir="$(mktemp -d)"
printf 'MAT-101 workspace: %s\n' "$workdir"
cp -R "$module_dir/example" "$workdir/example"
cd "$workdir"
touch logic-dossier.md experiment-record.md
```

All writes stay inside the printed directory. Use Python 3.11 or newer and the
standard library only. No network or administrator access is needed.

In your dossier, define `even`, `odd`, and `a divides b` before using them. State
that all variables in Tasks 1 through 4 range over the integers unless another
domain is named.

## Tasks

1. **Translate and negate — MAT-101-01.** For each statement, write:

   - precise prose with its domain;
   - a predicate-and-quantifier form;
   - its logical negation with negation moved through the quantifier; and
   - whether it is true or false, with a witness or counterexample when one is
     available.

   Statements:

   1. Every integer divisible by 6 is divisible by 3.
   2. Some integer has square 25.
   3. No integer is both even and odd.
   4. Every even integer is divisible by 4.
   5. For every integer `x`, there exists an integer `y` with `y > x`.

   For statements 1 and 4, also write the converse, inverse, and contrapositive.
   Do not assume that these forms share a truth value merely because their words
   are similar.

2. **Build implication truth cases — MAT-101-01.** Draw the four-row truth table
   for `P -> Q`. For each row, say whether a case with those values supports or
   refutes the universal implication. Explain why a false antecedent does not
   establish the consequent.

3. **Construct four arguments — MAT-101-02.** Label the method, assumptions,
   arbitrary variables, justified steps, and conclusion for each:

   - **Direct:** the sum of two even integers is even.
   - **Contrapositive:** if the square of an integer is even, the integer is even.
   - **Contradiction:** no integer is both even and odd.
   - **Induction:** for every integer `n >= 0`, the sum of the first `n` odd
     positive integers is `n^2`.

   The induction argument must include the empty-sum base case, an induction
   hypothesis for an arbitrary `k >= 0`, the identity of the next odd number,
   and the step to `k+1`.

4. **Run bounded checks — MAT-101-03.** Create `experiment.py` with this supplied
   structure:

   ```python
   from example.logic_scope import check_integer_claim, implies, triangular_sum

   true_on_range = check_integer_claim(
       -100,
       100,
       lambda n: implies(n % 6 == 0, n % 3 == 0),
   )
   false_claim = check_integer_claim(
       -100,
       100,
       lambda n: implies(n % 2 == 0, n % 4 == 0),
   )
   formula_cases = check_integer_claim(
       0,
       100,
       lambda n: triangular_sum(n) == n * (n + 1) // 2,
   )

   print(true_on_range)
   print(false_claim)
   print(formula_cases)
   ```

   Run it and preserve the exact command, interpreter version, stdout, stderr,
   and exit status in `experiment-record.md`. For each result, state:

   - requested and actually checked range;
   - whether a counterexample was found;
   - the narrow conclusion the run supports;
   - which universal claim, if any, a counterexample refutes; and
   - why a passing finite result does not replace the corresponding unbounded
     proof.

5. **Inventory assumptions and limits — MAT-101-03.** End the dossier with two
   separate inventories. For the induction proof, list definitions, domain,
   arithmetic facts, base case, and induction principle. For the Python run,
   list source file, interpreter, exact inputs, finite bound, predicate encoding,
   execution result, and the assumption that the implementation behaved as
   observed. Give at least three limits for each evidence form.

## Verification

Run the supplied unit suite from the workspace root:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s example/tests -v
suite_status=$?
printf 'example suite status: %s\n' "$suite_status"
test "$suite_status" -eq 0
```

Then use this checklist:

- `logic-dossier.md` contains all five translations, negations, truth decisions,
  and required converse/inverse/contrapositive forms.
- A concrete counterexample refutes Statement 4.
- The implication table has exactly one false row: true antecedent and false
  consequent.
- All four proof methods have complete, correctly scoped arguments.
- The induction proof uses an arbitrary `k`, not a list of examples.
- `experiment-record.md` preserves all three command-result channels and the
  exact finite ranges.
- Passing computation is never described as proof over all integers.
- Assumptions and limits are separate for the proof and program run.

If any item is absent, correct the specific section and retain the earlier
observation as part of the record.

## Reflection

Answer at the end of `logic-dossier.md`:

1. Which translation error was easiest to make: domain, quantifier, implication,
   or negation? How did you detect it?
2. Why can one counterexample do more logical work than one million passing
   samples against a universal claim?
3. Which step makes the induction argument cover an unbounded range?
4. How do the assumptions of a mathematical proof differ from the assumptions
   of a Python execution?
5. What claim can the finite checker report honestly without using the word
   “proved”?
