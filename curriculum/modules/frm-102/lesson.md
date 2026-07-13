# Proof assistants, kernels, and trust

A proof assistant can help construct a proof, but the decisive operation is
smaller: a trusted checker replays a proof object against explicit rules and
either accepts a precise judgment or rejects it. Professional use requires
knowing which statements were proved, under which assumptions and axioms, by
which checker, and which larger claims still remain unsupported.

This module's **Pebble kernel** is bounded Python 3.11 teaching courseware. It
is not an Orange component, an implementation of a production proof assistant,
or evidence that its own implementation is sound.

## Learning objectives

- **FRM-102-01:** Distinguish propositions, judgments, assumptions, axioms,
  proof terms, certificates, proof construction, and deterministic replay.
- **FRM-102-02:** Implement and audit a small trusted kernel whose inference
  rules, integrity checks, diagnostics, and resource bounds are explicit.
- **FRM-102-03:** Inventory the trusted computing base and axiom dependencies,
  then calibrate soundness and theorem claims to the actual evidence.
- **FRM-102-04:** Validate proof certificates with rule, endpoint, malformed,
  replay, mutation, deliberate-failure, and recovery evidence.

## Prerequisites

Pass <code>frm-101</code>. You should be able to state preconditions and
postconditions, maintain an invariant, distinguish an example from a universal
claim, and explain why finite tests are not proofs. The supplied checker needs
Python 3.11 or newer and only the standard library. It runs offline and creates
no generated file in the repository.

## Lesson

### Propositions are objects; judgments make claims

Pebble has four proposition forms:

~~~text
P ::= Atom(name) | Bottom | And(P, P) | Imp(P, P)
~~~

An atom is an uninterpreted proposition such as <code>Ready</code>.
<code>Bottom</code> denotes contradiction. <code>And(A,B)</code> is a
conjunction, and <code>Imp(A,B)</code> is implication. These constructors give
syntax. They do not by themselves make any proposition true.

A kernel checks a judgment written:

~~~text
Gamma ; Delta |- p : P
~~~

Read it as: under local assumptions <code>Gamma</code> and trusted axiom
registry <code>Delta</code>, proof object <code>p</code> establishes proposition
<code>P</code>. The colon is a checking relationship between a proof and its
proposition. Acceptance is always relative to the exact rules, context, axiom
registry, and kernel implementation.

An **assumption** is local and discharged by implication introduction. An
**axiom** is admitted without a proof by the kernel configuration. Both affect
the force of a theorem, but they have different scope. A theorem using no
axioms can still depend on its open assumptions. A closed proof has no open
assumptions, yet it may depend on admitted axioms. Record both.

### Proof terms are replayable derivation trees

Pebble uses proof terms whose constructors correspond to inference rules. For
conjunction:

~~~text
Gamma |- p : A      Gamma |- q : B
----------------------------------- AndIntro
        Gamma |- AndIntro(p,q) : A and B

Gamma |- pair : A and B
------------------------ AndElimLeft
Gamma |- AndElimLeft(pair) : A
~~~

There is a symmetric right elimination rule. For implication:

~~~text
Gamma, x:A |- body : B
-------------------------------- ImpIntro
Gamma |- ImpIntro(x,A,body) : A -> B

Gamma |- fn : A -> B      Gamma |- arg : A
------------------------------------------- ImpElim
            Gamma |- ImpElim(fn,arg) : B
~~~

For contradiction:

~~~text
Gamma |- impossible : Bottom
-------------------------------- ExFalso
Gamma |- ExFalso(P, impossible) : P
~~~

<code>Hyp(x)</code> retrieves the proposition bound to active label
<code>x</code>. <code>Axiom(name)</code> retrieves the proposition fixed by the
kernel's axiom registry; the certificate cannot supply or replace that
proposition. Pebble requires active assumption labels to be unique. This is a
small policy that makes lookup and evidence unambiguous, not a universal
requirement of proof assistants.

A tactic, search procedure, language model, or human can construct a candidate
term. None of those producers is trusted merely because it proposed the term.
The kernel replays the complete object. If construction and checking share a
bug, however, replay by the same implementation is not independent assurance.

### The small kernel is the trust bottleneck

The supplied [kernel](examples/proof_kernel.py) recursively infers one
proposition for each proof constructor. It validates explicit formulas, looks
up hypotheses and axioms, checks each premise, compares formulas structurally,
and returns an immutable theorem record containing the conclusion, open
assumptions, sorted used-axiom names, and proof-node count.

The kernel accepts at most:

- 255 visited proof nodes;
- proof depth 40;
- 255 visited nodes in each explicit or resulting formula;
- explicit formula depth 64;
- 32 simultaneously active assumptions; and
- 16 configured axioms.

Names are 1–32 ASCII characters matching
<code>[A-Za-z][A-Za-z0-9_]*</code>. Checks occur before the next visit,
descent, context extension, or registry retention. Repeated subobjects count as
repeated visits. An object identity already on the active recursion path is a
cycle and is rejected. Frozen records prevent ordinary mutation, while cycle
checks also handle hostile host objects created by bypassing that protection.

The proof-node cap bounds recursive proof work. Each explicit or resulting
formula is bounded by both 255 visits and depth 64; formulas synthesized by
rules are also bounded by the finite proof tree and checked before a theorem is
returned. The context and registry caps bound retained bindings. These are
logical model bounds, not an exact byte bound for Python objects, stack frames,
dictionaries, allocator metadata, or the interpreter.

### Axioms must be visible in the theorem's provenance

