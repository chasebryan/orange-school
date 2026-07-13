# Lab: bounded leakage evidence for public fixtures

## Goal

Audit a deliberately leaky comparator and a fixed-scan source control without
promoting either to a security primitive. Build exact C17 artifacts in a fresh
temporary tree, inspect what local tools can show, analyze bounded synthetic
samples, and produce a claim ledger whose negative conclusions retain their
scope.

All bytes and sample values in this lab are public course fixtures. Do not use
credentials, cryptographic keys, tokens, personal data, production artifacts,
or another process's memory. Do not change machine-wide performance, affinity,
power, mitigation, or kernel settings.

## Setup

From the repository root, run the unchanged gate:

~~~sh
PYTHONDONTWRITEBYTECODE=1 python3 curriculum/modules/sys-105/checks/lab_smoke.py
~~~

It must print <code>sys-105 lab smoke: PASS</code> and exit 0. The result means
only that the public teaching fixtures, temporary C17 build, optional
inspection, and deterministic analysis checks passed in this environment.

Create a fresh workspace and copy inputs rather than editing the module:

~~~sh
workdir="$(mktemp -d)"
mkdir -- "$workdir/src" "$workdir/build-o0" "$workdir/build-o2" \
  "$workdir/evidence" "$workdir/tmp"
cp -- curriculum/modules/sys-105/examples/compare.h \
  curriculum/modules/sys-105/examples/compare.c \
  curriculum/modules/sys-105/examples/harness.c \
  curriculum/modules/sys-105/examples/leakage_evidence.py "$workdir/src/"
cd -- "$workdir"
pwd
~~~

Keep every copied source, object, executable, assembly file, raw sample,
analysis result, command log, and report below this directory. Set
<code>TMPDIR</code> to its <code>tmp</code> directory and prevent Python cache
files. Record paths or absence before using tools:

~~~sh
for tool in cc python3 nm objdump readelf; do
  if tool_path="$(command -v "$tool")"; then
    printf '%s\t%s\n' "$tool" "$tool_path"
  else
    printf '%s\t%s\n' "$tool" unavailable
  fi
done > evidence/capabilities.txt
~~~

The C17 compiler and Python are required. Object inspectors are optional. A
missing inspector produces a recorded evidence gap; it does not authorize an
installation or an invented observation.

## Tasks

1. **Specify the model — SYS-105-01.** Write <code>leakage-model.md</code>.
   Identify the exact two functions and planned artifacts; classify length,
   contents, equality result, compiler/target, class label, and work counter as
   public, sensitive-model, declassified, or analyst-only. State an adversary
   with clock and repetition capabilities, the observed channels, chosen-input
   capability, maximum repetitions, allowed observation, and excluded physical
   channels. Define the input equivalence classes before inspecting results.
2. **Preserve source identity.** Record absolute workspace, repository state,
   SHA-256 of all four copied files, C compiler identity, Python identity,
   target information exposed by the compiler, environment fields relevant to
   reproduction, and exact commands. Confirm that every byte and class is
   synthetic and public even though the model labels a field
   “sensitive-model.”
3. **Build two exact artifacts — SYS-105-02.** Compile copied C with
   <code>-std=c17 -Wall -Wextra -Wpedantic -Werror</code> at
   <code>-O0</code> and <code>-O2</code>. Keep objects and executables in their
   separate build directories. Generate assembly for <code>compare.c</code> at
   each level. Hash every source, object, executable, and assembly file. Do not
   use link-time optimization unless your model and evidence plan explicitly
   add a third artifact.
4. **Preserve deterministic leak/control evidence.** Run both executables.
   Retain stdout, stderr, and immediate status. Explain why one versus 32
   explicit iterations is positive evidence of an early-exit source path, why
   32 versus 32 is evidence about explicit source work, and why neither counter
   is an unmodified timing observation. Confirm the oversized-length rejection
   leaves output unchanged. Do not execute null, dangling, misaligned,
   undersized, or overlapping pointers.
