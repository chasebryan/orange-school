# Semantics, names, types, and effects

Parsing establishes that source has a permitted shape. Semantics establishes
what that shape means. A useful language definition makes scope, static
rejection, evaluation order, effects, failures, and resource limits explicit
enough that two readers can derive the same result or find the exact point
where their derivations differ.

This module uses **Lumen**, a deliberately small expression language represented
directly as an immutable abstract syntax tree (AST). Lumen is independent
teaching courseware. It is not Orange syntax, an Orange implementation, or
evidence about Orange behavior.

## Learning objectives

- **PLT-102-01:** Define lexical name resolution, binding, and shadowing over a
  bounded immutable abstract syntax tree.
- **PLT-102-02:** Derive static type-and-effect judgments that reject invalid
  programs before evaluation and conservatively describe potential effects.
- **PLT-102-03:** Specify and execute deterministic call-by-value operational
  semantics with explicit evaluation order, values, effects, and resource
  failures.
- **PLT-102-04:** Test static and dynamic semantics with derivations, endpoints,
  relational cases, independent oracles, and observed deliberate failures while
  keeping claims within the model.

## Prerequisites

Pass <code>plt-101</code> and <code>mat-101</code>. You should be able to read an
AST, distinguish syntax from data derived about syntax, work with predicates
and inference rules, construct a counterexample, and explain why finite tests
are not proofs. The supplied model requires Python 3.11 or newer, uses only the
standard library, runs offline, and writes generated evidence only beneath a
temporary directory.

## Lesson

### Static and dynamic semantics answer different questions

Lumen expressions are integer and Boolean literals, variables, addition,
subtraction, equality, conditionals, lexical <code>let</code> bindings,
<code>emit</code>, and sequencing. Its values are bounded integers, Booleans,
and unit. Its types are <code>Int</code>, <code>Bool</code>, and
<code>Unit</code>. Its only modeled effect is appending one integer to an
ordered output log.

The **static semantics** answers, without running the expression:

1. Is every name bound at its use?
2. Does every operator receive the expected operand types?
3. Do both branches of a conditional have one result type?
4. Which modeled effects could occur on some execution path?

The **dynamic semantics** answers:

1. Which value results for this expression?
2. Which branch is actually selected?
3. Which output values occur, and in what order?
4. Does a defined runtime limit or arithmetic range stop evaluation?

A parser cannot answer those questions merely because it produced an AST. A
typechecker does not establish that evaluation terminates unless the language
and proof cover termination. An evaluator producing a value for one input does
not establish type soundness for every well-typed program.

### Names mean bindings selected by a scope rule

A name is spelling; a binding is the declaration occurrence that supplies its
meaning. Lumen uses lexical scope. In
<code>let x = 1 in let x = 2 in x</code>, the final <code>x</code> resolves to
the nearest enclosing binding and the result is 2. The inner binding
**shadows** the outer one; it does not mutate it.

The model represents an environment as an immutable ordered tuple of
name/value pairs. Extending an environment appends one pair. Lookup searches
from newest to oldest, so the implementation directly realizes nearest-binding
shadowing. A closed expression has no free names. An unbound use produces
stable error <code>S003</code> rather than consulting a Python global, process
environment, current directory, or interactive state.

Names are limited to 1–24 ASCII bytes and match
<code>[A-Za-z_][A-Za-z0-9_]*</code>. The model supports at most 24 active
environment bindings. These are Lumen policy choices, not universal language
rules. A production language also needs decisions about modules, namespaces,
imports, visibility, separate compilation, Unicode, hygiene, and tooling
identities.

### Judgments turn type rules into checkable obligations

Write a typing judgment as:

~~~text
Gamma |- e : T ! epsilon
~~~

Read it as: under type environment <code>Gamma</code>, expression
<code>e</code> has type <code>T</code> and potential effect set
<code>epsilon</code>. For representative Lumen forms:

~~~text
Gamma |- n : Int ! {}

