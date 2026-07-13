# Orange 2026 grammar, diagnostics, and conformance

## Learning objectives

- **ORG-103-01:** Write the complete implemented Orange 2026 grammar at the
  pinned revision, including the additive typed-`spec` alternative.
- **ORG-103-02:** Create accepted and rejected source cases that distinguish
  lexical, syntactic, and S3a semantic boundaries.
- **ORG-103-03:** Explain why a recovered tree or successful parse establishes
  no semantic or cryptographic claim, while accurately scoping full `check`
  success.

## Prerequisites

Complete `org-102`. You should be able to classify every current token, predict
half-open byte spans, run `orangec lex`, and distinguish tokenization from a
token's later grammatical or semantic role.

## Lesson

At canonical revision `ee0fa66d3d38af5e8e10adaa67555b1f0cebc6f6`,
Orange 2026 has the following complete implemented grammar:

```text
source_file    = edition_decl module_decl EOF ;
edition_decl   = "edition" "2026" ";" ;
module_decl    = "module" IDENTIFIER "{" function_decl* "}" ;
function_decl  = "spec" IDENTIFIER "(" ")" spec_tail
               | "impl" IDENTIFIER "(" ")" empty_body ;
spec_tail      = empty_body
               | "->" parsed_type "{" signed_integer "}" ;
empty_body     = "{" "}" ;
parsed_type    = IDENTIFIER ("[" INTEGER "]")? ;
signed_integer = "-"? INTEGER ;
```

The edition declaration is mandatory and first. Its integer token must have
the exact decimal spelling `2026`; a prefix, separator, leading zero, or other
value is rejected even when a spelling could denote the same number elsewhere.
One source has exactly one module, whose body contains zero or more function
declarations in source order.

Both declaration kinds retain their legacy empty form. Only `spec` may instead
have one parsed result type followed by a body containing exactly one
optionally negative integer token:

```orange
edition 2026;
module demo {
  spec placeholder() {}
  impl placeholder() {}
  spec answer() -> Int { 42 }
  spec mask() -> Word[8] { 0xff }
}
```

The parameter list is always empty. There is no expression grammar hidden
inside the typed body. `-` is an optional literal sign, not a unary operator;
the magnitude is one integer token. A typed `impl`, parameter, operator,
second literal, semicolon inside a body, or nonempty statement body is a syntax
error.

### Syntax containers are not semantic acceptance

`parsed_type` deliberately accepts any identifier with either no bracketed
integer or one bracketed integer. Thus `Byte`, `Int[8]`, and `Word[08]` are
syntactically shaped types. Parsing does not make any of them supported types.
The separate S3a semantic rules accept only exact `Int` without a width and
exact `Word[8]` with the decimal width spelling `8`.

Likewise, a syntax-tree integer node retains its spelling, sign span, and
magnitude span; it is not yet a decoded value. Semantic analysis supplies
numeric interpretation, rejects a minus sign on `Word[8]`, enforces its
`0..255` range, and normalizes accepted values.

Duplicate names illustrate the same phase boundary. The parser creates a
function node for each declaration, so both same-kind and cross-kind
duplicates are syntactically valid. Semantic analysis then rejects a repeated
name inside the same declaration-kind namespace with `ORC0201`. A `spec` and an
`impl` with the same exact name use separate namespaces and pass this check;
they are not linked or callable.

### Deterministic parsing and recovery

The grammar is LL(1). A declaration begins with `spec` or `impl`; `}` ends the
declaration list; and `{` versus `->` chooses a `spec` tail. There is no
precedence, implicit semicolon, contextual keyword, or grammar ambiguity in
this slice.

The parser diagnostic families are:

| Code | Stable meaning |
| --- | --- |
| `ORC0101` | a required or allowed grammar token was not present |
| `ORC0102` | the source edition was not exactly `edition 2026;` |
| `ORC0103` | a module member did not begin with `spec` or `impl` |
| `ORC0104` | syntax followed the single allowed module |
| `ORC0105` | further ordinary syntax errors were suppressed |
| `ORC0106` | a parser resource budget was exhausted |

Parser work is bounded by 262,144 syntax nodes, 1,048,576 parser events, 100
ordinary diagnostics plus at most one suppression diagnostic, and recovery
delimiter depth 64. Recovery may skip to a bounded declaration or delimiter
boundary for diagnostic quality, but it must consume input or stop.

A recovered tree is never an accepted source. No recovery node or missing
token may appear in a successful parse. Repeated execution on identical bytes
and the same compiler revision must preserve token order, syntax-tree shape,
diagnostic order and codes, spans, and success or failure.

### `check` is a multi-phase command

The CLI does not expose a parser-only subcommand. At this revision,
`orangec check` runs these gates in order:

```text
bounded read -> lex -> parse -> semantic analysis -> Typed Reference Core
```

A lexical diagnostic prevents parsing. A parser diagnostic prevents semantic
analysis. A semantic diagnostic rejects the whole source and prevents an
accepted Core. Successful `check` is silent with status `0`; a source
diagnostic goes to standard error with status `1`; CLI usage errors use status
`2`.

