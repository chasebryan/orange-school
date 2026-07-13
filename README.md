# Orange School

Canonical repository: [chasebryan/orange-school](https://github.com/chasebryan/orange-school)

Orange School is a competency-based path from no assumed technical background
to professional work with the Orange programming language and toolchain.

Orange is being built for specifying, implementing, and verifying
cryptography. That makes the professional prerequisite surface unusually wide:
programming, mathematics, systems, cryptography, formal methods, and assurance
practice all belong in the path. This repository makes those prerequisites
explicit instead of assuming learners already have them.

## Current truth

Orange is pre-alpha. At the exact merged source revision, stages S1 and S2 are
complete and accepted S3a is implemented: deterministic lexing, bounded
parsing, same-kind declaration uniqueness, closed typed `spec` literals for
`Int` and `Word[8]`, a source-ordered noncanonical Typed Reference Core, and
the `orangec lex`, `check`, and `eval` commands. S3 remains incomplete, and
Orange still has no general expressions, typed implementations, refinement,
proof checking, code generation, packages, standard library, or releases.

Accordingly, Orange School separates:

- **released** modules that a learner can complete and verify now;
- **planned** modules whose subject is stable but whose course material is not
  yet released; and
- **blocked** Orange modules that depend on language capabilities or decisions
  that do not exist yet.

Passing `orangec check` at this revision establishes lexical, syntactic, and
the narrow S3a semantic acceptance plus Core construction. It does not execute
an implementation, compile, prove, verify, or establish a cryptographic claim.

## Start here

1. Read [Start Here](curriculum/modules/ori-001/lesson.md).
2. Complete its [lab](curriculum/modules/ori-001/lab.md) and
   [assessment](curriculum/modules/ori-001/assessment.md).
3. Follow the released modules in the
   [learner pathways](docs/learner-pathways.md).
4. Use `make check` to validate the curriculum and its Orange examples.

The machine-readable source of curriculum truth is
[`curriculum/catalog.json`](curriculum/catalog.json). It defines the complete
prerequisite graph, competencies, professional roles, Orange user journeys,
module maturity, and specialization tracks.

## Repository map

- [`docs/curriculum-architecture.md`](docs/curriculum-architecture.md) — design
  rules and completion standard
- [`docs/learner-pathways.md`](docs/learner-pathways.md) — the ordered learner
  journey and five role specializations
- [`docs/competency-matrix.md`](docs/competency-matrix.md) — what graduates must
  be able to do and where it is assessed
- [`docs/assessment-system.md`](docs/assessment-system.md) — scoring, retries,
  stage gates, and capstones
- [`docs/source-and-maturity-policy.md`](docs/source-and-maturity-policy.md) —
  authoritative sources and the rule against teaching proposals as features
- [`docs/authoring-guide.md`](docs/authoring-guide.md) — the module contract
- [`docs/current-status.md`](docs/current-status.md) — implemented curriculum
  versus future work
- `curriculum/modules/` — released learner material
- `scripts/` and `tests/` — automated curriculum and example validation

## Local checks

The default example check uses the Orange Git repository at `../orange` as an
object provider. It exports and builds the catalog's exact pinned commit in a
fresh temporary directory, so the repository may have another branch checked
out or contain unrelated working-tree changes. Override the provider with
`ORANGE_REPO=/absolute/path/to/orange`; it must contain the pinned commit.

```sh
make check
```

Individual gates are:

```sh
make validate
make test
make host-examples
make examples
```

The end-state gate is intentionally stricter and remains red while any module
is planned or blocked:

```sh
make professional-complete
```

Curriculum `0.9.0-dev` currently has thirty-six released modules: orientation;
complete computing, programming, mathematical, cryptography, systems, and
language-construction, formal-methods, and assurance foundations; and the
complete current Orange frontend plus its accepted S3a typed-literal and
reference-evaluation slice. No general foundation module remains planned. The
catalog keeps the S3 remainder and S4-S8 material visible without presenting it
as available.

No outbound license has been selected for this repository. Do not assume that
the material is licensed for redistribution until the owner adds an explicit
license.