Gamma(x) = T
-----------------
Gamma |- x : T ! {}

Gamma |- a : Int ! ea    Gamma |- b : Int ! eb
-------------------------------------------------
Gamma |- a + b : Int ! (ea union eb)

Gamma |- c : Bool ! ec    Gamma |- t : T ! et    Gamma |- f : T ! ef
------------------------------------------------------------------------
Gamma |- if c then t else f : T ! (ec union et union ef)

Gamma |- e : Int ! ee
----------------------------------
Gamma |- emit e : Unit ! (ee union {emit})
~~~

The rules are syntax-directed: the outer AST node selects the rule, and each
premise recursively checks a child. Addition and subtraction require two
integers. Equality requires two operands of the same <code>Int</code> or
<code>Bool</code> type. A conditional requires a Boolean condition and equal
branch types. Sequencing requires a <code>Unit</code> first expression because
its value is discarded.

Lumen's effect set is **conservative**. Both branches contribute potential
effects even though only one branch runs. Thus
<code>if false then emit 9 else emit 7</code> has potential effect
<code>{emit}</code> and actual output <code>(7)</code>. An empty potential set
means this model found no modeled output effect. It does not imply the host
runtime performs no allocation, scheduling, exception machinery, or other
unmodeled activity.

Type checking visits at most 256 AST nodes, follows paths at most 32 nodes
deep, rejects cycles, and checks a bound before entering a child or retaining a
binding. Repeated references to a shared immutable subtree count as repeated
visits. The bounds keep a hostile or accidentally cyclic host object from
turning the teaching checker into unbounded recursion.

### Operational semantics fixes order and effects

Lumen uses deterministic strict call-by-value evaluation:

- a compound expression evaluates required children from left to right;
- <code>let</code> evaluates its bound expression before extending the
  environment for its body;
- a conditional evaluates its condition, then exactly one branch;
- <code>emit e</code> evaluates <code>e</code>, appends its integer to the log,
  and returns unit; and
- <code>seq a b</code> evaluates <code>a</code> before <code>b</code> and returns
  the value of <code>b</code>.

A big-step judgment can be written:

~~~text
rho ; out ; fuel |- e => value ; out' ; fuel'
~~~

Here <code>rho</code> is the value environment, <code>out</code> is the ordered
output log, and fuel is an observable budget. The executable evaluator charges
one step when entering each evaluated AST node. It allows a caller-selected
budget of 1–256 steps and an output budget of 1–64 entries. It never evaluates
an expression that failed the static checker.

Consider <code>add(a, emit(b))</code>. It is statically invalid because
<code>emit(b)</code> has type <code>Unit</code>, so evaluation order never makes
that malformed addition meaningful. By contrast,
<code>seq(emit(1), emit(2))</code> is well typed and produces output
<code>(1, 2)</code>. Reversing the evaluator's child order would be an
observable semantic change.

### Values, errors, and host behavior need boundaries

Lumen integers occupy the mathematical interval -1,000,000 through 1,000,000.
Literals outside that range are static errors. A well-typed addition or
subtraction can still exceed the range at runtime, producing stable error
<code>R002</code>. The evaluator does not inherit Python's unbounded-integer
behavior as Lumen behavior.

Static errors use <code>S</code> codes and dynamic resource/arithmetic failures
use <code>R</code> codes. Their messages contain no object address, temporary
path, clock, locale-dependent text, or hash iteration. A host Python traceback
is useful during development but is not the language diagnostic contract.

The model guarantees bounds over AST visits, path depth, environment entries,
evaluation steps, outputs, names, and modeled integers. It does not give an
exact byte bound for Python objects or allocator metadata. It also does not
model concurrency, input, exceptions inside the language, file access,
nondeterminism, recursion, polymorphism, subtyping, traits, ownership, or
garbage collection.

### Test the relation between phases

