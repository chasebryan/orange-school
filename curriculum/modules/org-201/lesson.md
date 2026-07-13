# Typed closed specifications and reference evaluation

## Learning objectives

- **ORG-201-01:** Distinguish the separate `spec` and `impl` declaration
  namespaces, enforce same-kind name uniqueness, and avoid inventing a
  relationship between same-spelled declarations.
- **ORG-201-02:** Check closed typed specification literals against the exact
  contextual `Int` and `Word[8]` rules, including normalization, range, and
  stable semantic failures.
- **ORG-201-03:** Interpret the source-ordered, noncanonical Typed Reference
  Core and predict exact `orangec eval` values for accepted sources.
- **ORG-201-04:** Record pinned `check` and `eval` evidence without promoting it
  into unsupported language, proof, compilation, security, or release claims.

## Prerequisites

Complete `org-103`, `plt-102`, `mat-103`, and `prg-104`. This module begins
from the lexer and parser boundary, exact mathematical integers, bounded
machine words, and the distinction between an implementation result and a
language claim.

`org-103` described the complete grammar and phase boundary at this same pinned
revision. This module concentrates on the one narrow S3a semantic slice. Do not
read that slice as evidence for any later Orange stage.

## Lesson

Orange revision `ee0fa66d3d38af5e8e10adaa67555b1f0cebc6f6`
closes the merged evidence for accepted pre-alpha S3a semantics for closed
typed `spec` literals. `SEMANTICS_2026.md` is normative for this slice and
OEP-0003 is **Accepted**. That acceptance establishes bounded language
authority, not a supported Orange release, completion of S3, or a final
compatibility promise.

### The entire typed source addition

The only new function shape in scope is:

```text
function_decl = "spec" IDENTIFIER "(" ")" spec_tail
              | "impl" IDENTIFIER "(" ")" empty_body
spec_tail     = empty_body | "->" parsed_type "{" signed_integer "}"
parsed_type   = IDENTIFIER ("[" INTEGER "]")?
signed_integer = "-"? INTEGER
```

An empty `spec name() {}` and empty `impl name() {}` remain accepted but have
no type, value, or execution behavior. A typed declaration must be a `spec`,
must have no parameters, and must contain exactly one signed integer token in
braces. The parser deliberately accepts a broad type spelling so the semantic
phase can issue a stable type or width diagnostic. A typed `impl` is outside
the source grammar and fails during parsing; the internal `ORC0202` defense is
not the expected source-level result for that syntax.

Operators, parameters, names in value position, calls, bindings, statements,
control flow, conversions, inference, contracts, effects, and nonempty
implementations do not exist in this slice. A typed `spec` here is a closed
literal declaration, not a callable function or an executable implementation.

### Declaration identity

The semantic phase uses separate declaration namespaces keyed by
`(kind, exact ASCII name)`:

| Declarations in one module | Result |
| --- | --- |
| `spec item`, then `spec item` | `ORC0201` duplicate function |
| `impl item`, then `impl item` | `ORC0201` duplicate function |
| `spec item`, then `impl item` | accepted |
| `impl item`, then `spec item` | accepted |

Empty and typed specifications participate in the same `spec` namespace. An
empty declaration can therefore collide with a typed declaration of the same
kind. Exact spelling matters, and there is no overload set.

Acceptance of `spec shared` beside `impl shared` establishes only that their
namespaces are separate. S3a performs no linking, matching, conformance,
resolution, call, refinement, or execution between them.

### The two contextual types

Only exact `Int` without a width and exact `Word[8]` with the width spelling
`8` are supported:

| Source form | Accepted values | Normalized value |
| --- | --- | --- |
| `Int { INTEGER }` | any supported positive magnitude | mathematical integer |
| `Int { -INTEGER }` | any supported negative magnitude | mathematical integer; negative zero becomes `0` |
| `Word[8] { INTEGER }` | `0` through `255` | unsigned eight-bit value |
| `Word[8] { -INTEGER }` | none, including `-0` | `ORC0206` |

The integer token may use binary, decimal, or hexadecimal notation and digit
separators. The semantic value discards radix, spelling, and separators.
`Int { -0x0 }`, for example, denotes `0`. `Word[8] { 256 }` fails with
`ORC0207`; no wrapping, truncation, or coercion occurs.

`Word`, `Word[08]`, `Word[16]`, `Int[8]`, and arbitrary identifiers may parse
as types but are not supported contextual types. Unsupported type names use
`ORC0203`; an unsupported `Word` width uses `ORC0204`. Integer magnitudes are
also bounded to 16,384 significant bits before conversion. Crossing that
source representation limit uses `ORC0205`; it is not a bound on the
mathematical `Int` value domain.

The semantic diagnostic families in this slice are:

| Code | Stable meaning |
| --- | --- |
| `ORC0201` | duplicate name in one declaration-kind namespace |
| `ORC0202` | unsupported typed function reached an internal AST defense |
| `ORC0203` | unsupported contextual type |
| `ORC0204` | unsupported `Word` width |
| `ORC0205` | integer significant-bit budget exceeded |
| `ORC0206` | negative `Word[8]` literal, including `-0` |
| `ORC0207` | nonnegative `Word[8]` literal exceeds `255` |
| `ORC0208` | further ordinary semantic errors suppressed |
| `ORC0209` | semantic resource budget exhausted |
| `ORC0301` | evaluation resource budget exhausted |

### What `check` establishes

At this revision, `orangec check SOURCE` runs lexing, parsing, semantic
analysis, and construction of the internal Typed Reference Core. A silent
status `0` means all of those revision-specific acceptance gates succeeded.
It does not evaluate the values, emit code, run an implementation, or check a
proof.

