# Assessment: independent table-selection leakage audit

## Instructions

Complete this assessment independently in a new temporary directory. Do not
copy or rename the module comparator, harness, smoke check, synthetic samples,
or analysis implementation. You may use only public synthetic table entries,
selectors, and class labels. No production artifact or real secret is allowed.

Implement and audit two bounded C17 table-selection candidates: a deliberate
direct-index baseline and a full-scan source candidate. Build at two
optimization levels, inspect exact artifacts when local tools support it, and
run a predeclared calibrated timing experiment. A pass is an evidence-quality
result, not a finding that the full-scan candidate is constant-time.

This assessment covers:

- **SYS-105-01:** explicit leakage/adversary model and secret/public/
  declassification classification;
- **SYS-105-02:** source discipline plus target/compiler/artifact inspection;
- **SYS-105-03:** calibrated measurement, effects, Welch-style evidence,
  confounders, and multiple-testing limits; and
- **SYS-105-04:** evidence-ranked conclusions and precise non-claims.

## Knowledge check

1. Distinguish functional correctness, fixed-work source discipline,
   constant-instruction artifact evidence, empirical non-detection, and formal
   noninterference.
2. Define sensitive, public, declassified, and analyst-only values for one
   concrete operation. Explain why the categories are protocol-specific.
3. Name a control-flow, address, cache, branch-predictor, scheduler, and
   physical observation channel.
4. Explain how an optimizer, library substitution, link-time optimization, or
   undefined behavior can invalidate a source-only leakage argument.
5. State what disassembly can reveal and at least five relevant facts it cannot
   prove.
6. Derive the Welch statistic from class counts, means, and sample variances.
   Explain why its value is not the effect size.
7. Explain how drift, autocorrelation, class imbalance, adaptive stopping, and
   outlier removal can each mislead an experiment.
8. Explain why testing many offsets, lengths, targets, or interim sample counts
   changes the false-positive analysis.
9. Describe positive and null controls, including the correct response when
   either behaves unexpectedly.
10. Write the strongest justified sentence after a candidate experiment finds
    no difference at its current sensitivity.

## Independent task

1. **Model and classify — SYS-105-01.** Define an operation over a public table
   of exactly 32 <code>uint32_t</code> values and a selector from 0 through 31.
   The selector is a synthetic public integer used to model a sensitive class;
   the selected result is explicitly declassified. State exact source,
   compiler, flags, target, linker, executable, runtime, clock, co-location,
   repetitions, chosen-input ability, and observable channels. Define which
   selector pairs should be indistinguishable before building or measuring.
2. Implement <code>direct_select</code>, which deliberately reads
   <code>table[selector]</code>, and <code>full_scan_select</code>, which reads
   all 32 entries in order and combines the selected value without a
   selector-dependent source branch or address. Both accept a fixed-size table,
   selector, and output pointer; reject invalid selector or pointer before table
   access, including null table and null output; leave output unchanged on
   every failure where an output object exists; allocate nothing; make no I/O;
   and return bounded status codes. Label the direct version an address-leaky
   positive baseline and the scan version a source-discipline candidate, not a
   constant-time implementation.
3. Test every selector and both invalid classes against an independent
   reference result. Confirm exact output and unchanged output on failure. Add
   explicit source-level counters in a separate instrumented build showing one
   table read for the direct baseline and 32 reads for the scan candidate.
   A negative test may pass a null table or null output because the function
   must reject it before dereference. Never fabricate or pass a dangling,
   misaligned, undersized, or illegally overlapping non-null table: portable C
   cannot validate those arbitrary pointer defects after they are introduced.
4. **Build and inspect — SYS-105-02.** Build separate clean artifacts with a
   C17 compiler, warnings denied, and <code>-O0</code> and <code>-O2</code>.
   Hash sources, objects, assembly, and executables. Record compiler identity,
   full commands, target, and linker inputs. Capability-detect
   <code>nm</code>, <code>objdump</code>, and <code>readelf</code>; use supported
   tools to annotate the selected load addresses, loop/control branches, calls,
   vectorization, and differences between artifacts. Do not infer an
   unsupported instruction's timing from its mnemonic.