Example tests check named cases. Endpoint tests check each exact cap and one
beyond without crossing a different cap first. Invalid tests establish stable
rejection. Relational tests check laws under declared preconditions:

- renaming a binder and all uses to a fresh name preserves type, effects,
  value, and outputs;
- inserting an unused pure <code>let</code> preserves observations;
- replacing an untaken branch with another expression of the same type can
  change potential effects without changing actual value or output; and
- two alpha-equivalent expressions agree even though their name spellings
  differ.

An independent oracle can evaluate the small closed, pure arithmetic subset
from a separate tree-walking function that does not call Lumen's
<code>run</code>. Agreement across fixed cases is useful evidence about that
overlap. It is not a proof of all Lumen semantics and says nothing about the
effectful forms excluded from the oracle.

A deliberate-failure pair demonstrates test sensitivity. First change an
expected result from 5 to 6 and preserve the nonzero status and assertion.
Then restore 5 and preserve status zero. Similar mutations should target a
shadowed-name result, potential-versus-actual effect distinction, output order,
and resource endpoint. A test suite that remains green after the targeted
expectation is wrong has not supplied the intended evidence.

## Worked example

The supplied [semantics model](examples/semantics.py) constructs this AST:

~~~text
let base = 20 + 1 in
  seq(
    emit(base),
    if false then seq(emit(999), 0) else base + 1
  )
~~~

The typechecker returns <code>Int ! {emit}</code>. The evaluator first binds
<code>base</code> to 21, emits 21, selects only the else branch, and returns 22
after 12 evaluated-node steps. The unselected branch contributes a potential
effect but does not emit 999.

Run it from the repository root:

~~~sh
cd curriculum/modules/plt-102
PYTHONDONTWRITEBYTECODE=1 python3 -B examples/semantics_worked.py
PYTHONDONTWRITEBYTECODE=1 python3 -B checks/lab_smoke.py
~~~

The smoke command must print <code>plt-102 lab smoke: PASS</code> and exit zero.
It also checks static rejection, lexical shadowing, effect joins, evaluation
order, exact and one-beyond limits, cyclic host AST rejection, stable error
codes, and an observed deliberate-failure/restored-pass pair.

## Check your understanding

1. In <code>let x = 1 in let x = x + 1 in x</code>, which binding supplies the
   <code>x</code> in the inner bound expression, and which supplies the final
   use?
2. Why does a typechecker inspect both branches while an evaluator executes
   only one?
3. Give one expression whose potential effect includes <code>emit</code> but
   whose actual output is empty.
4. Why is <code>seq(1, 2)</code> rejected even though an evaluator could discard
   the first value?
5. Distinguish an out-of-range literal, arithmetic overflow, and exhausted
   evaluation fuel in Lumen.
6. Which premise in the conditional typing rule prevents a value from changing
   type depending on the selected branch?
7. What can 30 agreements with an independent arithmetic evaluator establish,
   and what can they not establish?
8. Name two professional language properties that this finite teaching model
   does not establish for Orange.

## Next step

Complete the [Glimmer semantics lab](lab.md), preserving exact commands,
outputs, immediate statuses, and source hashes in a temporary workspace. Then
complete the independent [Slate assessment](assessment.md). The next module
uses these distinctions when lowering typed source constructs into an
intermediate representation and checking which observations are preserved.

## Sources

- Robert Harper, *Practical Foundations for Programming Languages*, second
  edition: abstract syntax, binding, static semantics, and dynamics.
- Benjamin C. Pierce, *Types and Programming Languages*: typed arithmetic,
  operational semantics, safety arguments, and extensions.
- Matthias Felleisen, Robert Bruce Findler, and Matthew Flatt, *Semantics
  Engineering with PLT Redex*: executable semantics and testable language
  models.
- Xavier Leroy, “Formal Verification of a Realistic Compiler”: the distinction
  between testing a model and proving a preservation theorem.

These references supply general methods. Lumen's exact nodes, bounds, effect,
and diagnostics are local course definitions.
