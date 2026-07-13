# Leakage models and side-channel engineering

Functional correctness says which output a computation returns. A leakage
claim says what an observer may learn from everything else the computation
does: elapsed time, control flow, memory addresses, cache state, allocation,
errors, power, electromagnetic activity, or contention with another workload.
Those are different contracts. A function can return the right answer for
every input and still reveal a sensitive-dependent prefix length.

This module teaches a bounded evidence workflow. Its byte arrays, class labels,
and timing-like samples are synthetic and public. The supplied C17 routines are
teaching fixtures, not security primitives. One is deliberately leaky. The
other follows a simple fixed-scan source discipline, but neither this module nor
its smoke check calls that routine constant-time.

## Learning objectives

- **SYS-105-01:** Write an explicit leakage model that identifies the system,
  adversary, sensitive and public inputs, permitted declassification,
  observations, target, and claim scope.
- **SYS-105-02:** Apply source-level control-flow and memory-access discipline,
  then inspect exact compiled artifacts while accounting for compiler,
  optimizer, linker, runtime, and microarchitectural effects.
- **SYS-105-03:** Design a bounded leakage experiment with calibration
  controls, randomized acquisition, raw effect sizes, Welch-style statistics,
  confounder handling, and an explicit multiple-testing plan.
- **SYS-105-04:** Calibrate conclusions from source review, artifact
  inspection, tests, and timing samples, explaining why each is evidence rather
  than proof of non-leakage or constant-time behavior.

## Prerequisites

Pass <code>sys-104</code>, <code>cry-102</code>, and <code>mat-104</code>. You
should be able to identify an exact target and feature tuple, distinguish
source semantics from an optimized artifact, describe cryptographic threat
models without inventing assurance, and reason about probability, expectation,
variance, sampling, and tail evidence.

The reference envelope supplies a C17 compiler and Python 3.11 or newer. Object
inspectors such as <code>nm</code> and <code>objdump</code> are optional. The
smoke check detects them before use, builds copied inputs only below a fresh
temporary directory, and performs no download or package installation.

## Lesson

### Start with a leakage contract

“Constant time” is incomplete until its observer and equivalence classes are
defined. Write the contract before choosing a coding idiom or statistical test.
A useful model names:

1. the exact operation and artifact, including source identity, compiler,
   options, target, dependencies, loader, and relevant platform state;
2. the **sensitive variables** whose distinctions must be hidden;
3. the **public variables** whose distinctions may affect behavior;
4. any **declassified output**, such as success/failure or a public length;
5. the adversary's access, repetition budget, co-location, clock, cache or
   performance-counter access, chosen inputs, and ability to influence state;
6. the observable channel, such as process duration, branch history, accessed
   cache lines, addresses, page faults, allocation, or response shape; and
7. the claim: which sensitive-equivalent executions should have
   indistinguishable allowed observations, on which platform and for how long.

Use a classification table rather than intuition:

| Variable | Classification | Reason | Allowed influence |
| --- | --- | --- | --- |
| Buffer length | Public in this fixture | The caller already supplies it | Loop trip count and sequential extent |
| Buffer contents | Sensitive-model input | Models a value whose class should be hidden | Final equality result only |
| Equality result | Declassified | Required functional output | Returned after the scan |
| Compiler and target | Public configuration | Needed to reproduce the artifact | Code shape and instruction selection |
| Sample class label | Analyst-only metadata | Needed for the test | Analysis grouping, never the operation |

This table is not universal. In another protocol, length can be sensitive;
even an error bit can reveal too much; a remote adversary may have fewer
observations than a same-core adversary; and an attacker who chooses inputs can
amplify a difference that random tests rarely exercise.

One formal shape is to partition inputs by the public values and permitted
output. For sensitive values <code>s0</code> and <code>s1</code> in the same
partition and fixed public context <code>p</code>, compare the distributions of
observations <code>O(A, s0, p)</code> and <code>O(A, s1, p)</code> for adversary
<code>A</code>. Exact equality, computational indistinguishability, and “no
detected difference under experiment E” are three different claims. This
module's empirical work supports only the last form.

### Side channels arise below and beside the API

Common leakage paths include:

- **control flow:** a sensitive-dependent branch, early return, loop bound,
  exception, retry count, or dispatch path;
