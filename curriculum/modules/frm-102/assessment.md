# Assessment: independent Flint proof certificates

## Instructions

Complete this assessment independently in a fresh temporary directory using
Python 3.11 or newer and only the standard library. Do not import, copy, rename,
or lightly translate Pebble or a Cairn solution. Submit the specification,
checker, tests, worked certificates, <code>trust.md</code>, and
<code>evidence.md</code>. All generated files remain beneath the temporary
workspace and all execution must work offline.

## Knowledge check

1. Explain **FRM-102-01** by distinguishing a proposition, judgment, inference
   rule, derivation, proof term, certificate, local assumption, discharged
   assumption, axiom, construction, and replay.
2. Read <code>Gamma ; Delta |- p : P</code> aloud. What changes if
   <code>Gamma</code> is empty but <code>Delta</code> is not?
3. Write introduction and elimination rules for conjunction and implication.
4. Why must an axiom registry fix the proposition associated with a name?
5. Explain **FRM-102-02** by naming the checks needed before accepting an
   implication-elimination certificate.
6. Explain **FRM-102-03** by inventorying a small kernel's trusted computing
   base and stating a conditional soundness boundary.
7. Contrast repeated replay, an independent checker, mutation testing, and a
   formal meta-proof. Name one limitation of each.
8. Why can finite green tests support **FRM-102-04** without proving kernel
   correctness, consistency, termination, security, or an Orange property?

## Independent task

Create <code>flint_kernel.py</code>, <code>test_flint_kernel.py</code>,
<code>trust.md</code>, and <code>evidence.md</code>.

1. **Language and judgment — FRM-102-01.** Define immutable propositions
   <code>Claim(name)</code>, <code>Falsehood</code>,
   <code>Either(left,right)</code>, and <code>Therefore(left,right)</code>.
   Define certificates for named assumptions, left and right disjunction
   introduction, disjunction elimination with two discharged branch
   assumptions, implication introduction/application, falsehood elimination,
   and trusted-registry lookup. Labels match
   <code>[A-Z][A-Z0-9]{0,19}</code> in ASCII and active labels are unique.
2. **Rules and checker — FRM-102-02.** Write every inference rule before its
   implementation. For disjunction elimination, check the scrutinee is
   <code>Either(A,B)</code>, check the left branch under a fresh <code>A</code>
   assumption and the right branch under a fresh <code>B</code> assumption, and
   require identical branch conclusions. For implication application require
   exact structural antecedent equality. Return an immutable theorem or a
   stable code/message; never return partial success on failure.
3. **Integrity and bounds — FRM-102-02.** Reject malformed fields, unsupported
   objects, cycles, unknown and duplicate labels, unknown axioms, wrong
   connective use, branch disagreement, antecedent mismatch, and expected
   mismatch. Permit at most 319 proof visits, proof depth 44, 383 proposition
   visits per explicit or resulting proposition, proposition depth 56, 28
   active assumptions, and 14 registry entries. Check each bound before the
   next operation that would exceed it.
4. **Assumptions and axioms — FRM-102-03.** The immutable registry alone maps
   an axiom name to its proposition. Return sorted names of only reached
   axioms. Supply a closed axiom-free proof of
   <code>Therefore(A, Either(A,B))</code>, an open proof, a proof that uses one
   axiom, and a proof whose two branches use different axioms and whose result
   therefore inventories both.
5. **Trust inventory — FRM-102-03.** Inventory the exact checker artifact,
   Python semantics, equality/records, context, registry, command and artifact
   selection, host runtime, operating system, and hardware. Separate untrusted
   certificate producers. State the strongest conditional acceptance claim
   justified and at least eight explicit non-proofs.
6. **Rule and invalid tests — FRM-102-04.** Cover every certificate form,
   scrutinee branch, discharge edge, and rejection code. Include malformed
   names/fields, unsupported objects, a proof cycle, a proposition cycle,
   branch-result disagreement, wrong implication antecedent, registry
   substitution, and deterministic repeated failures with exact messages.
7. **Endpoint tests — FRM-102-04.** Construct exact and next-operation evidence
   for all six bounds. Document proof visits, proof depth, proposition visits,
   proposition depth, context size, and registry size for every shape and
   demonstrate that an unrelated cap cannot mask the expected rejection.
8. **Replay and failure sensitivity — FRM-102-04.** Replay each valid proof
   twice. Independently mutate six facts: a discharged label, disjunction side,
   equal branch conclusion, implication antecedent, axiom name, and node-limit
   endpoint. Capture a targeted nonzero status and diagnostic, restore the
   original, and capture status zero for every pair.
9. **Reproducibility.** Record the Python version, absolute workspace, source
   hashes, exact commands, stdout, stderr, and immediate statuses. Explain the
   time and retained-state bounds without giving an exact Python byte claim.
10. **Claim boundary.** State that the evidence does not prove Flint's kernel,
    its rules consistent, Python or hardware correct, all certificates
    terminating outside the caps, any compiler or security property, or any
    Orange implementation, conformance, verification, or professional-readiness
    property.

## Completion criteria

Use the [rubric](rubric.md). Passing requires at least 80/100 and every critical
criterion. A complete submission faithfully implements **FRM-102-01** and
**FRM-102-02**, exposes the axiom and trust dependencies required by
**FRM-102-03**, and supplies the endpoint, malformed, replay, and observed
mutation/recovery evidence required by **FRM-102-04**. Commands, hashes,
channels, statuses, and non-proofs must be independently auditable.
