# Authoring guide

## Add a module

1. Add one module entry to `curriculum/catalog.json`.
2. Connect it to existing prerequisites and stable competency IDs.
3. If it is released, create `curriculum/modules/<module-id>/` with
   `lesson.md`, `lab.md`, `assessment.md`, and `rubric.md`.
4. Put every objective ID in both `lesson.md` and `assessment.md`.
5. List every executable or intentionally invalid Orange example in the module
   catalog entry.
6. For a released general module, add a no-network `checks/lab_smoke.sh` or
   `checks/lab_smoke.py` and register it in `host_checks`.
7. Run `make check`.

Do not create learner-facing files for a blocked Orange module. Its catalog
entry is enough to preserve the intended graph without implying availability.

## Write measurable objectives

Use an observable verb and an assessment condition.

Good:

> `ORG-102-02`: Predict whether a source fragment is lexically valid under
> Orange 2026 and name the stable diagnostic family for an invalid case.

Weak:

> Understand Orange lexing.

One module should normally contain three to six objectives. Every objective
must be taught, practiced, and assessed.

## Required lesson headings

- `## Learning objectives`
- `## Prerequisites`
- `## Lesson`
- `## Worked example`
- `## Check your understanding`
- `## Next step`
- `## Sources`

## Required lab headings

- `## Goal`
- `## Setup`
- `## Tasks`
- `## Verification`
- `## Reflection`

## Required assessment headings

- `## Instructions`
- `## Knowledge check`
- `## Independent task`
- `## Completion criteria`

## Required rubric headings

- `## Rubric`
- `## Critical criteria`
- `## Scoring`
- `## Feedback and retry`

## Status changes

- `blocked` to `planned`: cite the source decision or implementation dependency
  that resolved the blocker.
- `planned` to `released`: add the complete file contract, examples, assessment
  mappings, and passing check evidence.
- `released` to blocked or retired: preserve the reason and migration path; do
  not rewrite learner history silently.

## Executable host evidence

General modules use only the catalog's host validation envelope: Python 3.11+
standard library, Bash 5.1+, Git 2.39+, C17, and Rust 1.96.1. A registered
smoke check must:

- run without network access or global configuration changes;
- write only to a fresh temporary workspace;
- exercise the module's normal, boundary, and invalid behavior where relevant;
- return zero only when every declared observation holds; and
- clean only the temporary workspace it created.

Host-language evidence satisfies prerequisite competencies only. It never
satisfies an Orange language or professional-operation competency.

## Interacting resource bounds

Every released module with resource limits must state the counted unit, cap,
and point at which the cap is checked. Treat the limits as one system, not as
independent round numbers:

- construct the exact endpoint for each limit without crossing a different
  limit first;
- construct an isolated rejection immediately beyond it, or name and test the
  smallest representable overflow when the grammar or data model cannot express
  exactly cap plus one;
- show the arithmetic for dependent limits such as tokens versus AST nodes,
  path depth versus active bindings, or checked nodes versus runtime steps;
- assert the diagnostic for the intended limit so a different earlier failure
  cannot masquerade as endpoint coverage; and
- reject or revise any assessment whose required endpoint is mathematically
  unreachable under its other caps.

A larger dynamic budget is justified only when execution can revisit work that
the static pass counts once; otherwise its maximum cannot exceed the admitted
static work. Rubric-critical endpoint evidence must be feasible before a module
can move from planned to released.

## Style

- State current behavior before future direction.
- Prefer a small falsifiable example to a broad assertion.
- Keep proof, tests, external records, and assumptions distinct.
- Name exact editions, revisions, targets, and diagnostic codes where they
  matter.
- Explain every required tool before using it.
- Include accessible text alternatives for meaningful images.
- Do not use unexplained “TODO” placeholders in released modules.
