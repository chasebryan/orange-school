# Rubric: finite beacon games and conditional reduction audit

## Rubric

The assessment is worth 100 points. Passing requires at least 80/100 and every
critical criterion.

| Criterion | Points | Evidence required |
| --- | ---: | --- |
| Game, adversary, and advantage definition | 25 | Complete Games 0/1/2, probability spaces, interface and aborts, transcript/win/baseline/convention, quantifiers, finite adversaries, and resource bounds |
| Game hops, reduction, and assumptions | 25 | Coupled adjacent hops, named bad event and game, complete reduction algorithm, correct inequality direction, abort/guess losses, resource transformation, and conditional scope |
| Exact model, boundaries, and failure sensitivity | 30 | Independent Fraction enumerator, all strategies and slot sizes, exact endpoints/one beyond, relational properties, mutation failure/restoration, and deterministic evidence |
| Concrete, sampled, and reproducible claim discipline | 20 | Exact term ledger and vacuity analysis, pre-registered seeded sample, hashes/commands/channels/statuses, evidence categories, and explicit non-claims |
| **Total** | **100** |  |

## Critical criteria

All four critical criteria must pass:

1. **Game-definition integrity:** earn at least 20/25. Every coin,
   distribution, interface, query rule, transcript, win event, baseline,
   advantage convention, quantifier, adversary-domain rule, and resource bound
   must agree in prose and code. An ambiguous probability space, skipped
   invalid query, or omitted abort fails this criterion.
2. **Hop and reduction integrity:** earn at least 20/25. The Game 0/1 coupling,
   bad event, probability reference, and transition inequality must be valid;
   the Game 1/2 step must be conditional on the exact assumption; and the
   reduction must simulate every interface, translate success in the useful
   direction, and account for aborts, guessing, time, memory, queries, and
   data. A reversed or circular reduction fails this criterion.
3. **Exact and failure-sensitive evidence:** earn at least 24/30. The
   independent exact-rational enumerator must cover every declared strategy and
   <code>m=1..32</code>, reject 0 and 33, pass the ideal/hop/symmetry/monotonic
   relations, and preserve an observed mutant failure followed by restoration.
   Sampling or a hard-coded expected table cannot replace enumeration.
4. **Claim-boundary integrity:** earn at least 16/20. Concrete terms must retain
   formulas, exact values, assumptions, resource conversions, probability
   caps, and vacuity labels; the sample must be pre-registered and empirical;
   and conclusions must explicitly exclude general cryptographic proof,
   implementation/deployment evidence, side-channel claims, and Orange claims.

A total of 80/100 or more cannot compensate for a failed critical criterion.

## Scoring

- **Game, adversary, and advantage definition (25):** 7 for executable
  pseudocode and complete randomness; 6 for interface, state, transcript,
  validation, abort, and win event; 5 for baseline, convention, quantifiers,
  and randomized-mixture qualification; and 7 for exact adversary, slot, time,
  memory, probe, and enumeration bounds shared by prose and code.
- **Game hops, reduction, and assumptions (25):** 7 for the coupled Game 0/1
  transition and correct bad-event bound; 5 for the exact conditional Game 1/2
  replacement; 8 for complete reduction construction, output relation,
  direction, abort and guessing accounting; and 5 for runtime, memory, query,
  data, tightness, and assumption scope.
- **Exact model, boundaries, and failure sensitivity (30):** 9 for independent
  exact rational enumeration and deterministic output; 7 for every strategy,
  slot size, trial count, and endpoint/one-beyond result; 8 for ideal,
  identical-until-bad, complement, and monotonic relations; and 6 for malformed
  inputs plus preserved mutant failure and restored pass.
- **Concrete, sampled, and reproducible claim discipline (20):** 7 for exact
  concrete term accounting, caps, parameter cases, resource transformation,
  and vacuity; 5 for the pre-registered bounded single-seed run and exact/sample
  separation; and 8 for file identities, commands, channels, immediate
  statuses, evidence classification, limitations, and reproducible replay.

## Feedback and retry

Feedback names the first missing coin, distribution, query rule, transcript
field, win predicate, convention, quantifier, adversary strategy, endpoint,
coupling, bad event, reduction direction, abort/loss term, resource conversion,
model relation, mutation record, sample-plan field, or unsupported claim and
maps it to **FRM-104-01**, **FRM-104-02**, or **FRM-104-03**. Preserve the
original submission and append a correction record before retrying.

A retry changes the game to two ordered probes without replacement, changes
the slot range to an assessor-selected endpoint no greater than 24, changes the
win event and baseline, supplies a different conditional assumption and
resource transformation, and uses new sample parameters. Recompute the
strategy class, probability space, hop events, reduction, concrete bounds,
endpoints, relational properties, mutation failure, and sample plan. Rewording
an unsupported claim or copying the first result table is not a successful
retry.