5. Create a standalone bounded analysis program that accepts two immutable
   finite sample arrays of 2 through 4,096 values each and returns class counts,
   means, raw mean difference, sample variances, standard error, and Welch
   statistic. Reject booleans, non-numeric and non-finite data, out-of-bound
   counts, absolute magnitudes above 1,000,000,000, and the zero-standard-error
   case. Write at least 12 tests including
   unequal class sizes/variances and invalid endpoints. This implementation
   must be independent of the module helper.
6. **Predeclare acquisition — SYS-105-03.** Before timing, freeze an experiment
   record containing the exact <code>-O2</code> artifact hash, clock and unit,
   two selector classes, randomized balanced acquisition schedule, warm-up,
   cache-state policy, 1,024 samples per class, rejection policy, process and
   machine state, effect/statistic fields, fixed final look, and raw record
   schema with sequence number. Use a documented monotonic local clock. If the
   platform lacks one appropriate to the declared model, record the blocker
   rather than silently substituting a different clock.
7. Run three separately labeled, public-only experiments: a deliberate
   positive control with an added bounded class-dependent workload; a null
   control with identical work distributions; and the uninstrumented scan
   candidate for the predeclared selector classes. Consume each result so the
   intended operation is not dead. Keep raw acquisition order and all samples.
   The positive delay is calibration only and must not be described as the
   candidate's leakage magnitude.
8. Record sample counts, means, raw mean difference in clock units, standard
   error, Welch statistic, acquisition-order summaries, and control outcomes.
   Discuss timer overhead, scheduler events, frequency, temperature, cache
   history, branch history, address layout, virtualization, simultaneous work,
   and autocorrelation. If the positive control is not detected or the null
   control signals under the predeclared rule, mark the candidate run
   uninterpretable and preserve it.
9. Declare every tested selector pair, optimization level, input partition,
   statistic, and interim look as one multiple-test family. Use at most 32
   planned tests and record both family alpha and a conservative per-test
   planning threshold. If you explored additional partitions, label them
   exploratory and obtain fresh samples before presenting confirmation.
10. **Calibrate the conclusion — SYS-105-04.** Submit a claim ledger separating
    model, source, correctness, work-count, each exact artifact, disassembly,
    controls, timing effects, and statistics. Preserve a deliberate direct-index
    source/artifact finding, positive and null control outcomes, the candidate
    outcome, and any disagreement. Explicitly state that source review,
    assembly inspection, work counters, and timing samples are evidence but not
    proof. Reject claims of universal constant time, cryptographic security,
    non-leakage on another artifact/target, physical-channel resistance,
    certification, or Orange behavior.
11. Submit one replay manifest with absolute temporary path, repository state,
    source/artifact hashes, tools and versions, target, environment, commands,
    stdout, stderr, immediate statuses, raw-sample digests, analysis output,
    predeclared plan, and claim ledger. All generated content must remain below
    the temporary directory, and the complete replay must require no external
    service.

## Completion criteria

Use the [rubric](rubric.md). Passing requires at least 80/100 and every critical
criterion. The submission must:

- define a complete observer and classification contract for **SYS-105-01**;
- demonstrate correct bounded source discipline and exact target artifact
  reasoning for **SYS-105-02**;
- preserve calibrated, randomized, effect-reporting, failure-sensitive
  statistical evidence for **SYS-105-03**;
- constrain every conclusion to the actual evidence for **SYS-105-04**; and
- use only synthetic public fixtures in a temporary, offline workspace.

A large statistic alone, a green functional test, branchless-looking source,
clean disassembly, or a non-detection cannot pass as a constant-time claim.
