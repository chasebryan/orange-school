# Assessment: portable image-row dispatch

## Instructions

Complete this transfer assessment independently in a fresh temporary workspace.
Do not import, copy, rename, or lightly translate the module examples or lab
solution. Use Python 3.11 or newer, C17, and Rust 1.96.1 edition 2024 with no
external packages. Keep every created source, artifact, output, status, hash,
and evidence record inside the workspace. No network access or unsupported
target execution is permitted.

The scenario is an image-row transform with a scalar baseline and a future
accelerated implementation. The operation adds two equal-length rows of
unsigned 8-bit samples with **saturating** semantics, clamping each result at
255. Each row has 0 through 4,096 samples.

This assessment covers:

- **SYS-104-01:** exact target and artifact tuples;
- **SYS-104-02:** vector lane and operation semantics;
- **SYS-104-03:** safe baseline and accelerated dispatch; and
- **SYS-104-04:** capability, cross-build, inspection, and reproducibility
  evidence.

## Knowledge check

1. Distinguish target triple, ISA, ABI, OS, and object format. Give two artifact
   tuples that share an ISA but differ on another axis.
2. Explain why neither a target name nor <code>rustc --print target-list</code>
   proves that an artifact can be linked and run.
3. Explain what <code>target_endian</code>, <code>target_pointer_width</code>,
   and <code>target_feature</code> say at build time. Contrast them with runtime
   feature detection.
4. For a 256-bit vector, derive lane counts for u8, u16, u32, and u64. Explain
   why the operation must specify type and saturating semantics in addition to
   vector width.
5. Specify safe handling for a 4,095-byte row with a 32-byte vector width.
   Address bounds, alignment, full chunks, and the 31-byte tail.
6. Explain why reassociating floating-point reduction can change results even
   when elementwise integer saturation in this task is independent per lane.
7. State the safe entry condition for an accelerated body. Explain why
   executing first and handling failure later is not a valid detector.
8. Separate what a compiler target configuration, object inspector, successful
   link, and successful run each establish.

## Independent task

1. **Artifact model — SYS-104-01.** Implement immutable Python values for an
   artifact tuple, build manifest, and implementation requirements. The tuple
   has exact nonempty compiler target, ISA, ABI, OS, object format, endianness,
   pointer width, and compiler identity fields. Reject Boolean widths, unknown
   endian labels, mutable feature collections, duplicate implementation names,
   missing baseline, and a baseline requiring an optional feature.
2. **Evidence classification — SYS-104-01.** Produce the complete tuple for the
   native C and Rust artifacts. For every field name its source: language
   guarantee, official target/ABI documentation, compiler configuration,
   artifact inspection, runtime observation, or assumption. Capture exact
   compiler versions, targets, cfg output, flags, and source hashes. Do not
   infer object format from OS or ABI from architecture alone.
3. **Lane model — SYS-104-02.** Implement an independent Python semantic model
   for 16 u8 lanes of saturating addition. Inputs are exact 16-element tuples
   of plain integers from 0 through 255. Test zeros, ordinary sums, exactly 255,
   clamping above 255, all maximum lanes, wrong counts, Boolean, negative, 256,
   lists, and mixed invalid lanes. State that passing the model establishes no
   native SIMD code generation.
4. **C17 baseline — SYS-104-03.** Implement the row transform for two input
   pointers, one output pointer, and a <code>size_t</code> length. Accept a
   zero-length call without dereference. Reject null for nonzero length and
   reject 4,097 samples before access. Avoid unsigned intermediate wrap before
   clamping. Test 0, 1, 31, 32, 33, 4,095, and 4,096 samples; null positions;
   and the 4,097th sample. Deny compiler warnings.
5. **Rust dispatch policy — SYS-104-03.** Model <code>Baseline</code>,
   <code>Simd128</code>, and <code>Simd256</code>. Each variant records required
   build inclusion, runtime features, vector bytes, lane type, and saturation
   semantics. Select the largest-vector eligible variant only when it was built
   and all runtime requirements are positively observed; lane width remains a
   separate field. Reject a runtime artifact
   tuple different from the manifest. Always retain a feature-free baseline.
6. **Dispatch and tail tests — SYS-104-03.** Test baseline-only; detected but
   unbuilt; built but undetected; eligible 128; eligible 256; partial 256
   requirements; unknown extra runtime features; tuple mismatch; empty row;
   exact vector multiples; and 1-, 31-, and 4,095-byte tails. The simulated
   dispatcher may use the scalar C result or Python semantic chunks; it must
   never invoke a feature-specific instruction.
7. **Native artifacts — SYS-104-04.** Build and run the C baseline and Rust
   policy tests. Preserve source and artifact hashes, exact commands, stdout,
   stderr, immediate statuses, and target configuration. Capability-detect an
   object inspector, record its identity/version, and preserve machine/format
   output for at least the C artifact. Label those as observations.
8. **Cross-target row — SYS-104-04.** Select a non-host target known to the
   exact compiler. Record whether its target libraries, C sysroot/compiler,
   linker, inspector, and authorized runner are present. Attempt only a safe
   compile-only action supported by the detected capabilities. Preserve success
   or failure exactly. Do not execute the output and do not convert target
   recognition into a build, link, or run claim.
9. **Capability matrix — SYS-104-04.** Submit native and non-host rows with
   separate recognized, compile, link, inspect, run, baseline, optional body,
   runtime detector, and evidence-hash columns. Every supported cell links to
   evidence; every unsupported or unattempted cell gives a reason.
10. **Failure sensitivity and reproducibility.** Preserve nonzero evidence for
    four safe deliberate failures: expect wrapping rather than saturation for
    <code>250 + 10</code>; select Simd256 with one required feature missing;
    accept a mismatched artifact tuple; and assert the wrong inspected machine
    or format. Restore each expectation and preserve a full passing run. No
    deliberate failure may execute an unsupported instruction. State the
    O(n) time and O(n) output bound for <code>0 &lt;= n &lt;= 4096</code>, while
    noting that compiler, runtime, allocator, and artifact sizes are measured
    observations rather than fixed by the model.

## Completion criteria

Use [the rubric](rubric.md). Passing requires at least 80/100 and every critical
criterion. A passing submission must provide an exact native tuple, correct
saturating lane semantics, a bounded scalar implementation, fail-closed
dispatch, positive/endpoints/invalid tests, native build/run evidence, honest
cross-target evidence, an evidence-backed capability matrix, and all four
observed deliberate failures. The assessment establishes general systems
competence only; it makes no claim that Orange currently exposes SIMD,
target-feature dispatch, cross-compilation, an ABI, or professional deployment.
