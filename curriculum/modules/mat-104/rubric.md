# Rubric: exact dice model and collision evidence

## Rubric

The assessment is worth 100 points.

| Criterion | Points | Evidence required |
| --- | ---: | --- |
| Finite model, conditioning, and independence | 25 | Complete ordered space, precise event definitions, exact event/intersection counts, valid conditioning, and both product-equality decisions |
| Expectation and exact bounds | 30 | Exact expectation, union value and bound, tail value and Markov bound, collision formula and pair bound, reduced fractions, derivations, and inequality checks |
| Enumeration, simulation, and tests | 35 | Definition-driven exact code, input/event validation, declared bounds, complete tests, failure sensitivity, same-seed replay, estimate/error record, and non-cryptographic boundary |
| Reproducibility and evidence limits | 10 | Python/source identity, workspace, exact commands and channels, statuses, seed and trials, work bounds, and accurate sampling/model/implementation limits |
| **Total** | **100** |  |

## Critical criteria

All three critical criteria must pass:

1. **Model integrity:** earn at least 20/25. The 36 outcomes must be ordered,
   distinct, and equally likely under the stated model; events must match their
   definitions; conditioning must have a positive denominator; and
   independence must use exact intersection/product equality. An omitted or
   double-counted outcome fails this criterion.
2. **Exact-bound integrity:** earn at least 24/30. Expectation and every union,
   tail, and collision exact value must be correctly derived as a reduced
   rational, with each upper bound labeled and verified. A float substituted
   for required exact evidence or an upper bound below the exact probability
   fails this criterion.
3. **Simulation-evidence integrity:** earn at least 28/35. Enumeration and
   simulation bounds must be enforced, tests must detect a deliberately wrong
   expectation, same-seed replay must match, and the estimate must retain count,
   trials, seed, error, and limitations. Presenting Python
   <code>random</code> as cryptographically secure or a seeded replay as an
   independent sample fails this criterion.

A total of 80 or more cannot compensate for a failed critical criterion.

## Scoring

- **Finite model (25):** 6 for the complete ordered uniform space, 6 for exact
  event definitions and counts, 5 for conditional probability with denominator,
  and 8 for both independence decisions with intersection and product evidence.
- **Expectation and bounds (30):** 6 for expectation derivation, 7 for exact
  union and union bound, 7 for exact tail and Markov bound, 7 for collision
  exact value and pair bound, and 3 for reduced fractions and explicit
  inequality/looseness analysis.
- **Enumeration, simulation, and tests (35):** 8 for definition-driven exact
  enumeration, 6 for model and event validation, 6 for parameter/work bounds,
  6 for normal/boundary/invalid exact tests, 4 for deliberate failure and
  restoration, and 5 for seeded estimate, error, replay, and security boundary.
- **Reproducibility and limits (10):** 5 for environment, source, commands,
  channels, statuses, seed, and trials; 3 for readable model, source, and
  tests; and 2 for precise sampling, model, implementation, portability, and
  pseudorandom limits.

Pass only with at least 80/100 and all critical criteria.

## Feedback and retry

Feedback names the first sample-space error, unsupported independence claim,
incorrect fraction or bound, unenforced limit, or overstated simulation claim;
maps it to an outcome ID; and identifies the missing evidence. Preserve the
original work and append a correction record.

A retry uses a new assessor-selected bounded finite experiment, different
events, collision parameters, and seeds. Rerun every affected exact derivation,
boundary test, deliberate failure check, and simulation. A new estimate cannot
replace a wrong model, and revised prose cannot replace missing exact or
failure-sensitive executable evidence.
