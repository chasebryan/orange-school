# Assessment: independent Slate static and dynamic semantics

## Instructions

Complete this assessment independently in a fresh temporary directory with
Python 3.11 or newer and only the standard library. Do not copy, import, rename,
or lightly translate Lumen or a Glimmer solution. Slate has different nodes,
types, bounds, value rules, and effects.

Submit the language specification, immutable AST and results, checker,
evaluator, tests, independent oracle, deliberate-failure records, resource
argument, source hashes, exact commands, stdout, stderr, and immediate statuses.
All generated artifacts must remain beneath the temporary directory. The work
must run offline without external packages or privileged operations.

## Knowledge check

Answer before writing code:

1. Distinguish an identifier spelling, binding occurrence, variable use, free
   name, bound name, scope, shadowing, and alpha-renaming.
2. For <code>bind x = 3 in bind x = x + 1 in x</code>, identify the binding for
   both uses and state the result.
3. Read <code>Gamma |- e : T ! epsilon</code> aloud and explain why a
   conditional joins effects from both branches.
4. Distinguish static rejection, a modeled runtime failure, a host exception,
   and divergence.
5. Explain why left-to-right evaluation is observable when expressions can
   append to a trace.
6. Give a progress or bound invariant for AST checking and one for evaluation.
7. Contrast an example, endpoint, relational property, independent oracle, and
   deliberate-failure test. Name one limitation of each.
8. Explain why a typechecker and evaluator passing finite tests do not prove
   type soundness, memory safety, security, compiler correctness, or any Orange
   property.

## Independent task

Create <code>slate_semantics.py</code>, <code>test_slate_semantics.py</code>,
<code>specification.md</code>, and <code>evidence.md</code>.

1. **AST, names, and scope — PLT-102-01.** Define frozen nodes for signed
   integer and Boolean literals, variables, integer negation, integer addition,
   Boolean conjunction, integer equality, conditional, lexical
   <code>with</code>, <code>note</code>, and <code>then</code>. Names must match
   <code>[A-Z][A-Z0-9]{0,15}</code> in ASCII. Use lexical nearest-binding scope;
   a binder is not in scope in its own bound expression. Reject unsupported
   nodes, bad field values, free names, and cyclic host ASTs with stable codes.
2. **Static semantics — PLT-102-02.** Use types <code>I32</code>,
   <code>Truth</code>, and <code>One</code>, with potential effect
   <code>note</code>. Negation and addition require <code>I32</code>.
   Conjunction requires <code>Truth</code>. Equality takes two
   <code>I32</code> operands and returns <code>Truth</code>. A conditional
   requires <code>Truth</code> and equal branch types. <code>note</code> accepts
   <code>I32</code>, appends that value when executed, and has type
   <code>One</code>. <code>then</code> requires <code>One</code> on the left.
   Define the rules before implementing them and join all child potential
   effects, including both conditional branches.
3. **Checker bounds — PLT-102-02.** Limit visits to 320 nodes, path depth to 28,
   and active bindings to 24. Check each limit before the next visit, recursive
   descent, or environment retention. Return an immutable type/effect judgment
   plus exact visit count. A repeated shared subtree counts each visit; an
   active recursion identity indicates a cycle.
4. **Dynamic semantics — PLT-102-03.** Evaluate closed, successfully checked
   expressions under strict call-by-value, left-to-right rules. Evaluate only
   the selected conditional branch. Preserve lexical shadowing with immutable
   environments. Use the exact signed interval -2,147,483,648 through
   2,147,483,647 for literals and results; reject host Booleans as integers.
   Do not inherit Python's unbounded arithmetic as Slate semantics.
5. **Runtime budgets — PLT-102-03.** Charge one step per evaluated node, with a
   caller-selected exact-integer budget from 1 through 320. Retain at most 40
   noted integers under a caller-selected budget from 1 through 40. Check
   before consumption or append. Specify distinct deterministic codes for
   negation overflow, addition overflow, step exhaustion, note exhaustion, and
   invalid budgets. Do not expose a partial success result after failure.
6. **Static tests — PLT-102-04.** Cover every node and rule; name endpoints and
   one beyond; free names; scope of a bound expression; nested shadowing;
   alpha-equivalence; malformed host fields; every operand/branch mismatch;
   conservative effects from an untaken branch; exact node/depth/environment
   endpoints and one beyond; unsupported nodes; cycles; and stable code/message
   pairs.
7. **Dynamic tests — PLT-102-04.** Cover both conditional choices,
   left-to-right note order, pure evaluation, exact integer endpoints, minimum
   integer negation overflow, addition overflow in both directions, exact step
   and note budgets, one beyond each budget, invalid Boolean/zero/oversized
   budgets, deterministic repeated runs, and absence of a result on failure.
8. **Relational and independent evidence — PLT-102-04.** Implement a separate
   evaluator for at least 40 fixed pure closed cases over literals, negation,
   addition, conjunction, equality, and conditionals. It must not call the
   production checker or evaluator. Assert agreement within the declared
   overlap. Test alpha-renaming and unused pure binding insertion. Give a
   same-type untaken-branch pair with equal actual observations but different
   potential effects. State why each relation has preconditions and why finite
   agreement is not proof.
9. **Observed test sensitivity — PLT-102-04.** Mutate five expectations
   independently: inner shadowing, conjunction's required type, potential
   effect of an untaken branch, note order, and minimum-integer negation
   overflow code. Preserve targeted nonzero statuses and diagnostic channels,
   then restore each expectation and preserve targeted status zero.
10. **Reproducibility and claims.** Record Python version, absolute workspace,
    file hashes, exact commands, stdout, stderr, and immediate statuses. Justify
    O(n) checking for at most 320 visits and O(k) evaluation for at most 320
    steps; bound retained model collections and exclude Python object/allocator
    overhead from exact claims. State that Slate is independent courseware.
    This assessment establishes no parsing, termination, type-soundness theorem,
    concurrency, compiler, memory-safety, security, compatibility, conformance,
    or Orange claim.

## Completion criteria

Use the [rubric](rubric.md). Passing requires at least 80/100 and every critical
criterion. A complete submission must:

- specify and implement bounded lexical scope, binding, shadowing, and stable
  rejection for **PLT-102-01**;
- derive and implement the exact Slate type-and-effect rules for
  **PLT-102-02**;
- implement deterministic bounded evaluation, ordering, actual effects,
  integer behavior, and runtime failures for **PLT-102-03**;
- provide endpoint, invalid, relational, independent, and observed
  deliberate-failure evidence for **PLT-102-04**;
- preserve commands, channels, hashes, immediate statuses, and bound arguments;
  and
- make no Orange or general theorem claim beyond the submitted evidence.
