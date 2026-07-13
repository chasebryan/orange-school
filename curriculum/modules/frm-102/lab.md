# Lab: construct and audit the Cairn proof kernel

## Goal

Specify, implement, replay, and attack a bounded proof-certificate checker. The
submission must expose every assumption and admitted axiom, inventory its trust
base, isolate each resource endpoint, and keep its claims within the evidence.

## Setup

Inspect and run Pebble from the repository root:

~~~sh
cd curriculum/modules/frm-102
python3 --version
PYTHONDONTWRITEBYTECODE=1 python3 -B examples/worked_example.py
PYTHONDONTWRITEBYTECODE=1 python3 -B checks/lab_smoke.py
~~~

Use Python 3.11 or newer and only the standard library. Create a fresh learner
workspace with <code>mktemp -d</code>; keep generated source and evidence under
that directory. Do not import, copy, rename, or mechanically translate Pebble.
Cairn has the different contract below. No network or privileged operation is
required.

## Tasks

1. **Specify judgments — FRM-102-01.** Define propositions
   <code>Fact(name)</code>, <code>Truth</code>,
   <code>Both(left,right)</code>, and <code>Implies(left,right)</code>. Write the
   judgment <code>Gamma ; Delta |- certificate : proposition</code> in words.
   Distinguish local assumptions, discharged assumptions, configured axioms,
   proof terms, certificates, construction, and replay.
2. **Define certificate rules — FRM-102-01.** Use certificate forms for named
   assumption lookup, truth introduction, both introduction and both-right and
   both-left elimination, implication introduction and elimination, and
   registry axiom lookup. State every premise and conclusion before coding.
   Active labels are unique lowercase ASCII names matching
   <code>[a-z][a-z0-9_]{0,23}</code>.
3. **Implement the kernel — FRM-102-02.** Use frozen records and structural
   formula equality. Infer exactly one conclusion or return a stable code and
   message. Reject unsupported host objects, malformed names and fields,
   unknown assumptions, duplicate active labels, unregistered axioms, wrong
   connective eliminations, antecedent mismatches, expected-conclusion
   mismatches, and cycles created by bypassing immutability.
4. **Enforce bounds — FRM-102-02.** Permit at most 191 certificate-node visits,
   certificate depth 36, 191 proposition-node visits per explicit or resulting
   proposition, proposition depth 48, 24 active assumptions, and 12 axiom
   registrations. Check before the next visit, descent, extension, or
   retention. Repeated shared objects count as repeated visits. Return an
   immutable result with conclusion, open assumptions, sorted used axioms, and
   visit count.
5. **Track dependencies — FRM-102-03.** Make the registry, not the certificate,
   choose an axiom's proposition. Demonstrate one closed axiom-free theorem,
   one theorem with open assumptions, and one closed theorem using exactly one
   of at least two registered axioms. Record only axioms actually reached.
6. **Inventory trust — FRM-102-03.** In <code>trust.md</code>, inventory the
   checker source, executed Python semantics, equality/record behavior,
   assumptions, registry, artifact selection, host runtime, operating system,
   and hardware. Separate certificate producers from checker dependencies.
   State what an independent implementation could reduce and what it would
   still assume.
7. **Test rules and malformed objects — FRM-102-04.** Exercise every inference
   rule and every rejection path. Bypass frozen records to create one formula
   cycle and one certificate cycle. Include an arbitrary unsupported object,
   non-ASCII and overlong names, a duplicate label, an unknown axiom, a wrong
   elimination, and an implication mismatch. Assert exact code/message pairs.
8. **Isolate endpoints — FRM-102-04.** Construct jointly feasible exact and
   next-attempt shapes for all six caps. A node-count shape must stay shallow;
   a depth shape must remain below 191 visits and 24 contexts; a context shape
   must remain below depth 36. Explain why no other cap masks each expected
   result.
9. **Replay and mutate — FRM-102-04.** Replay the same three valid certificates
   twice and assert identical immutable results. Then independently mutate an
   assumption label, expected conclusion, axiom name, implication antecedent,
   and resource endpoint. Preserve the immediate nonzero status and diagnostic
   for each mutation, restore each object, and preserve immediate status zero.
10. **Record evidence and non-proofs.** In <code>evidence.md</code>, record the
    Python version, absolute temporary path, source hashes, exact commands,
    separate stdout/stderr, and immediate statuses. Justify the bounded work
    and retained logical state without claiming exact Python bytes. State that
    Cairn tests are not a soundness, normalization, consistency, termination,
    Python, hardware, security, compiler, or Orange proof.

## Verification

Run all learner tests from the temporary workspace, preserving channels and
the immediate status:

~~~sh
PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest -v \
  >passing.stdout 2>passing.stderr
status=$?
printf 'test status: %s\n' "$status"
~~~

Status zero is necessary but not sufficient. Inspect the rules, checker,
tests, <code>trust.md</code>, and <code>evidence.md</code>. Confirm that every
constructor has one encoded rule; registry propositions are not certificate
controlled; unused axioms stay out of result dependencies; all caps are
checked before work or retention; malformed cycles fail deterministically;
each mutation genuinely fails; every restoration passes; and theorem claims
name their assumptions and trust base.

Finally rerun the repository smoke separately:

~~~sh
cd /absolute/path/to/orange-school/curriculum/modules/frm-102
PYTHONDONTWRITEBYTECODE=1 python3 -B checks/lab_smoke.py
~~~

## Reflection

Write six to eight sentences answering: Which premise did the easiest mutation
violate? Why is a used-axiom list stronger evidence than the complete registry
alone? Which endpoint shape was hardest to isolate? What kernel defect could
same-implementation replay miss? How could an independent checker still share
a specification error? Which trusted component is outside your Python files?
What conditional claim can you make about an accepted Cairn certificate? Why
does the lab establish no professional Orange verification capability?
