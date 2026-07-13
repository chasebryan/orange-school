# Pin and run Orange Today

## Learning objectives

- **ORG-101-01:** Verify the exact Orange source revision and pinned Rust
  toolchain without changing the Orange source repository.
- **ORG-101-02:** Run `orangec check` on a valid Orange 2026 source and
  interpret its silent lexical, syntactic, semantic, and Core-construction
  success.
- **ORG-101-03:** Distinguish the implemented pre-alpha S3a boundary from at
  least four capabilities that the result does not establish.

## Prerequisites

Complete `cmp-101`. You should be able to open a terminal, move to the Orange
School repository root, quote paths, inspect an exit status, and distinguish
standard output from standard error.

## Lesson

This module begins with identity, because a command name does not identify the
implementation behind it. Every Orange observation in this module is tied to
this exact source revision:

```text
ee0fa66d3d38af5e8e10adaa67555b1f0cebc6f6
```

At that revision Orange is production-lineage, pre-alpha S3a. OEP-0003 is
accepted for one bounded typed-literal slice, but the compiler makes no stable
public compatibility promise. Treat the capability as provisional course
material, not as a supported Orange release. The repository also has unresolved
outbound license and working-name decisions, so this exercise is not permission
to redistribute source or binaries.

The repository pins Rust `1.96.1`, uses Rust edition 2024 for the compiler, and
declares no third-party Rust dependencies. An exact run record contains:

1. the source repository and full commit identity;
2. the selected Rust toolchain;
3. the complete command and exact input identity;
4. the exit status, standard output, and standard error; and
5. a claim limited to the phases that actually ran.

The current CLI exposes three different observations:

| Command | Implemented observation at this revision |
| --- | --- |
| `orangec lex SOURCE...` | Emits the deterministic token stream. It does not parse or assign meaning. |
| `orangec check SOURCE...` | Runs lexing, parsing, bounded semantic validation, and successful construction of the noncanonical Typed Reference Core. Accepted input is silent. |
| `orangec eval SOURCE` | Runs the same validation phases, then reference-evaluates the Core for exactly one source. It prints one normalized value line per typed `spec`, in source order. |

The S3a semantic surface is intentionally narrow. It recognizes same-kind
declaration-name uniqueness and closed typed declarations of the form
`spec NAME() -> TYPE { SIGNED_INTEGER }`. The only supported types are exact
`Int` and exact `Word[8]`. Empty `spec` and `impl` declarations remain valid,
but they have no type, value, or execution meaning and do not enter the Core.

For `check`, status `0` with empty standard output and standard error means that
all required phases succeeded, including Typed Reference Core construction. A
source diagnostic uses status `1` and standard error. A CLI usage mistake uses
status `2`. Successful `eval` output has this exact shape:

```text
module::name: Type = value
```

`Int` values are normalized decimal integers. `Word[8]` values use `0x` plus
exactly two lowercase hexadecimal digits. An accepted source whose Core has no
typed functions makes `eval` write zero bytes.

These observations are not general execution or compilation. S3a defines no
operators, parameters, calls, bindings, control flow, typed `impl` values,
proof checking, verified lowering, canonical Core encoding, refinement
relation, code generation, native artifact, target, ABI, leakage guarantee,
cryptographic construction, release behavior, or production-readiness claim.
Calling `eval` a reference evaluation of closed literals keeps that boundary
visible.

## Worked example

Run from the Orange School repository root. `ORANGE_REPO` names a local Git
object store containing the exact commit; the common layout uses the sibling
path `../orange`.

```bash
export ORANGE_REPO="${ORANGE_REPO:-../orange}"
ORANGE_REV="ee0fa66d3d38af5e8e10adaa67555b1f0cebc6f6"

test -d "$ORANGE_REPO/.git"
actual_revision="$(git -C "$ORANGE_REPO" rev-parse "${ORANGE_REV}^{commit}")"
printf 'expected revision: %s\nactual revision:   %s\n' \
  "$ORANGE_REV" "$actual_revision"
test "$actual_revision" = "$ORANGE_REV"
```

