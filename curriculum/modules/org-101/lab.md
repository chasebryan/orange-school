# Lab: establish an exact Orange S3a record

## Goal

Produce a reproducible record of the current `check` and `eval` behavior from
an archive of the pinned commit. Limit every conclusion to the implemented
pre-alpha S3a typed-literal boundary.

## Setup

Work from the Orange School repository root. A local Orange Git object store
must contain the exact revision:

```bash
export ORANGE_REPO="${ORANGE_REPO:-../orange}"
ORANGE_REV="ee0fa66d3d38af5e8e10adaa67555b1f0cebc6f6"

test -d "$ORANGE_REPO/.git"
actual_revision="$(git -C "$ORANGE_REPO" rev-parse "${ORANGE_REV}^{commit}")"
printf '%s\n' "$actual_revision"
test "$actual_revision" = "$ORANGE_REV"
rustup run 1.96.1 rustc --version
```

Stop and report an identity blocker if the object or Rust `1.96.1` is absent.
Do not fetch into, check out, reset, clean, or build inside the Orange source
repository.

Archive only the files needed for this lab into a fresh temporary directory:

```bash
ORANGE_SNAPSHOT="$(mktemp -d "${TMPDIR:-/tmp}/orange-org101.XXXXXX")"
(
  set -euo pipefail
  git -C "$ORANGE_REPO" archive "$ORANGE_REV" -- \
    compiler rust-toolchain.toml |
    tar -x -C "$ORANGE_SNAPSHOT"
)

test ! -e "$ORANGE_SNAPSHOT/.git"
git -C "$ORANGE_REPO" show "$ORANGE_REV:rust-toolchain.toml"

orange_cli() {
  cargo +1.96.1 run --quiet --locked --offline \
    --manifest-path "$ORANGE_SNAPSHOT/compiler/Cargo.toml" \
    -p orangec -- "$@"
}
```

All extraction and build output now stays under `ORANGE_SNAPSHOT`. A dirty or
shared source checkout cannot alter the archived commit's bytes.

## Tasks

1. Record `ORANGE_REPO`, `ORANGE_SNAPSHOT`, the full resolved revision, and the
   complete `rustc --version` line.
2. Read `curriculum/modules/org-101/examples/minimal.or`. Predict standard
   output, standard error, and status for both `check` and `eval`.
3. Run the example with a quoted absolute path:

   ```bash
   example="$(pwd -P)/curriculum/modules/org-101/examples/minimal.or"
   sha256sum "$example"

   orange_cli check "$example"
   check_status="$?"
   printf 'check status: %s\n' "$check_status"

   orange_cli eval "$example"
   eval_empty_status="$?"
   printf 'empty-Core eval status: %s\n' "$eval_empty_status"
   ```

4. Record that both commands produced no compiler output and returned `0`.
   Explain the difference: `check` completed lexing, parsing, bounded semantic
   validation, and empty-Core construction; `eval` then visited that empty Core
   and therefore had no value line to print.
5. Before running it, predict the exact output of the pinned typed fixture.
   Then run it twice:

   ```bash
   typed="$ORANGE_SNAPSHOT/compiler/fixtures/typed-answer.or"
   sha256sum "$typed"
   orange_cli eval "$typed"
   first_status="$?"
   printf 'first eval status: %s\n' "$first_status"

   orange_cli eval "$typed"
   second_status="$?"
   printf 'second eval status: %s\n' "$second_status"
   ```

6. Record the three value lines in source order, empty standard error, and
   status `0` for each run. Explain why `-0x2a` displays as decimal `-42` and
   why `0xff` displays as exactly two lowercase hexadecimal digits.
7. Write one supported conclusion for `check`, one supported conclusion for
   `eval`, and at least six explicit non-conclusions. Include general program
   execution, proof checking, code generation, canonical Core or verified
   lowering, target/ABI behavior, and production readiness.

## Verification

Your record is complete only if all of these statements are true:

- the resolved revision is
  `ee0fa66d3d38af5e8e10adaa67555b1f0cebc6f6`;
- the Rust version begins with `rustc 1.96.1`;
- the compiler was built from a fresh Git archive rather than from a mutable
  source checkout;
- `check` of `minimal.or` returned `0` with both output streams empty;
- `eval` of `minimal.or` returned `0` with both output streams empty;
- each typed-fixture evaluation returned `0`, had empty standard error, and
  printed exactly:

  ```text
  demo::answer: Int = 42
  demo::negative: Int = -42
  demo::mask: Word[8] = 0xff
  ```

- the claim record says bounded S3a validation, Core construction, and closed-
  literal reference evaluation, not arbitrary execution, compilation, proof,
  or production verification.

## Reflection

Why is the phrase “the program ran” too broad for `orangec eval` at this
revision? For each excluded capability you listed, name the missing language or
compiler boundary that would need specification and evidence before that claim
could be made.