- **memory access:** a sensitive index, pointer chase, table lookup, page,
  cache-line footprint, TLB footprint, or prefetch pattern;
- **instruction selection:** a source operation lowered to instructions whose
  latency depends on operands on the selected processor;
- **resource behavior:** allocation size, page faults, locks, queueing,
  syscalls, I/O volume, error formatting, and scheduler interaction;
- **microarchitectural state:** caches, branch predictors, speculative
  execution, shared execution units, buffers, and simultaneous multithreading;
  and
- **physical channels:** power draw, electromagnetic emission, sound, and
  temperature, which require different equipment and models.

The categories interact. A sensitive branch can change which cache lines are
loaded. A branchless table lookup can still reveal a sensitive address. A
fixed source loop can be vectorized, replaced with a library call, or deleted
when its result is unused. Speculation can touch memory absent from the
architecturally completed path. Linux's Spectre documentation, for example,
describes how speculative side effects left in shared caches can become an
observation; ordinary source-level bounds checks do not fully describe that
channel.

### Source discipline removes obvious dependencies

For a declared sensitive value, review whether it influences:

- branch conditions, loop termination, recursion depth, or error paths;
- load/store addresses, table indices, object layout, or allocation size;
- instruction choice, variable shifts/division, foreign or library calls;
- locks, atomics, scheduler-visible work, syscalls, and message shape; or
- optimizer assumptions such as undefined behavior, aliasing, and dead values.

The [early-exit example](examples/compare.c) stops on the first unequal byte.
Its explicit iteration counter preserves evidence of the source-level leak:
with a public 32-byte fixture, a prefix mismatch produces one iteration while a
suffix mismatch produces 32. The counter is not a timer and adding it changes
the artifact. It provides deterministic structural evidence only.

The second routine scans every byte and accumulates differences with bitwise
operations. For fixed public length, the C source contains no
content-dependent loop exit and its explicit data access is sequential. Call
that **fixed-scan source discipline**, not “constant time.” The compiler can
still transform it, the selected instructions can have target-specific
behavior, caches and speculation remain, and the surrounding caller can leak.

Correctness and memory safety remain mandatory. Do not read past a buffer to
make work look uniform. Do not execute invalid pointers as negative tests. Do
not introduce signed overflow, uninitialized values, data races, or undefined
behavior. A leakage mitigation built on undefined behavior has no stable source
meaning for the optimizer to preserve.

### Inspect the artifact you will actually evaluate

The source file is not the executable. Record the complete pipeline:

~~~text
source + headers + compiler identity + flags + target
    -> assembly or object -> linker inputs/options -> executable or library
    -> loader/runtime/platform configuration -> executed process
~~~

Optimization level matters. GCC documents that optimization changes code size
and execution and that the enabled transformations depend on target and build
configuration. Whole-program and link-time optimization can use facts across
translation units. Rust's official <code>black_box</code> documentation is
equally explicit: it is best-effort benchmarking support and supplies no
cryptographic or constant-time guarantee.

For every candidate artifact:

1. preserve source hashes, compiler version, complete options, target, and
   dependency identity;
2. retain the object or executable hash before inspection;
3. capability-detect the disassembler or object inspector;
4. map source operations to relevant loads, branches, calls, and vectorized
   regions without assuming one mnemonic has universal timing; and
5. repeat after any compiler, option, source, dependency, target, or link
   change.

Assembly inspection can find a remaining early-exit branch, sensitive-indexed
load, or unexpected library call. It can also show that two builds differ. It
cannot establish all speculative behavior, cache state, operand-dependent
latency, firmware, interrupt behavior, or the observations of every adversary.
Absence of a suspicious mnemonic is therefore not proof.

### Timing acquisition is an experiment

A timing file without an acquisition protocol is hard to interpret. Specify in
advance:

- exact artifact, machine, clock source, sample unit, class construction, and
  sample count;
- which variable changes between classes and which variables are held fixed;
- randomized or balanced class order so class does not equal time-of-run;
- warm-up, cache-state, affinity, frequency, power, and simultaneous-workload
  policy;
- rejection rules decided before seeing results;
- raw-sample retention with sequence number and class label; and
- the effect, statistic, decision rule, repeated looks, and number of tests.

