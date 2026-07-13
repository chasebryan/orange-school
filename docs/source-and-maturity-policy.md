# Source and maturity policy

## School repository identity

The canonical home for this curriculum is
<https://github.com/chasebryan/orange-school>. Release records, issue links,
review evidence, and downstream references must name that repository plus an
exact revision or tag. A local directory name or mutable branch name is not a
stable curriculum identity.

## Authoritative Orange source

Curriculum facts are pinned to:

- repository: `https://github.com/chasebryan/orange`
- revision: `ee0fa66d3d38af5e8e10adaa67555b1f0cebc6f6`
- language edition: `2026`
- compiler status: production-lineage pre-alpha; stages S1 and S2 complete;
  accepted S3a implemented; S3 incomplete

The catalog records this identity for automation. Orange-specific lessons must
cite a tracked, revision-pinned normative document, implementation, or test.
Untracked drafts and mutable branch pages are not curriculum authority.

## Evidence order

When sources disagree, use this order:

1. accepted normative language or format specification at the pinned revision;
2. accepted decision or proposal defining that surface;
3. executable conformance tests and implementation behavior;
4. tracked architecture, roadmap, assurance, and user-journey documents;
5. explanatory repository documentation.

An implementation bug does not silently redefine a normative rule. A proposal
does not silently become an implemented feature.

## Maturity wording

Use these verbs precisely:

- **is accepted by the current parser** — demonstrated current syntax;
- **is implemented** — present and tested at the pinned revision;
- **is ratified but unimplemented** — decided design, not usable behavior;
- **is proposed** — directional and subject to change; and
- **is not defined** — outside the current language surface.

Never use “compiled,” “implementation ran,” “proved,” “verified,”
“constant-time,” or “production-ready” when the evidence establishes only
lexing, parsing, narrow S3a semantic checking, or reference evaluation.

## Sync protocol

When Orange advances:

1. update the pinned revision in the catalog;
2. review the source project’s roadmap, decisions, normative specification,
   tests, diagnostics, and user journeys;
3. record which curriculum competencies changed;
4. update or add examples and their expected outcomes;
5. move a blocked module to planned only when its design inputs are settled;
6. move a module to released only after complete learner material and automated
   evidence exist; and
7. run `make check` against the new exact revision.

`make examples` treats `ORANGE_REPO` as a Git object provider, not as trusted
checked-out source. The checker verifies the catalog commit object exists and
exports only that commit's compiler and Rust toolchain files into a fresh
temporary directory. This keeps evidence stable when the provider is on another
branch or has local changes.

Curriculum and language versions need not share numbers. The catalog records
both.

## Host validation envelope

General labs are checked with Python 3.11 or newer, Bash 5.1 or newer, Git 2.39
or newer, a C17 compiler, and the Rust 1.96.1 toolchain, without network access.
This is a course-tooling compatibility envelope, not an Orange supported-host
or release claim. A module that needs a new host tool must add and validate that
requirement before release.

## Licensing boundary

The source Orange repository and this school currently have no selected
outbound license. Curriculum authors may cite and paraphrase repository facts
for this workspace, but must not assume permission to copy or redistribute
substantial source text. Add a license only through an explicit owner decision.
