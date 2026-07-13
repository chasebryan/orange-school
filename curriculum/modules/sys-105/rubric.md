# Rubric: independent leakage evidence audit

## Rubric

The assessment is worth 100 points. A passing score is at least 80/100 and all
critical criteria must pass.

| Criterion | Points | Evidence required |
| --- | ---: | --- |
| Leakage model and classification | 20 | Exact operation/artifact scope, sensitive/public/declassified/analyst-only classification, adversary capabilities, observations, equivalence classes, repetition bound, and exclusions |
| Source, correctness, and artifacts | 25 | Bounded valid C17 candidates, complete tests, deterministic work-count contrast, separate optimized builds, hashes, target/tool identity, capability-aware inspection, and source/artifact distinction |
| Measurement and statistical design | 35 | Independent bounded analyzer, predeclared randomized acquisition, positive/null/candidate evidence, raw effects and Welch statistic, confounder analysis, multiple-test accounting, and failure-sensitive interpretation |
| Claim calibration and reproducibility | 20 | Evidence-layer ledger, deliberate and negative evidence preserved, exact replay manifest, temp-only public fixtures, explicit unsupported claims, and no Orange inference |
| **Total** | **100** |  |

## Critical criteria

All four critical criteria must pass:

1. **Model integrity:** earn at least 16/20. The assessor must be able to locate
   the exact artifact, adversary, sensitive-model selector, public table,
   declassified output, observations, equivalence classes, and repetition
   scope. Relabeling observed classes or treating synthetic data as real secret
   evidence fails this criterion.
2. **Implementation and artifact integrity:** earn at least 20/25. Both
   functions must be correct for all 32 selectors, reject invalid inputs before
   access, preserve output on error, and avoid undefined behavior. Source,
   objects, assembly, and executables must remain associated with their exact
   compiler/options/target and inspection evidence. Calling the scan source or
   artifact proven constant-time fails this criterion.
3. **Experiment integrity:** earn at least 28/35. Acquisition must be
   predeclared, bounded, balanced and randomized; raw order retained; effects
   and Welch evidence reported; positive and null controls interpreted; and
   all planned tests counted. A missed positive control, signaled null, changed
   stop rule, hidden rejection, or unrecorded exploratory test makes the
   candidate result uninterpretable and must be reported that way.
4. **Claim integrity:** earn at least 16/20. Every conclusion must identify its
   evidence layer and scope. The submission must state that source review,
   assembly inspection, counters, and samples are evidence rather than proof.
   Universal non-leakage, cryptographic security, cross-target, physical,
   certification, or Orange claims fail this criterion.

A total of 80/100 or more cannot compensate for a failed critical criterion.

## Scoring

- **Leakage model and classification (20):** 6 points for exact artifact and
  public/sensitive/declassified classifications; 6 for adversary access,
  observation channels, chosen inputs, and repetitions; 5 for predeclared
  equivalence classes and permitted output; and 3 for exclusions and model
  limitations.
- **Source, correctness, and artifacts (25):** 7 points for correct bounded
  APIs, validation, unchanged error output, and all-selector tests; 5 for
  separate deterministic counters and safe negative cases; 7 for clean
  <code>-O0</code>/<code>-O2</code> builds, target identity, and hashes; and 6
  for capability-aware annotated inspection plus compiler/linker/runtime
  limits.
- **Measurement and statistical design (35):** 7 points for the independent
  strict analyzer and tests; 8 for frozen artifact, balanced randomized
  schedule, clock, samples, raw schema, and fixed look; 7 for credible positive
  and null controls; 7 for candidate effects, Welch evidence, acquisition-order
  and confounder analysis; and 6 for a declared bounded test family and honest
  exploratory/confirmatory separation.
- **Claim calibration and reproducibility (20):** 7 points for a complete
  evidence-layer claim ledger; 5 for preserving adverse, control, negative, and
  disagreement evidence; 5 for a replayable temporary manifest with exact
  commands/channels/statuses/hashes; and 3 for explicit non-claims and
  public-only, offline, non-Orange scope.

## Feedback and retry

Feedback identifies the first missing classification, sensitive-dependent
source edge, invalid memory test, artifact/source mismatch, acquisition-order
error, control failure, statistical assumption break, uncounted test, or
overstated claim and maps it to **SYS-105-01**, **SYS-105-02**,
**SYS-105-03**, or **SYS-105-04**. Preserve the original source, artifact,
sample, output, and claim evidence before correcting it.

A retry uses an assessor-selected table width, selector pairing, optimization
option, and public control workload. It must build in a new temporary directory,
freeze a new artifact hash and experiment plan, acquire fresh randomized
samples, rerun positive/null/candidate analysis, and update the multiple-test
family and claim ledger. Rewording a conclusion without repairing its source,
artifact, acquisition, control, or analysis evidence is not a successful retry.