Suppose a registry admits <code>deployment_ready : Ready</code>. The proof
<code>Axiom("deployment_ready")</code> checks as <code>Ready</code>, but this is
not a derivation of readiness from nothing. It is a checked use of the admitted
claim. The returned theorem lists <code>deployment_ready</code> in
<code>axioms_used</code>. Unused registered axioms are not dependencies of that
particular proof, although the registry remains part of the run configuration.

Changing an axiom name, registry proposition, or expected conclusion must
force replay or rejection. Saving only “proof passed” loses the evidence
needed to audit that change. Production artifacts normally bind the proof
object, theorem statement, axiom inventory, checker version or digest, command,
status, and diagnostic output.

Assumptions and axioms are not automatically defects. They are obligations to
state boundaries honestly. A model of a processor may assume a memory model; a
protocol proof may assume a cryptographic primitive; a verified component may
assume its foreign-function interface contract. The professional error is
hiding those dependencies or silently strengthening the conclusion.

### What kernel acceptance does and does not establish

If Pebble is implemented exactly as intended and terminates normally, an
accepted term is a derivation according to Pebble's encoded rules and supplied
registry. Even that conditional sentence is not a machine-checked
meta-theorem. This module supplies code inspection and executable tests, not a
formal proof of preservation, normalization, consistency, kernel correctness,
Python correctness, or hardware correctness.

The trusted computing base includes at least:

1. the kernel source actually executed;
2. the meaning of Python 3.11 used by that source;
3. formula equality and immutable-record behavior;
4. the supplied axiom registry and open assumptions;
5. artifact loading and the command that selected the files; and
6. the host runtime, operating system, and hardware to the extent faults can
   change execution or evidence.

Reducing a checker is valuable because a smaller trust bottleneck is easier to
audit or reimplement independently. “Small” is not synonymous with “proved.”
Testing a kernel with its own expected outputs is useful fault-detection
evidence, not a soundness theorem.

### Replay, independent checking, and mutation answer different questions

Deterministic replay checks that the same certificate, context, registry, and
kernel yield the same theorem again. A separately implemented kernel can reduce
common-mode risk if its specification and test oracle are not copied from the
first implementation. Proof-producing automation plus a small certificate
checker separates search from trust, but only when the checker validates every
claimed step rather than trusting a solver's success flag.

Mutation demonstrates test sensitivity. Change a hypothesis label so it is
unbound, replace the expected proposition, rename an axiom, corrupt a proof
constructor, or exceed a cap. Preserve the nonzero result and stable error.
Then restore the original object and preserve the successful replay. The
failure/recovery pair shows that the exercised check can distinguish that
specific fault. It does not prove that every possible fault will be detected.

Endpoint tests must be jointly feasible. A 255-node balanced formula and proof
each have shallow depth; adding a binary formula wrapper causes attempted visit
256, while adding a one-node proof wrapper causes attempted proof visit 256,
without first hitting the depth or context cap. A depth-40 proof uses fewer
than 255 nodes and
one additional implication application reaches depth 41 without extending the
context. A 32-assumption proof stays below the depth-40 cap; the next extension
isolates the context rejection.

## Worked example

The [worked example](examples/worked_example.py) first proves
<code>(Ready and Safe) -&gt; Ready</code> by assuming the conjunction and applying
left elimination. Its open assumption is discharged by implication
introduction, and its used-axiom inventory is empty.

It then configures <code>deployment_ready : Ready</code>, applies the identity
proof <code>Ready -&gt; Ready</code> to that axiom, and reports the exact dependency
<code>("deployment_ready",)</code>. The second conclusion is only as strong as
the admitted deployment claim.

Run both the narrative example and the complete smoke suite:

~~~sh
cd curriculum/modules/frm-102
PYTHONDONTWRITEBYTECODE=1 python3 -B examples/worked_example.py
PYTHONDONTWRITEBYTECODE=1 python3 -B checks/lab_smoke.py
~~~

The final command prints <code>frm-102 lab smoke: PASS</code> and exits zero.

## Check your understanding

1. In <code>Gamma ; Delta |- p : P</code>, what do the four named components
   mean?
2. Why is <code>Axiom("ready")</code> not a proof of <code>Ready</code> from no
   trusted premise?
3. Which rule discharges a local assumption, and which proof constructor
   records that discharge?
4. Why must implication elimination compare the argument proposition to the
   antecedent?
5. Why does replay by the same kernel not independently prove that kernel
   sound?
6. Name four members of Pebble's trusted computing base.
7. What does one observed mutation/failure/recovery pair establish, and what
   does it not establish?
8. Why are the proof-node, depth, and context endpoint shapes different?

## Next step

Complete the lab by specifying and implementing **Cairn**, a distinct proof
language with changed connectives, bounds, labels, and certificate forms. Then
complete the independent **Flint** assessment without importing Pebble or your
Cairn solution. Preserve the proof, statement, assumptions, axiom inventory,
checker hash, commands, stdout, stderr, and immediate status for every claimed
result. After passing, continue to <code>frm-103</code>, where automated search
must produce evidence checked by an explicit certificate verifier.

## Sources

- [The Pebble teaching kernel](examples/proof_kernel.py) — normative executable
  model for this lesson.
- [The worked certificate replay](examples/worked_example.py) — closed and
  axiom-dependent examples.
- [The portable smoke suite](checks/lab_smoke.py) — rule, malformed-object,
  endpoint, replay, and mutation/recovery evidence.
- [Python 3.11 data classes](https://docs.python.org/3.11/library/dataclasses.html)
  — host-language record behavior. This link is optional background; all
  required courseware and checks run offline.