Temperature, frequency scaling, scheduler preemption, interrupts, address
layout, cache history, allocator state, background work, virtualization, and
measurement overhead can all create or hide differences. The supplied
synthetic fixture includes a “drift” pair: its two groups differ only because
one models earlier acquisition and one later acquisition. A large statistic on
that pair is a confounder demonstration, not leakage evidence.

Randomly interleave classes, preserve acquisition order, and plot or summarize
measurements by time as well as class. Repeat across fresh processes and
machines when the claim needs that scope. Never silently drop inconvenient
outliers. If a rejection rule is necessary, define it from independent
engineering constraints, retain both raw and filtered results, and report how
the conclusion changes.

### Report an effect before a statistic

For class samples <code>x</code> and <code>y</code>, first report counts,
means, robust summaries as appropriate, and the raw mean difference in the
measurement unit. A test statistic is not an effect size.

The bounded helper computes the Welch statistic:

~~~text
                 mean(x) - mean(y)
t = ------------------------------------------------
    sqrt(sample_variance(x)/n_x + sample_variance(y)/n_y)
~~~

It accepts 2 through 4,096 finite numeric values per class and rejects absolute
sample magnitudes above 1,000,000,000 before summation or squaring. That is an
engineering bound for predictable course execution, not a statistical
normalization rule; a real experiment must record its unit and choose a bound
appropriate to the acquisition device.

Welch's construction does not assume equal class variances. It still relies on
an experiment whose samples can support the intended inference. Autocorrelation,
drift, mixtures, heavy tails, adaptive stopping, class imbalance, measurement
resolution, and selection after looking at the data can make a simple
interpretation unsound. The helper deliberately does not turn <code>t</code>
into a universal pass/fail claim.

A dudect-style test repeatedly compares measurement classes and watches Welch
statistics. It is valuable for finding input-dependent execution in a concrete
build. The dudect paper describes this as assessment, not proof. A large
absolute statistic in a calibrated experiment is evidence of a distributional
difference worth investigating. A small statistic means the experiment did not
detect a difference of the exercised kind at its present sensitivity. It does
not prove the distributions equal.

Report practical magnitude as well as statistical evidence. With enough
samples, a tiny difference can produce a large statistic; with noisy or sparse
samples, a consequential difference can remain undetected. Include the raw
mean difference, standard error, sample counts, units, and an application-level
leakage relevance analysis.

### Repeated tests consume the error budget

Testing many offsets, lengths, targets, compiler variants, input partitions,
statistics, or interim sample sizes creates multiple opportunities for an
apparently surprising result. Declare the **family** of tests before examining
the results. The module helper can compute a Bonferroni per-test planning alpha
as <code>family_alpha / test_count</code>, but that arithmetic does not repair
dependent samples, poor acquisition, or an unjustified model.

If exploratory work tries many partitions, label it exploratory and confirm a
selected hypothesis with a new, independently acquired data set. Repeatedly
peeking at a statistic and stopping when it crosses a convenient threshold is
not a predeclared fixed-sample test. A threshold copied from another tool or
paper is not automatically calibrated for a new platform or experiment.

### Controls make negative conclusions interpretable

Use at least three evidence classes:

1. a **positive control** with an intentional, bounded, public-label effect
   that the acquisition and analysis must detect;
2. a **null control** constructed to have no intended class effect, which
   should not repeatedly trigger the decision procedure; and
3. the **candidate** under the real leakage model.

The positive control answers whether the pipeline can see a known effect in
this environment. The null control can expose drift, class-order bugs, or an
inflated false-positive procedure. Neither calibrates every possible leakage
shape. A deliberate delay much larger than the candidate's effect shows only
that the pipeline detects that large delay.

Preserve controls even when they undermine a desired conclusion. If the
positive control is missed, the experiment is insensitive or broken. If the
null control signals, investigate acquisition and analysis before interpreting
the candidate. If the candidate does not signal in a well-calibrated run, say:

> No difference was detected for the declared classes, artifact, platform,
> sample count, and analysis sensitivity.

Do not shorten that to “constant-time,” “secure,” or “no side channel.”

### Evidence forms complement rather than replace each other

