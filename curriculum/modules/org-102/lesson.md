# Orange 2026 lexical model

## Learning objectives

- **ORG-102-01:** Classify Orange 2026 identifiers, reserved words, integers,
  strings, comments, punctuation, and whitespace.
- **ORG-102-02:** Use `orangec lex` to inspect deterministic tokens and byte
  spans.
- **ORG-102-03:** Predict a lexical rejection and identify its stable
  diagnostic code.

## Prerequisites

Complete `org-101`. Use only Orange revision
`ee0fa66d3d38af5e8e10adaa67555b1f0cebc6f6` with Rust `1.96.1`. The lab
creates a disposable archive of that revision, so it neither depends on the
Orange checkout's current branch nor writes build artifacts into the source
repository.

## Lesson

Lexing turns source bytes into a deterministic sequence of tokens. A token
records a kind, its exact source spelling, and a half-open UTF-8 byte span. The
lexer does **not** build the syntax tree, decide whether the tokens match the
grammar, resolve a type, decode a value, or evaluate anything.

Orange 2026 source is valid UTF-8 and is limited to 16 MiB per input. A token
span is `[start, end)`: `start` is included and `end` is the byte immediately
after the token. The required final `EOF` token is zero-width at the source byte
length. Diagnostic lines and columns are for humans; token spans remain
byte-based.

### Trivia

Only tab, line feed, carriage return, and ordinary space count as whitespace.
Other Unicode space characters are unexpected characters. `//` begins a line
comment. `/*` and `*/` delimit a block comment, and block comments may nest.
Whitespace and comments separate tokens but are not emitted as tokens.

### Names and reserved words

An identifier starts with an ASCII letter or `_`; later characters may also be
ASCII digits. Identifiers are exact, case-sensitive ASCII spellings. Unicode
letters do not extend an identifier.

These seven spellings are always reserved:

```text
edition  module  spec  impl  game  proof  claim
```

`edition`, `module`, `spec`, and `impl` have parser roles at the pinned S3a
boundary. `game`, `proof`, and `claim` receive keyword tokens but have no
grammar or semantics. Lexical reservation alone never creates a language
feature.

### Integers and strings

Integer tokens may be decimal, binary with `0b` or `0B`, or hexadecimal with
`0x` or `0X`. A base prefix requires at least one digit. An underscore is
allowed only as a single separator between two digits valid for that base.
Leading, trailing, doubled, or base-invalid digits make the complete integer
candidate malformed.

At S3a an `INTEGER` token can appear in three parser positions: the exact
decimal spelling `2026` in the edition declaration, the optional width in a
parsed type, or the magnitude in a typed `spec` body. Those positions do not
change how the lexer forms the token. Parsing preserves the spelling and
structure; only later semantic analysis decides whether a contextual type and
literal are supported and decodes a value. For example, `08`, `0x8`, and `256`
are all valid integer tokens even when a particular semantic context rejects
them.

A string is confined to one logical line and uses double quotes. Its supported
escapes are:

```text
\"  \\  \n  \r  \t  \0  \xNN
```

Each `N` in `\xNN` is one ASCII hexadecimal digit. An unsupported or
incomplete escape, a line ending before the closing quote, or end of input
before the closing quote is a lexical error. A valid string token still has no
current parser or runtime meaning.

### Punctuation and phase roles

The lexer recognizes the following punctuation, using longest matching where
two spellings share a prefix:

```text
(  )  {  }  [  ]  ,  :  ;  .  ..  ::
+  -  *  /  %  &  &&  |  ||  ^  ~  !
=  <  >  ==  !=  <=  >=  ->  =>  ?
```

The S3a parser grammar uses `(`, `)`, `{`, `}`, `[`, `]`, `;`, `-`, and `->`.
In the narrow typed-`spec` alternative, `->` introduces a parsed result type,
brackets enclose its optional integer width, and `-` may be the sign directly
before the one body integer. `-` is not a general unary operator. Every other
punctuation token above is lexically recognized without gaining syntax or
semantics. Even for punctuation that the parser does use, `orangec lex` reports
tokens only; it does not report that their arrangement is grammatical.

### Output and failures

Each `orangec lex` output line has three tab-separated fields:

```text
START..END    TOKEN_NAME    "escaped source spelling"
```

The lexical diagnostic families at the pinned revision are:

| Code | Stable meaning |
| --- | --- |
| `ORC0001` | unexpected character |
| `ORC0002` | unterminated block comment |
| `ORC0003` | unterminated string |
| `ORC0004` | invalid or incomplete string escape |
| `ORC0005` | malformed integer |
| `ORC0006` | non-trivia token limit exceeded |
| `ORC0007` | further ordinary lexical errors suppressed |