Semantic analysis begins only after lexing and parsing have no diagnostics.
Any diagnostic rejects the source as a whole: no accepted partial AST, Core,
or value stream is exposed. Ordinary semantic diagnostics are capped at 100
plus one suppression diagnostic; semantic work, Core nodes, integer magnitude,
and evaluation steps also have fixed resource limits.

### Typed Reference Core and `eval`

The Typed Reference Core contains only accepted typed specifications. Empty
`spec` and `impl` declarations are absent. Typed specifications retain source
order and receive contiguous internal IDs `0..n-1` over those Core entries.
Each entry stores the exact module and declaration names, one of the two
supported types, and the normalized value.

This Core is an internal typed compiler boundary. It is explicitly
**noncanonical**. The commit defines no stable serialization, digest,
fingerprint, schema, theorem identity, refinement mapping, erasure mapping, or
cross-revision ID promise. Do not use it as proof or artifact identity.

`orangec eval SOURCE` accepts exactly one source path, or `-` for standard
input. It first applies the same gates as `check`, then prints one line per Core
entry in source order:

```text
module::name: Type = value
```

`Int` values print in normalized decimal. `Word[8]` values print as exactly two
lowercase hexadecimal digits after `0x`. An empty Core writes zero bytes. If
any earlier phase or evaluation fails, `eval` writes no partial value sequence
to standard output.

### Professional claim boundary

The strongest justified statement is narrow: recorded bytes were accepted or
rejected, with the recorded streams and status, by the recorded CLI built from
the exact revision. `eval` additionally demonstrates that implementation's
normalized, source-ordered reference values.

This evidence establishes no operators, parameters, calls, implementation
values, spec-to-impl relationship, inference, refinement, proof checking,
canonical Core, code generation, compilation correctness, target behavior,
constant-time property, cryptographic correctness, package compatibility, or
production support. Those exclusions are part of correct professional use,
not fine print.

## Worked example

After building the exact archived revision as shown in the lab, run the same
source through both commands:

```bash
accepted="$(pwd -P)/curriculum/modules/org-201/examples/typed-values.or"

"$ORANGEC" check "$accepted"
printf 'check status: %s\n' "$?"

"$ORANGEC" eval "$accepted"
printf 'eval status: %s\n' "$?"
```

`check` writes nothing and returns `0`. `eval` returns `0` and writes exactly:

```text
ledger::zero: Int = 0
ledger::debt: Int = -1024
ledger::low: Word[8] = 0x0a
ledger::high: Word[8] = 0xff
```

The empty `shared` declarations demonstrate separate kind namespaces but
produce no value lines. The empty `placeholder` implementation is also absent.
The typed specifications alone retain their interleaved source order.

Now evaluate `eval-no-partial.or`. Although `before` is valid, `too_large`
fails with `ORC0207`. Status is `1`, standard output is empty, and no line for
either `before` or `after` is exposed.

## Check your understanding

1. Why may `spec n() {}` and `impl n() {}` coexist while two `spec n`
   declarations fail? Does coexistence connect their behavior?
2. Predict `check` for `Int { -0b0 }`, `Word[8] { 0xff }`, `Word[8] { -0 }`,
   `Word[8] { 256 }`, `Word[08] { 1 }`, and `Byte { 1 }`.
3. Which declarations enter the Typed Reference Core, and how are their order
   and internal IDs chosen?
4. Predict the exact value lines for decimal `10`, hexadecimal `0a`, and
   binary `00001010` when each is a `Word[8]` literal.
5. What does silent `check` success establish at this revision that it did not
   establish at the `org-103` revision? What does it still not establish?
6. Why would calling the Core canonical or treating an ID as a theorem
   fingerprint be a material error?
7. Why must an `eval` diagnostic suppress values that precede the bad
   declaration in source order?

## Next step

Complete the lab and assessment using fresh source cases. Later Orange modules
may add richer semantic or proof obligations only after their own pinned
implementation gates; do not read those future stages backward into S3a.

## Sources

All Orange facts in this lesson are pinned to revision
`ee0fa66d3d38af5e8e10adaa67555b1f0cebc6f6`:

- [Normative accepted S3a semantics and nonclaims](https://github.com/chasebryan/orange/blob/ee0fa66d3d38af5e8e10adaa67555b1f0cebc6f6/docs/SEMANTICS_2026.md)
- [Orange 2026 grammar with the S3a typed delta](https://github.com/chasebryan/orange/blob/ee0fa66d3d38af5e8e10adaa67555b1f0cebc6f6/docs/LANGUAGE_2026.md)
- [Accepted OEP-0003 governance boundary](https://github.com/chasebryan/orange/blob/ee0fa66d3d38af5e8e10adaa67555b1f0cebc6f6/docs/governance/oeps/OEP-0003-orange-2026-typed-literals.md)
- [Compiler implementation boundary](https://github.com/chasebryan/orange/blob/ee0fa66d3d38af5e8e10adaa67555b1f0cebc6f6/compiler/README.md)
- [Semantic analyzer and Typed Reference Core construction](https://github.com/chasebryan/orange/blob/ee0fa66d3d38af5e8e10adaa67555b1f0cebc6f6/compiler/crates/orange-compiler/src/semantics.rs)
- [Reference evaluator](https://github.com/chasebryan/orange/blob/ee0fa66d3d38af5e8e10adaa67555b1f0cebc6f6/compiler/crates/orange-compiler/src/eval.rs)
- [Stable diagnostic definitions](https://github.com/chasebryan/orange/blob/ee0fa66d3d38af5e8e10adaa67555b1f0cebc6f6/compiler/crates/orange-compiler/src/diagnostic.rs)
- [CLI behavior tests](https://github.com/chasebryan/orange/blob/ee0fa66d3d38af5e8e10adaa67555b1f0cebc6f6/compiler/crates/orangec/tests/cli.rs)