| Evidence | Can support | Cannot prove by itself |
| --- | --- | --- |
| Leakage/threat model | Reviewable scope and allowed observations | That implementation matches the model |
| Source review | Absence/presence of obvious source dependencies | Optimized artifact or microarchitecture behavior |
| Assembly/object inspection | Properties of one exact compiled artifact | Every runtime state, target, or adversary |
| Functional and work-count tests | Correct outputs and exercised structural paths | Timing distribution or physical leakage |
| Timing samples | Detected or undetected effects in one experiment | Universal non-leakage or future builds |
| Formal proof in an explicit machine model | Property within assumptions and model | Effects omitted from assumptions/model |

Professional engineering combines these layers, records disagreements, and
uses the weakest justified conclusion. A clean source review plus no detected
timing difference is stronger evidence than either alone, but it remains
bounded by artifact, model, platform, sample construction, and sensitivity.

## Worked example

Run the deterministic evidence gate from the repository root:

~~~sh
PYTHONDONTWRITEBYTECODE=1 python3 curriculum/modules/sys-105/checks/lab_smoke.py
~~~

It must print exactly:

~~~text
sys-105 lab smoke: PASS
~~~

The check copies four source files into a temporary directory. It builds the C
fixture with warnings denied, observes one versus 32 iterations for the
deliberately leaky prefix/suffix cases, observes 32 iterations for both
fixed-scan cases, checks failure leaves the output unchanged, generates
<code>-O0</code> and <code>-O2</code> assembly, and uses optional symbol/object
inspectors only when present.

The Python fixture contains public synthetic samples. Its null control has zero
mean difference and zero Welch statistic. Its deliberate class has a known
40-unit shift. Its drift class has a known 10-unit acquisition-order shift to
demonstrate a false interpretation. These facts test the analysis code; they
are not measurements of the C executable and do not establish a security
property.

## Check your understanding

1. Why can a content-independent loop count still coexist with a cache side
   channel?
2. Give one setting where message length is public and one where it is
   sensitive.
3. What claim does a one-iteration versus 32-iteration counter support? What
   timing claim does it not support?
4. Why must the exact optimized artifact be inspected after a source review?
5. How can acquisition drift produce a large Welch statistic with no
   candidate-dependent leak?
6. Why is a raw mean difference necessary even when an absolute statistic is
   large?
7. What changes when 20 partitions are tested instead of one?
8. What is the correct conclusion when a positive control is not detected?
9. Why can neither assembly inspection nor timing samples prove universal
   constant-time behavior?
10. Name the exact artifact and platform fields needed to reproduce a negative
    leakage result.

## Next step

Complete the lab with the supplied public fixtures, then perform the independent
table-selection assessment. Preserve the first source/artifact discrepancy,
positive-control miss, null-control signal, or candidate signal before changing
anything. Later Orange work may adopt this evidence discipline only after the
Orange compiler, native artifact, target, and timing surface exist; this module
establishes no Orange constant-time behavior.

## Sources

- Reparaz, Balasch, and Verbauwhede,
  [“Dude, is my code constant time?”](https://eprint.iacr.org/2016/1123.pdf),
  the primary dudect research paper introducing a Welch-test-based empirical
  assessment workflow and its limits.
- Kocher,
  [“Timing Attacks on Implementations of Diffie-Hellman, RSA, DSS, and Other Systems”](https://paulkocher.com/doc/TimingAttacks.pdf),
  primary research showing that execution-time observations can expose secret
  information.
- Bernstein,
  [“Cache-timing attacks on AES”](https://cr.yp.to/antiforgery/cachetiming-20050414.pdf),
  primary research on cache-mediated timing leakage.
- Linux kernel documentation,
  [Linux 6.12 Spectre side channels](https://www.kernel.org/doc/html/v6.12/admin-guide/hw-vuln/spectre.html),
  official platform documentation on branch prediction, speculative execution,
  caches, and attack contexts.
- GNU Compiler Collection,
  [GCC 16.1 options that control optimization](https://gcc.gnu.org/onlinedocs/gcc-16.1.0/gcc/Optimize-Options.html),
  official documentation for optimization- and target-dependent compiler
  transformations.
- Rust standard library,
  [Rust 1.96.1 <code>std::hint::black_box</code>](https://doc.rust-lang.org/1.96.1/std/hint/fn.black_box.html),
  official documentation distinguishing best-effort benchmarking barriers from
  cryptographic guarantees.