5. **Inspect exact artifacts — SYS-105-02.** If <code>nm</code> is available,
   record the two comparator symbols in each object. If <code>objdump</code> can
   decode the target, disassemble both objects; otherwise try a supported
   <code>readelf</code> view and record the limitation. Annotate content-dependent
   exits, loop-control branches, loads, stores, calls, and vectorized regions
   that are actually present. Compare <code>-O0</code> with <code>-O2</code> and
   separate observed artifact facts from C language guarantees. State the
   uninspected linker, loader, speculation, cache, firmware, and physical
   obligations.
6. **Analyze calibrated synthetic evidence — SYS-105-03.** Import the copied
   <code>leakage_evidence.py</code> with bytecode disabled. For the null control,
   deliberate 40-unit shift, and 10-unit acquisition-drift classes, preserve
   sample counts, both means, raw mean difference, standard error, and Welch
   statistic. Explain why the deliberate shift is a positive-control signal,
   why the null is a pipeline check, and why the drift signal must not be
   attributed to the candidate.
7. **Predeclare a dudect-style candidate experiment — SYS-105-03.** Before
   collecting any additional samples, write the exact fixed-versus-random or
   two-fixed-class construction, public length, random balanced acquisition
   order, warm-up, sample count capped at 4,096 per class, clock, process and
   cache-state policy, finite sample-magnitude cap of 1,000,000,000 in the
   declared unit, target artifact, effect/statistic fields, stop rule,
   exclusion rule, raw format, positive and null controls, and interpretation.
   List scheduler, interrupts, frequency, thermals, address layout, cache
   history, virtualization, and timer overhead as possible confounders. Do not
   change privileged or machine-wide settings for this lab.
8. **Account for repeated tests.** Declare whether offsets, lengths,
   optimization levels, interim looks, or partitions form one family. Keep the
   family to at most 64 tests. Record family alpha and the Bonferroni planning
   value from the helper. Explain why adjustment arithmetic cannot fix
   autocorrelation, data-dependent exclusions, adaptive hypothesis selection,
   or a broken acquisition order.
9. **Write bounded conclusions — SYS-105-04.** Create
   <code>claim-ledger.md</code> with separate rows for model, source review,
   work counts, each compiled artifact, optional inspection, synthetic
   statistics, and any locally acquired timing samples. For each row state the
   observed fact, supported claim, unsupported claim, assumptions, and next
   evidence. Preserve at least these conclusions: deliberate early-exit
   evidence detected; the synthetic null produced no detected mean difference;
   synthetic drift can mimic a signal; fixed-scan source and assembly review do
   not prove constant-time behavior; and no Orange implementation was tested.

## Verification

Run the baseline smoke check once more from the repository root and retain its
stdout, stderr, and status. Independently verify:

- all work and generated artifacts remain below the recorded temporary path;
- the two executables came from separate <code>-O0</code> and <code>-O2</code>
  commands and their hashes are associated with the right evidence;
- the leaky prefix/suffix work counts remain 1 and 32, while both fixed-scan
  mismatch counts remain 32;
- every optional inspection claim names the tool, options, artifact hash, and
  target or records that inspection was unavailable;
- every sample group contains 2 through 4,096 finite values of magnitude at
  most 1,000,000,000 and the analysis
  reports effects as well as statistics;
- the multiple-test family contains 1 through 64 tests and was declared before
  candidate interpretation;
- positive, null, drift, and candidate evidence are not relabeled after seeing
  results; and
- no statement claims constant-time execution, absence of all leakage,
  cryptographic security, cross-target behavior, or Orange behavior.

Preserve any mismatch, failed control, unexpected artifact, or analysis
rejection before repairing it. A green rerun does not replace the first failed
evidence.

## Reflection

1. Which part of your model most strongly limits the conclusion?
2. What changed between the <code>-O0</code> and <code>-O2</code> artifacts,
   and which changes matter to the declared observer?
3. What minimum effect could 4,096 samples per class plausibly detect in the
   observed noise, and how did you estimate it without converting it to proof?
4. How would contiguous class acquisition turn ordinary drift into a false
   candidate signal?
5. Which additional artifact, target, formal model, or physical experiment
   would most materially strengthen the result?
