# Assessment: Orange 2026 lexical model

## Instructions

Answer from the canonical Orange 2026 lexical rules, then verify only the
independent task with the exact archived-revision setup from `lab.md`. Preserve
your predictions before recording observed output. The pass threshold is 80%
and every critical criterion in `rubric.md` must pass.

## Knowledge check

1. **ORG-102-01:** Classify each item as identifier, reserved word, valid
   integer, valid string, comment/trivia, punctuation, or lexical error:
   `_x9`, `Proof`, `proof`, `0x2a`, `0b102`, `"a\x2A"`, `"a\q"`, a nested
   block comment, `::`, and U+00A0 non-breaking space. Give the stable lexical
   code for every error.
2. **ORG-102-02:** For the ASCII input `module M {}` followed by one line feed,
   write the complete expected token stream, including exact spellings,
   half-open byte spans, and `EOF`. Explain why no whitespace token appears.
3. **ORG-102-03:** Predict the stable code and reason for each rejection:
   unclosed `/*`, unclosed `"`, `"\u1234"`, `0x`, and `@`. Distinguish those
   lexer failures from invalid UTF-8 and an oversized input rejected before
   lexing.
4. For the source fragment `spec byte() -> Word[08] { -256 }`, list the token
   kinds for `->`, `[`, `08`, `]`, `-`, and `256`. Then separate three claims:
   what `lex` establishes, how the S3a parser uses those tokens, and which
   questions are left for semantic analysis. State why `-` is not a general
   unary operator.
5. Explain why `game`, `proof`, and `claim` have keyword tokens without current
   grammar or semantics, and why a successful token stream is not a syntax
   tree, accepted type, decoded value, Core, or evaluation result.

## Independent task

In your own assessment workspace, author two fresh inputs:

- a lexically valid token fixture containing an ASCII identifier, one reserved
  word with no parser role, a based integer with a legal separator, a valid
  escaped string, a nested block comment, a longest-match punctuation token,
  and the separate token spellings `->`, `[`, `]`, and `-`; and
- a lexically invalid fixture containing exactly one failure selected from
  `ORC0002` through `ORC0005`.

Before execution, submit the predicted token sequence, exact source spellings,
byte spans, exit status, and diagnostic code. Then run `orangec lex` through
the disposable archive helper at canonical revision
`ee0fa66d3d38af5e8e10adaa67555b1f0cebc6f6`. Run the valid case twice and
compare the complete outputs. Capture standard output, standard error, and
status separately for the invalid case so its retained tokens are not confused
with its diagnostic. Submit the source bytes or a hex dump, commands, both
runs, statuses, and a correction note for every prediction mismatch.

For one selected integer or punctuation token, add a three-column boundary
note: `lexer fact`, `parser role`, and `semantic question`. A correct note may
say, for example, that `08` is an `INTEGER` token, that the parser can retain it
as a type-width argument, and that semantic acceptance of the contextual type
is a separate question. Do not claim a parser or semantic result unless you ran
the appropriate command and label that evidence as a different phase.

Do not call either fixture a program merely because it lexes. `lex` is not
`check` or `eval`, and none of those commands is code generation or proof.

## Completion criteria

- **ORG-102-01** is complete when all lexical categories and reservations are
  classified according to Orange 2026, including ASCII-only identifiers,
  nested comments, and all four S3a-relevant punctuation kinds.
- **ORG-102-02** is complete when token names, escaped spellings, half-open byte
  spans, omitted trivia, zero-width `EOF`, retained tokens on failure, and
  repeatability are correctly demonstrated.
- **ORG-102-03** is complete when the invalid case is predicted before running,
  fails with the matching stable lexical code and status, and is distinguished
  from both pre-lexing input failures and later parser or semantic failures.
- Integer, `->`, `[`, `]`, and `-` are described with accurate lexer facts and
  bounded S3a parser or semantic roles; no value is attributed to tokenization.
- The result states that token output establishes no syntax, semantics,
  evaluation, Core, compilation, type, proof, or cryptographic property.
- The submission earns at least 80 points and passes all critical criteria.
