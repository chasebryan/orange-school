# Curriculum architecture

## Purpose

Orange School must let a learner begin without hidden prerequisites and finish
with evidence that they can perform a real Orange professional workflow. It is
not a tour of syntax and it is not allowed to outrun the language it teaches.

The curriculum therefore has three simultaneous structures:

1. a prerequisite graph from orientation through professional practice;
2. a competency graph connecting instruction, guided practice, independent
   assessment, and capstones; and
3. a maturity gate connecting every Orange-specific claim to an exact source
   revision and implementation stage.

The canonical representation of all three is
[`curriculum/catalog.json`](../curriculum/catalog.json).

## Learner promise

A learner may enter at `ori-001` with no assumed terminal, programming,
mathematics, cryptography, or formal-methods experience. Placement evidence may
let an experienced learner skip instruction, but never an assessment gate.

A graduate of the shared core and one role specialization will be able to:

- reproduce an exact toolchain and explain what is trusted;
- connect a standards requirement to a specification, implementation, and
  scoped evidence;
- distinguish proof, testing, external evidence, assumptions, and non-claims;
- inspect the compiler, target, ABI, and artifact boundary relevant to a claim;
- work fail-closed when evidence is missing or invalid; and
- trace where assurance stops instead of applying a generic “verified” label.

That standard is intentionally conditional on Orange implementing the required
professional surface. Until then, the corresponding modules and capstones stay
blocked.

## Curriculum layers

| Layer | Purpose | Exit evidence |
| --- | --- | --- |
| Orientation | Establish learning workflow, placement, and honest status reading | Personal path and correctly classified claims |
| Computing practice | Terminal, files, Git, debugging, tests, and repeatable commands | Reproducible repository task |
| Programming | Control, data, types, errors, algorithms, testing, C, and Rust | Tested program and review |
| Mathematical foundations | Logic, proofs, number theory, algebra, and probability | Written and executable reasoning |
| Cryptography | Security notions, constructions, misuse, standards, and vectors | Standards-grounded implementation analysis |
| Systems | Representation, memory, ABI, targets, SIMD, and leakage | Artifact and side-channel analysis |
| Languages and formal methods | Semantics, type/effect systems, compilers, refinement, and proof checking | Model-to-implementation argument |
| Assurance | Claims, TCBs, adversarial tests, reproducibility, and lifecycle response | Replayable evidence and incident exercise |
| Orange Today | Exact implemented Orange 2026 frontend and S3a typed-literal tooling | Passing, intentionally failing, and exact reference-evaluation cases |
| Orange professional core | Remaining S3 and future S4-S8 Orange workflows | J-01 through J-08 workflow evidence |
| Role specialization | Deep practice for one of five project personas | Independently graded portfolio capstone |

## Instructional languages

The foundations path uses the smallest language suited to each learning goal:

- Python with only its standard library for first programming, algorithms,
  executable mathematics, and test design;
- C and Rust for representation, ownership, native artifacts, and foreign
  interfaces; and
- Orange only for behavior supported by the pinned Orange capability stage.

This progression keeps first programming approachable while still reaching the
actual systems boundary Orange professionals must inspect. A Python, C, or Rust
lab is prerequisite evidence only; it cannot satisfy an Orange operational
competency. Exact host-language versions are pinned when those currently
planned modules become released.

## Two independent status axes

Curriculum status and source maturity must never be conflated.

### Curriculum status

- `released`: complete learner material exists and passes every repository gate.
- `planned`: the competency and graph position are defined, but the material is
  not learner-ready.
- `blocked`: release is forbidden because an explicit dependency is unresolved.

### Source maturity

- `general`: prerequisite knowledge that does not claim an Orange feature.
- `implemented`: exercised by the pinned Orange source and tests.
- `ratified`: normatively decided but not yet implemented; may be discussed as
  design context, never as runnable behavior.
- `proposed`: a project direction or user journey that can still change.

A module may be `released` only when its source maturity is `general` or
`implemented`. This is enforced automatically.

## Module contract

Every released module has one catalog entry and exactly these learner files:

- `lesson.md` — prerequisites, objectives, teaching, worked example, knowledge
  check, next step, and versioned sources;
- `lab.md` — setup, guided tasks, verification, and reflection;
- `assessment.md` — knowledge check, independent task, and completion criteria;
- `rubric.md` — critical criteria, scoring, feedback, and retry policy; and
- optionally `examples/` — executable or intentionally invalid artifacts; and
- for every released general module after orientation, a registered
  `checks/lab_smoke.py` or `checks/lab_smoke.sh` that verifies its runnable
  examples without network access.

Each objective has a stable ID. The same ID must appear in the lesson and
assessment. Each competency mapping declares `instruction`, `practice`, and
`assessment`; “mentioned” does not count as coverage.

## Assessment gates

- Every released module requires at least 80% and every critical criterion.
- Stage averages cannot hide a failed critical objective.
- Placement can replace instruction only when the learner passes the same
  independent assessment.
- Guided work is never the sole evidence for a professional competency.
- Each specialization ends in a capstone mapped to its primary Orange user
  journeys and reviewed with an analytic rubric.
- Professional completion requires all required modules and capstones to be
  `released`; planned or blocked competencies do not count.

## Structural invariants

`make validate` fails if any of these conditions is false:

- IDs, stages, roles, journeys, outcomes, and competencies are unique and valid;
- every prerequisite exists, precedes its dependent, and forms an acyclic graph;
- every module is reachable from the single beginner entry module;
- every released module has released prerequisites and the full file contract;
- every objective is present in instruction and assessment;
- every released general module after orientation has a contained registered
  host check, while every released Orange example is checked at the exact
  pinned compiler revision;
- every competency and J-01 through J-08 has mapped coverage;
- all five professional roles have exactly one specialization track and
  capstone; and
- no proposed or merely ratified Orange behavior is released as runnable
  curriculum.

## Completion definition

The curriculum is professionally complete only when all of the following are
true at the same pinned Orange release:

1. every required core and specialization module is `released`;
2. every catalog competency has instruction, guided practice, and independent
   assessment;
3. J-01 through J-08 are exercised by runnable labs using supported artifacts;
4. all examples, invalid cases, reference solutions, graph checks, and content
   checks pass in a clean environment;
5. each role capstone meets its critical criteria and 80% threshold; and
6. a clean supported environment reaches its first checked Orange source using
   only published instructions, and representative beginner pilots expose no
   unresolved critical onboarding defect; and
7. the status page contains no blocked professional competency.

A passing documentation build alone is not professional-readiness evidence.
