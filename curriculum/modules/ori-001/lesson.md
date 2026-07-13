# Start here: evidence, status, and your path

Orange School assumes no prior technical experience. This module teaches you
how to tell what is available now, describe evidence without exaggeration, and
start at the first assessment you have not yet passed.

## Learning objectives

- **ORI-001-01:** Distinguish released, planned, and blocked curriculum
  material.
- **ORI-001-02:** Classify a test, proof, assumption, and proposal without
  strengthening its claim.
- **ORI-001-03:** Produce a personal path that begins at the earliest unpassed
  assessment.

## Prerequisites

None. You only need a way to read this repository, such as a web browser or
text editor, and somewhere to write your answers. The orientation lab does not
require a terminal.

## Lesson

**The catalog is the curriculum record.** The
[curriculum catalog](../../catalog.json) lists every module, its prerequisites,
its curriculum status, and its learning outcomes. Explanatory pages are useful,
but use the catalog when two descriptions disagree.

Curriculum status answers one question: “May a learner rely on this module as
available course material now?”

| Status | What it means | Learner action |
| --- | --- | --- |
| <code>released</code> | The complete learner material exists and passes the repository release gates. | You may study it or take its assessment for placement. |
| <code>planned</code> | Its place and purpose are recorded, but learner-ready material is incomplete. | Do not count it as available or completed. |
| <code>blocked</code> | A named unresolved dependency forbids release. | Stop at the boundary; do not pretend the missing capability exists. |

Status does not say that every statement in a module is universally true.
It also does not say what Orange itself implements. The separate
<code>source_maturity</code> field records whether subject matter is general,
implemented, ratified, or proposed. Keep those two axes separate.

**Evidence labels describe different kinds of support.**

| Label | Honest meaning | What it does not establish by itself |
| --- | --- | --- |
| Test | An observed result for a stated procedure, input, tool, and revision. | All possible cases or a universal theorem. |
| Proof | A conclusion derived from stated premises under stated rules, possibly checked by a named tool. | The truth of unstated premises or correctness outside its scope. |
| Assumption | Something the claim relies on but the supplied evidence does not establish. | Evidence that the assumed statement is true. |
| Proposal | A suggested future decision, design, or behavior. | Current or guaranteed future behavior. |

An evidence packet may contain all four. For example, a proof can depend on an
assumption, and a proposal can request a new test. Naming each item correctly
is more useful than applying one impressive label to the whole packet.

Use this sentence pattern for a bounded claim:

> With **procedure and tool**, **input** produced **observed result** at
> **revision or date**. This supports **narrow conclusion**. It does not
> establish **named exclusions**.

**Placement still requires evidence.** A beginner starts with
<code>ori-001</code>. An experienced learner may skip instruction, but only
after passing the same independent assessment. Build a personal path this way:

1. List released modules in prerequisite order, beginning with
   <code>ori-001</code>.
2. Mark a module “passed” only when you can point to its assessment result.
   “Read it,” “used it before,” and “probably know it” are not pass evidence.
3. Find the earliest module without passing evidence. That assessment is your
   first step.
4. Continue through released prerequisites. Stop when the next required module
   is planned or blocked and record that status instead of claiming completion.
5. Recalculate the path whenever an assessment is passed or a status changes.

This rule prevents both unnecessary repetition and hidden knowledge gaps.

## Worked example

Mina records this assessment ledger:

| Module | Result | Evidence |
| --- | --- | --- |
| <code>ori-001</code> | Passed | Rubric record dated 2026-07-12 |
| <code>cmp-101</code> | Not passed | First attempt scored 72/100 |
| <code>org-101</code> | Not attempted | None |

Even though Mina has used a terminal at work, her path begins with the
<code>cmp-101</code> assessment because it is the earliest unpassed gate.
<code>org-101</code> comes later because it requires <code>cmp-101</code>.

Mina also sees this note:

> At revision R, the checker accepted <code>sample.or</code> and exited 0. We
> expect every Orange program to compile.

She classifies the observed command result as a **test**. “Every Orange program
will compile” is not supported by that one case and reads as a **proposal or
expectation**, not current evidence. An honest rewrite is:

> At revision R, the checker accepted <code>sample.or</code> and exited 0.
> This supports acceptance of that file by that checker revision. It does not
> establish behavior for other files, compilation, execution, or verification.

## Check your understanding

1. A module has a defined title and outcomes, but its learner files are not
   complete. Which curriculum status fits?
2. A module cannot be released until Orange implements evaluation. Which status
   fits?
3. “Command C exited 0 for input I at revision R” is what kind of evidence?
4. A derivation reaches conclusion Q from premise P. What must accompany the
   word “proof”?
5. Your first two assessments passed and the third has no result. Where does
   your personal path begin?

**Answers:** (1) planned; (2) blocked; (3) a test; (4) the stated premise,
rules or checking method, scope, and any assumptions; (5) at the third
assessment, the earliest one without pass evidence.

## Next step

Complete the [guided lab](lab.md), then take the
[independent assessment](assessment.md). A passing result is at least 80/100
and every critical criterion in the [rubric](rubric.md). After passing, update
your personal path; for a new learner, the next released assessment is normally
<code>cmp-101</code>.

## Sources

- [Curriculum catalog](../../catalog.json), repository snapshot used for module
  status, prerequisites, and stable outcome IDs.
- [Curriculum architecture](../../../docs/curriculum-architecture.md), “Two
  independent status axes,” “Assessment gates,” and “Module contract.”
- [Assessment system](../../../docs/assessment-system.md), placement and scoring
  policy.
- [Current status](../../../docs/current-status.md), snapshot dated 2026-07-12.