If the exact object is absent, stop and ask the course operator to provision
it. Do not fetch into, check out, reset, clean, or otherwise rewrite a shared
Orange repository.

Create a fresh archive snapshot from that immutable Git object. The extraction
and Cargo build write only beneath the new temporary directory, not into
`ORANGE_REPO`:

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
rustup run 1.96.1 rustc --version
```

The toolchain file must name channel `1.96.1` with the `clippy` and `rustfmt`
components and the minimal profile. Define a helper that selects that toolchain
and uses Cargo's locked, offline mode:

```bash
orange_cli() {
  cargo +1.96.1 run --quiet --locked --offline \
    --manifest-path "$ORANGE_SNAPSHOT/compiler/Cargo.toml" \
    -p orangec -- "$@"
}
```

First check the catalog example and record the silent result:

```bash
example="$(pwd -P)/curriculum/modules/org-101/examples/minimal.or"
orange_cli check "$example"
printf 'check status: %s\n' "$?"
```

The compiler writes nothing and the status is `0`. The supported conclusion is
that this exact implementation accepted `minimal.or` through lexing, parsing,
bounded semantic validation, and construction of its empty Typed Reference
Core.

Now observe the implemented value surface using the pinned fixture:

```bash
orange_cli eval "$ORANGE_SNAPSHOT/compiler/fixtures/typed-answer.or"
printf 'eval status: %s\n' "$?"
```

Expected compiler output:

```text
demo::answer: Int = 42
demo::negative: Int = -42
demo::mask: Word[8] = 0xff
```

The status is `0` and standard error is empty. This is deterministic reference
evaluation of three closed literal values; it is not execution of a general
Orange program, proof checking, or code generation.

## Check your understanding

1. Why does archiving a full commit object give stronger input identity than
   running from an arbitrary checkout state?
2. What phases does silent status `0` from `orangec check` establish at this
   revision?
3. How do `lex`, `check`, and `eval` differ?
4. Why can successful `eval` of an empty Core produce no output?
5. Name six properties that neither the successful check nor reference
   evaluation establishes.
6. Which exit statuses distinguish accepted source, rejected source, and a
   command-line usage error?

## Next step

In `org-102` you will inspect the token stream, predict byte spans, and connect
lexical failures to stable `ORCxxxx` diagnostic codes.

## Sources

All Orange facts in this lesson are pinned to revision
`ee0fa66d3d38af5e8e10adaa67555b1f0cebc6f6`:

- [Compiler status and CLI contract](https://github.com/chasebryan/orange/blob/ee0fa66d3d38af5e8e10adaa67555b1f0cebc6f6/compiler/README.md)
- [Accepted typed-literal semantics](https://github.com/chasebryan/orange/blob/ee0fa66d3d38af5e8e10adaa67555b1f0cebc6f6/docs/SEMANTICS_2026.md)
- [Orange 2026 lexical and grammar specification](https://github.com/chasebryan/orange/blob/ee0fa66d3d38af5e8e10adaa67555b1f0cebc6f6/docs/LANGUAGE_2026.md)
- [OEP-0003 accepted S3a boundary](https://github.com/chasebryan/orange/blob/ee0fa66d3d38af5e8e10adaa67555b1f0cebc6f6/docs/governance/oeps/OEP-0003-orange-2026-typed-literals.md)
- [`orangec` CLI conformance tests](https://github.com/chasebryan/orange/blob/ee0fa66d3d38af5e8e10adaa67555b1f0cebc6f6/compiler/crates/orangec/tests/cli.rs)
- [`rust-toolchain.toml`](https://github.com/chasebryan/orange/blob/ee0fa66d3d38af5e8e10adaa67555b1f0cebc6f6/rust-toolchain.toml)
- [Release and licensing status](https://github.com/chasebryan/orange/blob/ee0fa66d3d38af5e8e10adaa67555b1f0cebc6f6/RELEASE_POLICY.md)