At most 262,144 non-trivia tokens are retained, not counting `EOF`. At most
100 ordinary lexical diagnostics are emitted, followed when needed by one
suppression diagnostic. Input failures such as invalid UTF-8 and a file beyond
16 MiB are rejected before lexing with CLI-level codes `ORC1002` and `ORC1003`.
A lexical error prevents parsing in `check` and `eval`.

The `lex` command still prints the retained token stream, including `EOF`, when
the lexer reports an error; diagnostics go to standard error and the process
exits with status `1`. A successful `lex` exits `0` with empty standard error.
Neither result is a parser, semantic, Core, evaluation, compilation, proof, or
cryptographic result. At this revision `orangec check` runs later parsing and
semantic phases, while `orangec eval` also evaluates the accepted reference
Core. Do not transfer claims from those commands to `lex`.

## Worked example

Complete the pinned snapshot setup in `lab.md`, which defines `orange_cli`, then
run:

```bash
orange_cli lex \
  "$(pwd -P)/curriculum/modules/org-102/examples/tokens.or"
```

The exact token output is:

```text
0..6	KW_MODULE	"module"
7..17	IDENTIFIER	"Identifier"
18..19	LEFT_BRACE	"{"
56..61	KW_CLAIM	"claim"
62..67	IDENTIFIER	"value"
68..69	EQUAL	"="
70..74	INTEGER	"0x2a"
74..75	SEMICOLON	";"
78..84	STRING	"\"ok\\n\""
85..87	DOT_DOT	".."
88..89	RIGHT_BRACE	"}"
90..90	EOF	""
```

The gap from byte 19 to byte 56 is whitespace plus a nested block comment.
`claim`, the string, `=`, and `..` are valid tokens even though this token
sequence is not an accepted Orange source file.

Now inspect the intentionally invalid example:

```bash
orange_cli lex \
  "$(pwd -P)/curriculum/modules/org-102/examples/unexpected-character.or"
printf 'exit status: %s\n' "$?"
```

Standard output contains only `2..2 EOF ""`. Standard error begins with
`error[ORC0001]: unexpected character '@'`, and the exit status is `1`. That
separation is important: token output is not an acceptance certificate.

## Check your understanding

1. Why can the byte offset of a token differ from the number of visible
   characters before it?
2. Classify `_round9`, `proof`, `0B10_01`, `0x_2a`, `"a\q"`, `/* a /* b */
   c */`, and a non-breaking space.
3. How can `Word[08]` and `Word[8]` both lex successfully while later semantic
   analysis treats them differently?
4. What token kinds does `-> Word[8] { -1 }` produce, and which facts about its
   grammar and meaning remain unknown after `lex`?
5. What is the difference between `ORC0005` and the pre-lexing code `ORC1002`?
6. What does a successful, repeatable `lex` result not establish?

## Next step

In `org-103` you will apply the complete S3a parser grammar and distinguish
accepted syntax from recovered syntax. Later semantic work decides which
parsed typed literals have meaning; this lexer module does not.

## Sources

All Orange facts in this lesson are pinned to canonical revision
`ee0fa66d3d38af5e8e10adaa67555b1f0cebc6f6`:

- [Normative Orange 2026 lexical and grammar specification](https://github.com/chasebryan/orange/blob/ee0fa66d3d38af5e8e10adaa67555b1f0cebc6f6/docs/LANGUAGE_2026.md)
- [Accepted S3a semantic phase boundary](https://github.com/chasebryan/orange/blob/ee0fa66d3d38af5e8e10adaa67555b1f0cebc6f6/docs/SEMANTICS_2026.md)
- [Compiler CLI and frozen lexical boundary](https://github.com/chasebryan/orange/blob/ee0fa66d3d38af5e8e10adaa67555b1f0cebc6f6/compiler/README.md)
- [Lexer implementation and unit tests](https://github.com/chasebryan/orange/blob/ee0fa66d3d38af5e8e10adaa67555b1f0cebc6f6/compiler/crates/orange-compiler/src/lexer.rs)
- [Stable diagnostic codes](https://github.com/chasebryan/orange/blob/ee0fa66d3d38af5e8e10adaa67555b1f0cebc6f6/compiler/crates/orange-compiler/src/diagnostic.rs)
- [`orangec lex` CLI behavior tests](https://github.com/chasebryan/orange/blob/ee0fa66d3d38af5e8e10adaa67555b1f0cebc6f6/compiler/crates/orangec/tests/cli.rs)