Therefore a silent `check` now establishes lexical, syntactic, and the narrow
S3a semantic acceptance implemented at this exact revision, including
successful construction of its internal Typed Reference Core. It is wrong to
describe current `check` as parser-only.

It is equally wrong to overstate the result. S3a semantics cover only exact
declaration-kind uniqueness and closed `Int` or `Word[8]` specification
literals. `check` does not reference-evaluate output, execute an `impl`, check
a proof, establish refinement, generate code, validate cryptography, or prove
parser or semantic correctness. The Core is internal and noncanonical.

A semantic diagnostic is useful phase evidence. For example, `ORC0203` on
`spec x() -> Byte { 1 }` shows that the source crossed the lexical and
syntactic gates and reached the semantic type check. It still is not an
accepted program, and the public CLI exposes no accepted partial tree or Core.

### Conformance strategy

A useful grammar suite tries to falsify each production boundary. It includes:

- an empty module, both legacy empty declaration kinds, and typed `spec` cases;
- `{` and `->` alternatives after `spec`;
- generic parsed-type shapes that later fail semantics;
- typed-`impl`, parameter, nonliteral-body, and trailing-source rejection;
- reserved-word-as-name and reserved-declaration rejection;
- syntactic duplicate acceptance followed by same-kind semantic rejection;
- Unicode whitespace and identifier rejection;
- LF, CRLF, and bare-CR line endings;
- lexical and parser resource boundaries; and
- repeated diagnostic and result equality.

These are results from one identified implementation. They do not prove the
grammar complete, the parser correct, the semantic system sound, or another
implementation conformant.

## Worked example

After completing the archived setup in the lab, check the cross-kind case:

```bash
source="$(pwd -P)/curriculum/modules/org-103/examples/functions.or"
"$ORANGEC" check "$source"
printf 'status: %s\n' "$?"
```

The command is silent and returns `0`. `functions.or` contains an empty `spec`
and empty `impl` named `duplicate`. The parser admits both declarations, and
semantic analysis accepts their different namespace keys. This is not general
duplicate-name acceptance and creates no spec-to-impl relationship.

`reserved-declaration.or` uses valid tokens but fails with `ORC0103` because
`proof` cannot begin a module member. `trailing-syntax.or` fails with
`ORC0104` because a second module follows the one allowed module. Neither
source reaches semantic analysis.

For a phase contrast, put this fresh source in the disposable lab directory:

```orange
edition 2026;
module boundary {
  spec parsed_not_supported() -> Byte { 1 }
}
```

`check` returns `1` with `ORC0203`, not a parser diagnostic. Its type has the
shape required by `parsed_type`, then fails the narrower semantic gate.

## Check your understanding

1. Write all eight grammar productions without looking back. Which alternatives
   preserve the earlier empty declarations?
2. Why does `parsed_type` admit `Byte` and `Word[08]` while S3a rejects them?
3. Predict the phase and first code family for a missing edition semicolon,
   `proof p() {}`, `impl p() -> Int { 1 }`, `spec p() -> Byte { 1 }`, a second
   same-kind name, and a cross-kind same name.
4. Why is `-` in `signed_integer` not evidence of arithmetic expressions?
5. What does a recovered syntax tree establish? What does it never establish?
6. What is the strongest justified claim after silent `check` success at this
   revision? Name eight excluded claims.
7. Why can an `ORC0203` result support a phase-boundary observation without
   making the rejected source an accepted program?

## Next step

Complete the lab and assessment with predictions recorded before execution.
`org-201` then studies the narrow semantic and reference-evaluation behavior of
accepted closed typed specifications; do not read later Orange stages into
this grammar.

## Sources

All Orange facts in this lesson are pinned to canonical revision
`ee0fa66d3d38af5e8e10adaa67555b1f0cebc6f6`:

- [Normative Orange 2026 lexical and syntactic grammar](https://github.com/chasebryan/orange/blob/ee0fa66d3d38af5e8e10adaa67555b1f0cebc6f6/docs/LANGUAGE_2026.md)
- [Accepted S3a semantic phase boundary](https://github.com/chasebryan/orange/blob/ee0fa66d3d38af5e8e10adaa67555b1f0cebc6f6/docs/SEMANTICS_2026.md)
- [Compiler grammar and current CLI capability](https://github.com/chasebryan/orange/blob/ee0fa66d3d38af5e8e10adaa67555b1f0cebc6f6/compiler/README.md)
- [Bounded parser implementation](https://github.com/chasebryan/orange/blob/ee0fa66d3d38af5e8e10adaa67555b1f0cebc6f6/compiler/crates/orange-compiler/src/parser.rs)
- [Semantic phase implementation](https://github.com/chasebryan/orange/blob/ee0fa66d3d38af5e8e10adaa67555b1f0cebc6f6/compiler/crates/orange-compiler/src/semantics.rs)
- [CLI phase and diagnostic tests](https://github.com/chasebryan/orange/blob/ee0fa66d3d38af5e8e10adaa67555b1f0cebc6f6/compiler/crates/orangec/tests/cli.rs)
