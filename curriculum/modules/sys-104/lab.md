# Lab: capability-gated vector addition

## Goal

Build the portable reference examples, specify two exact artifact tuples,
model four-lane wrapping addition, and produce a capability matrix whose build,
link, run, inspection, and dispatch claims are independently evidenced.

## Setup

From the repository root:

~~~sh
cd curriculum/modules/sys-104
PYTHONDONTWRITEBYTECODE=1 python3 checks/lab_smoke.py
~~~

The command must print <code>sys-104 lab smoke: PASS</code> and exit 0. It
places every generated file under a fresh temporary directory and deletes that
directory on exit. It does not execute optional SIMD instructions.

Create your own fresh workspace with <code>mktemp -d</code>. Copy the three
example sources there before changing them. Keep source, objects, executables,
hashes, tool output, and status files under that workspace. Use no network,
package installation, administrator access, persistent cache, or unsupported
target execution.

## Tasks

1. **Record the native artifact tuple — SYS-104-01.** Capture the absolute
   workspace; Python, C compiler, and <code>rustc +1.96.1 -vV</code> identities;
   C compiler target when supported; <code>rustc --print cfg</code>; flags; and
   source hashes. Write separate fields for compiler target, ISA baseline, ABI,
   OS, object format, endianness, pointer width, and required CPU features.
   Mark every field as a documented guarantee, compiler configuration, artifact
   observation, runtime observation, or still-unverified assumption.
2. **Explain the tuple boundaries — SYS-104-01.** For the native row and one
   selected non-host target, explain why ISA, ABI, OS, and object format cannot
   be substituted for one another. Explain why target-triple components are not
   safely recovered by naive hyphen splitting. Show how the same ISA can have
   multiple OS/ABI/object-format combinations. State that C17 defines none of
   ELF, PE/COFF, Mach-O, a universal pointer width, or a universal byte order.
3. **Trace SIMD semantics — SYS-104-02.** For 128-bit values, enumerate the
   lane counts for 8-, 16-, 32-, and 64-bit lane types. Trace four wrapping
   <code>u32</code> additions including zero, <code>UINT32_MAX</code>, and a
   carry that wraps one lane without affecting its neighbor. Contrast wrapping
   with signed saturation and floating-point addition. Specify alignment,
   in-bounds load, tail, aliasing, and reduction-order requirements.
4. **Implement a changed semantic model — SYS-104-02.** In Python, independently
   implement eight-lane wrapping <code>u16</code> addition. Require exact tuples,
   exact lane count, plain integers rather than Booleans, and values from 0
   through 65535. Test normal, zero, maximum, wrapping, wrong count, wrong type,
   and out-of-range inputs. Label it a semantic lane model that makes no SIMD
   code-generation claim.
5. **Extend the baseline — SYS-104-03.** Change the copied C17 program to add at
   most 64 <code>uint16_t</code> lanes. Preserve a valid zero-length call without
   dereference, reject null for nonzero input, reject the 65th lane, and use
   defined unsigned wrapping. Compile with C17 and warnings denied. Run normal,
   zero, exact-64, maximum, wrapping, null, and excessive-length cases.
6. **Write the dispatch truth table — SYS-104-03.** Define a feature-free
   baseline and one hypothetical <code>simd128</code> body requiring a named
   feature appropriate to your selected native architecture. Record 32-bit
   lanes separately from the 128-bit total vector width. Test all four
   combinations of “body built” and “feature observed.” The accelerated result
   is allowed only when both are true; every other cell selects baseline. Do
   not call a feature-specific intrinsic for this task. Explain how a real body
   would isolate its target-feature preconditions and how differential tests
   would compare it with baseline after safe detection.
7. **Build and inspect native artifacts — SYS-104-04.** Build and run the C
   baseline and Rust tests. Hash the resulting artifacts. Capability-detect
   <code>readelf</code>, <code>objdump</code>, or <code>file</code>, then inspect
   with the first usable tool. Preserve exact command, stdout, stderr, immediate
   status, inspector version, and artifact hash. Report object format and
   machine only as observations for those bytes.
8. **Produce cross-target evidence — SYS-104-04.** Query target names known to
   the exact Rust compiler and installed target components when that facility
   is available. Select one non-host target. Attempt a compile-only build; do
   not link unless its linker/sysroot is already present, and never execute the
   result on the host. Preserve the exact target, command, stdout, stderr, and
   status. Success establishes only object emission. Failure establishes the
   observed missing capability; do not download around it or claim a cross
   artifact exists.
9. **Complete the capability matrix — SYS-104-04.** Include native and non-host
   rows with separate columns for target recognized, target library present,
   compile, link, inspect, authorized runner, run, build-time features, runtime
   detection, and dispatch. Use “not attempted” rather than implying a pass
   from an earlier column. Give one next action for each unsupported cell.
10. **Prove failure sensitivity.** Preserve three deliberate failures and their
    restorations: change one expected lane-wrap result, claim accelerated
    dispatch when the runtime feature is absent, and inspect a text source as
    though it were the native executable. Each wrong case must produce a
    nonzero test or explicit assertion status. Restore it and preserve the
    passing rerun. No invalid CPU instruction is part of the failure test.

## Verification

Your lab is complete only when:

- C17 and exact Rust 1.96.1 native builds pass with warnings denied;
- positive, zero, maximum, wrapping, invalid, and exact-bound cases are tested;
- no optional instruction is executed without a built body and positive runtime
  detection, and this lab executes no optional body at all;
- lane width, lane type, arithmetic, load extent, alignment, tail, and reduction
  semantics are separately stated;
- the native artifact tuple has evidence for every asserted field;
- cross-target recognition, compile, link, and run states remain separate;
- source and artifact hashes bind the evidence to exact bytes;
- every deliberate error is observed before restoration; and
- all created files and command outputs remain inside the temporary workspace.

## Reflection

Write six to eight sentences answering: Which tuple field was easiest to
over-infer? What does build-time <code>cfg</code> know that runtime detection
does not, and vice versa? Why are four 32-bit lanes not interchangeable with
eight 16-bit lanes? What protects the baseline from an unsupported-instruction
path? What did the cross-target attempt prove and not prove? Which artifact
fact came from inspection rather than the language? What would need to change
before one target row could be called deployable?
