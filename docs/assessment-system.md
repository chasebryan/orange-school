# Assessment system

## Evidence, not attendance

Completing a lesson or copying a guided example is practice. Completion requires
independent evidence tied to stable objective IDs.

Every released module uses four assessment layers:

1. **retrieval** — explain a concept without copying the lesson;
2. **guided practice** — follow a lab while recording observations;
3. **independent transfer** — solve a changed case without step-by-step
   instructions; and
4. **reflection** — state limitations, assumptions, and the next debugging step.

## Scoring

- Module pass threshold: **80%**.
- Every rubric marks some criteria as critical.
- A learner must pass every critical criterion regardless of total score.
- Knowledge checks may be retried after reviewing the related objective.
- Independent tasks require a fresh variant or a documented correction, not a
  copied answer.
- Stage completion requires every required module, not an average across
  modules.

## Placement

A learner may skip instruction only by passing the normal module assessment.
The evidence is recorded exactly as if the lesson and lab had been completed.
This protects the no-hidden-prerequisites promise without forcing experienced
learners through material they have mastered.

## Orange example evidence

Examples carry explicit expectations in the catalog:

- `check-pass`: `orangec check` must exit successfully;
- `check-fail`: it must fail with the named stable diagnostic code;
- `lex-pass`: `orangec lex` must succeed and emit the named token evidence;
- `lex-fail`: lexing must fail with the named stable diagnostic code;
- `eval-pass`: `orangec eval` must emit the exact registered reference-value
  output without standard-error output; or
- `eval-fail`: evaluation must fail with the named stable diagnostic and emit
  no partial value sequence.

The repository exports the compiler and toolchain files from the exact pinned
Orange Git commit, builds that immutable snapshot in a fresh temporary
directory, and runs every listed example against it. The provider repository's
checked-out branch and working-tree changes are never used. A missing pinned
object, unsafe archive, build failure, or example failure blocks curriculum
release.

## Host lab evidence

Every released general module after orientation registers an executable smoke
check. `make host-examples` runs those checks with isolated temporary home and
temporary directories, deterministic Python hashing, no bytecode writes, and
the catalog's minimum Python, Bash, Git, C17, and Rust versions. The validator rejects
registered code that refers to network operations or escapes its module path.

Compiler checks may point `RUSTUP_HOME` or a user-local C wrapper back to an
already installed read-only tool store when the temporary home hides it. Build
outputs and assessed work must still remain in the fresh temporary workspace;
checks must not install or update a toolchain.

Smoke checks verify the stable worked examples and lab mechanics. They do not
grade the learner's independent reasoning, explanation, or transfer task; the
rubric remains required evidence for those outcomes.

## Capstones

Each role capstone requires:

- a requirements and threat analysis;
- a versioned source, standard, and toolchain inventory;
- implementation or inspection work appropriate to the role;
- positive, negative, and adversarial tests;
- an explicit claim/assumption/exclusion matrix;
- reproducible commands and artifact identities;
- a peer-review response or simulated review record; and
- an oral or written defense of where the evidence stops.

Capstones require at least 80%, every critical criterion, and no unresolved
high-severity correctness or assurance issue. Their detailed rubrics remain
blocked until the corresponding Orange workflows exist.
