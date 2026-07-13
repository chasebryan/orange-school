# Rubric: Orange 2026 lexical model

## Rubric

| Criterion | Objective | Points |
| --- | --- | ---: |
| Lexical classification and phase boundaries | ORG-102-01 | 30 |
| Token stream, byte spans, and repeatability | ORG-102-02 | 40 |
| Predicted rejection and stable lexical diagnostic | ORG-102-03 | 30 |
| **Total** |  | **100** |

## Critical criteria

All of the following are mandatory:

- Identifiers are ASCII-only, and `game`, `proof`, and `claim` are reservations
  without current grammar or semantics.
- Integers, `->`, `[`, `]`, and `-` are tokenized independently of their bounded
  S3a parser roles and later semantic checks. `-` is not presented as a general
  unary operator.
- `orangec lex` output is described only as retained tokens, exact spellings,
  and byte spans. It is not described as syntax, semantics, Core, evaluation,
  compilation, type checking, proof checking, or cryptographic verification.
- The valid fixture includes correct half-open UTF-8 byte spans and a
  zero-width `EOF`; character counts are not substituted for byte offsets.
- The independent invalid fixture fails with the predicted stable lexical code
  and status `1`, with token output and diagnostics kept in their correct
  output channels.
- Evidence comes from a disposable archive of exact canonical revision
  `ee0fa66d3d38af5e8e10adaa67555b1f0cebc6f6` through quoted paths.

## Scoring

- **27–30 classification points:** every category, reservation, escape, and
  requested phase distinction is accurate; **20–26:** one or two non-critical
  mistakes; **0–19:** the lexical model or lexer/parser/semantic boundary is
  materially incorrect.
- **36–40 token points:** predictions, observed names, spellings, spans, trivia,
  retained failure tokens, `EOF`, and repeated outputs all agree or are
  explicitly corrected; **28–35:** one non-critical omission; **0–27:** the
  token evidence cannot be reproduced.
- **27–30 diagnostic points:** the failure is isolated, predicted, matched to
  the correct lexical code and status, and distinguished from pre-lexing and
  later-phase failures; **20–26:** the result is correct but the prediction or
  phase explanation is incomplete; **0–19:** the code or phase is
  misidentified.

A passing result is at least **80/100** and satisfies every critical criterion.

## Feedback and retry

Feedback identifies the first incorrect category, byte boundary, phase claim,
or diagnostic prediction. A retry uses fresh valid and invalid fixtures that
exercise the same missed rule; it must preserve predictions before execution
and include a short correction explaining the earlier mismatch.
