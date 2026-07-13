# Lab: predict and inspect Orange tokens

## Goal

Predict token kinds, exact source spellings, half-open byte spans, and one
lexical failure before comparing the predictions with deterministic `orangec
lex` output. Demonstrate that S3a-looking tokens remain only tokens until later
phases run.

## Setup

Work from the Orange School repository root. Create and build a disposable
archive of the canonical Orange revision. This requires the exact commit object
to exist in `ORANGE_REPO`, but it does not require that checkout to be on a
particular branch and does not write into it.

```bash
export ORANGE_REPO="${ORANGE_REPO:-../orange}"
ORANGE_REV="ee0fa66d3d38af5e8e10adaa67555b1f0cebc6f6"
ORANGE_SCHOOL="$(pwd -P)"

test "$(git -C "$ORANGE_REPO" rev-parse "$ORANGE_REV^{commit}")" = \
  "$ORANGE_REV"
rustup run 1.96.1 rustc --version

ORANGE_SNAPSHOT="$(mktemp -d)"
git -C "$ORANGE_REPO" archive "$ORANGE_REV" -- \
  compiler rust-toolchain.toml | tar -x -C "$ORANGE_SNAPSHOT"
cargo +1.96.1 build --quiet --locked --offline \
  --manifest-path "$ORANGE_SNAPSHOT/compiler/Cargo.toml" \
  -p orangec
ORANGEC="$ORANGE_SNAPSHOT/compiler/target/debug/orangec"
test -x "$ORANGEC"

orange_cli() {
  "$ORANGEC" "$@"
}
```

Stop on a revision-object mismatch or missing toolchain. Do not substitute a
checkout, reset, clean, or build in the Orange source repository. Remove the
disposable snapshot after preserving the required evidence.

## Tasks

1. Read `curriculum/modules/org-102/examples/tokens.or` without running the
   compiler. Make a prediction table with columns for spelling, class, token
   name, start byte, and end byte. Include the zero-width `EOF` token. Mark
   whitespace and both levels of the nested comment as trivia.

2. Run the lexer and compare every row:

   ```bash
   tokens="$ORANGE_SCHOOL/curriculum/modules/org-102/examples/tokens.or"
   orange_cli lex "$tokens"
   printf 'lex status: %s\n' "$?"
   ```

3. Check repeatability without writing into either repository:

   ```bash
   first="$(orange_cli lex "$tokens")"
   first_status="$?"
   second="$(orange_cli lex "$tokens")"
   second_status="$?"
   test "$first" = "$second"
   test "$first_status" -eq "$second_status"
   printf '%s\n' "$first"
   ```

4. Before running it, predict standard output, the diagnostic code on standard
   error, and exit status for `unexpected-character.or`. Then observe each
   channel separately:

   ```bash
   invalid="$ORANGE_SCHOOL/curriculum/modules/org-102/examples/unexpected-character.or"
   invalid_stdout="$(mktemp)"
   invalid_stderr="$(mktemp)"
   orange_cli lex "$invalid" >"$invalid_stdout" 2>"$invalid_stderr"
   invalid_status="$?"
   cat "$invalid_stdout"
   cat "$invalid_stderr" >&2
   grep -F 'error[ORC0001]' "$invalid_stderr"
   test "$(cat "$invalid_stdout")" = $'2..2\tEOF\t""'
   test "$invalid_status" -eq 1
   ```

5. Predict these standard-input cases, then test them. The first line consists
   entirely of valid tokens. The second contains one malformed integer.

   ```bash
   printf '%s\n' '0b10_01 0X2a "ok\n" &&' | orange_cli lex -
   printf '%s\n' '0b102' | orange_cli lex -
   printf 'last status: %s\n' "$?"
   ```

   Explain why the first input's success does not mean it matches the source
   grammar. Confirm that the second still emits its retained `EOF` token while
   reporting `ORC0005` and status `1`.

6. Predict the token stream for this complete source before lexing it:

   ```bash
   typed='edition 2026; module boundary { spec byte() -> Word[8] { -0 } }'
   printf '%s\n' "$typed" | orange_cli lex -
   printf 'lex status: %s\n' "$?"
   ```

   Identify `INTEGER`, `ARROW`, `LEFT_BRACKET`, `RIGHT_BRACKET`, and `MINUS` in
   the output. Explain their phase-specific roles: the lexer only recognizes
   them; the parser may use them in the S3a typed-`spec` production; semantic
   analysis decides whether the type and signed value are supported. `-` is not
   a general unary operator.

7. Run the same bytes through `check` only to expose that phase boundary:

   ```bash
   typed_stdout="$(mktemp)"
   typed_stderr="$(mktemp)"
   printf '%s\n' "$typed" | \
     orange_cli check - >"$typed_stdout" 2>"$typed_stderr"
   typed_status="$?"
   test ! -s "$typed_stdout"
   grep -F 'error[ORC0206]' "$typed_stderr"
   test "$typed_status" -eq 1
   ```

   `lex` succeeded because every byte formed a valid token. `check` reached
   semantic analysis and rejected the minus sign on `Word[8]`, including
   negative zero. Do not call `ORC0206` a lexer diagnostic, and do not treat the
   earlier token stream as syntax or semantic acceptance.

## Verification

Your lab evidence must show:

- the exact canonical revision object, Rust toolchain, and disposable archive;
- a prediction and observed output for every token in `tokens.or`;
- trivia omitted, exact source spellings retained, and `EOF` at `90..90`;
- byte-identical repeated token output and identical exit status;
- `ORC0001`, retained `EOF`, and status `1` for the catalog invalid example;
- `ORC0005` for the malformed binary integer;
- the exact S3a tokens `INTEGER`, `ARROW`, both bracket tokens, and `MINUS`;
- a correct separation between lexical success and the later `ORC0206`
  semantic failure; and
- a statement that token output is neither syntax, semantics, evaluation,
  compilation, proof checking, nor cryptographic verification.

## Reflection

Choose one recognized spelling whose role depends on a later phase: `claim`,
an integer, `->`, `[`, `]`, or `-`. State what the lexer knows, what the S3a
parser may know, and what only semantic analysis may know. Avoid attributing a
value or operator meaning to the token itself.
