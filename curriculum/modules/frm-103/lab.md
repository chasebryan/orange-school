# Lab: build and audit Lantern automation

## Goal

Build a bounded deterministic CNF search producer and a separately callable
certificate checker. Demonstrate sound use of <code>sat</code>,
<code>unsat</code>, and <code>unknown</code>; attack every certificate boundary;
and preserve evidence whose claims stop at the checked formula.

## Setup

From the repository root, inspect and run Kindle:

~~~sh
cd curriculum/modules/frm-103
python3 --version
PYTHONDONTWRITEBYTECODE=1 python3 -B examples/worked_automation.py
PYTHONDONTWRITEBYTECODE=1 python3 -B checks/lab_smoke.py
~~~

Use Python 3.11 or newer and only the standard library. Create a fresh learner
workspace with <code>mktemp -d</code>. Keep generated source and evidence under
that directory. Do not import, copy, rename, or mechanically translate Kindle.
Lantern uses the distinct contract below. No network, external solver, global
configuration change, or privileged operation is required.

## Tasks

1. **Specify the logic and statuses — FRM-103-01.** Define positive and
   negative literals, disjunctive clauses, CNF conjunction, total models,
   partial assignments, and the exact meanings of <code>sat</code>,
   <code>unsat</code>, and <code>unknown</code>. Explain why an external kill or
   empty output supplies none of those solver statuses.
2. **Define Lantern input.** Use lowercase names <code>a</code> through
   <code>e</code>, 1 through 16 clauses, and 1 through 4 distinct literals per
   clause. Reject a clause containing both a name and its negation rather than
   normalizing it. Represent input with immutable records and tuples. Give
   stable codes and messages for unsupported objects, malformed names, repeated
   literals, complementary literals, empty/oversized clauses, and too many
   variables or clauses.
3. **Separate production from checking — FRM-103-01 and FRM-103-02.** Implement
   <code>produce</code> and <code>check_candidate</code> as separate entry
   points. The producer uses deterministic name order, false before true, at
   most 31 partial-assignment visits, and no wall-clock claim. The checker must
   not call <code>produce</code> or trust a status string.
4. **Check SAT models — FRM-103-02.** Require one exact Boolean for each
   declared name in sorted order. Independently reevaluate every clause. Reject
   omitted, extra, repeated, non-Boolean, or unsatisfying assignments. Preserve
   the checked model as the witness; do not call the producer's search trace a
   proof.
5. **Check UNSAT certificates — FRM-103-02.** Design immutable
   <code>Dead(clause_number)</code> leaves and
   <code>Fork(name,no,yes)</code> branches. A dead leaf must reference a clause
   false on its branch. A name may not repeat on one path. Both fork children
   are mandatory. Check active-object cycles, depth before descent, and node
   count before the next visit. Shared subtrees count once per branch visit.
6. **Fail closed — FRM-103-02 and FRM-103-04.** Accept a SAT status only with a
   checked model, UNSAT only with a checked complete tree, and UNKNOWN only
   without a certificate. Directly submit a model under an UNSAT status, a tree
   under SAT, a certificate under UNKNOWN, foreign result objects, misspelled
   statuses, Boolean counts, and counts outside the declared search envelope.
7. **Make endpoints feasible — FRM-103-03.** Build 16 four-literal clauses that
   exclude every assignment to four names. Show
   <code>1+2+4+8+16=31</code>. Reach the name, clause, literal, search-node,
   certificate-node, and depth endpoints without an earlier rejection. Show
   that budget 30 yields UNKNOWN and 31 yields checked UNSAT. State the
   smallest structurally representable certificate-node overflow and isolate
   it from depth rejection.
8. **Attack certificates — FRM-103-03.** Exercise an out-of-range leaf, a leaf
   whose clause remains possible, an unknown and repeated branch name, missing
   child, unsupported host object, active cycle created by bypassing
   immutability, exact depth and next depth, exact nodes and smallest overflow,
   incomplete model, non-Boolean model entry, and satisfying model altered to
   falsify one clause. Assert exact code/message pairs.
9. **Preserve deliberate failures — FRM-103-03.** Forge at least four candidate
   results that the checker rejects: one status/payload mismatch, one corrupted
   leaf index, one incomplete branch, and one false model. Record each nonzero
   immediate status and diagnostic. Restore the authentic artifact and record
   the independent passing check after each failure.
10. **Inventory trust and claims — FRM-103-04.** In <code>trust.md</code>, list
    the CNF encoding, producer, checker, Python semantics, artifact selection,
    commands, runtime, operating system, hardware, and claim-mapping argument.
    Explain why the producer is outside the correctness trust base only when
    the checker fully validates its evidence. Name shared representation and
    specification risks. State that the work proves no checker soundness,
    external encoding, Python, host, security, compiler, or Orange property.
11. **Record reproducible evidence.** In <code>evidence.md</code>, preserve the
    Python version, absolute temporary path, SHA-256 identities, exact commands,
    separate stdout/stderr, immediate statuses, input identities, endpoint
    arithmetic, certificate sizes/depths, failure/restoration pairs, and the
    exact narrow claim attached to each checked result.

## Verification

Run the learner suite from the temporary workspace and preserve the immediate
status before another command can replace it:

~~~sh
PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest -v \
  >passing.stdout 2>passing.stderr
status=$?
printf 'test status: %s\n' "$status"
~~~

Status zero is necessary but not sufficient. Review Lantern's specification,
input validator, search, model checker, refutation checker, forged-object tests,
trust inventory, and evidence record. Confirm that the checker never calls the
producer, UNKNOWN carries no logical conclusion, every certificate branch is
covered, all cap endpoints are reachable, and no claim escapes the bounded CNF.

Finally rerun the repository smoke separately:

~~~sh
cd /absolute/path/to/orange-school/curriculum/modules/frm-103
PYTHONDONTWRITEBYTECODE=1 python3 -B checks/lab_smoke.py
~~~

## Reflection

Write six to eight sentences answering: Which forged status was easiest to
reject? Why does a complete model need every declared variable even when one is
unused? What makes a refutation branch exhaustive? Which endpoint required the
most careful arithmetic? What can UNKNOWN conceal? Which common-mode defect
could affect producer and checker? Which component connects the CNF to an
external requirement? What exact conditional claim can you make after one
Lantern certificate checks?
