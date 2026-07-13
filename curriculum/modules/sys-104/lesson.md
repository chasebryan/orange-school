# Targets, SIMD, and feature dispatch

Source code is not the deployable unit. A compiler produces an artifact for a
particular target, with a particular instruction-set baseline, ABI, operating
environment, object format, byte order, pointer width, and feature policy. A
program that runs on the build machine proves only that one observed artifact
ran in that environment. Professional systems work records the complete tuple,
keeps a safe baseline, and enters accelerated code only after both the build
and the running machine establish its preconditions.

This module uses a C17 scalar baseline, a Rust 1.96.1 dispatch model, and a
Python 3.11 metadata model. The examples never execute an optional instruction.
They make the dispatch invariant testable even on hosts without SIMD support.

## Learning objectives

- **SYS-104-01:** Specify an artifact tuple that distinguishes target triple,
  ISA, ABI, operating system, object format, endianness, and pointer width, and
  separate language guarantees from build and inspection observations.
- **SYS-104-02:** Explain SIMD lane width, lane type, per-lane semantics,
  alignment, tails, and reductions without inferring semantics from vector
  width or assuming that source notation guarantees vector instructions.
- **SYS-104-03:** Design a baseline-plus-accelerated dispatch policy that
  requires an included implementation and runtime capability evidence before
  entry, and that never executes an unsupported instruction.
- **SYS-104-04:** Build and inspect reproducible native and cross-target
  evidence, maintain a capability matrix, and scope every conclusion to the
  exact compiler, flags, target, and artifact hash observed.

## Prerequisites

Pass <code>sys-101</code> and <code>sys-103</code>. You should be able to reason
about fixed-width values, byte order, C translation units, Rust/C ABI
boundaries, object files, links, and target-scoped layout evidence.

The reference envelope provides a C17 compiler, Python 3.11 or newer, and
<code>rustc +1.96.1</code>. Object inspectors and non-host target libraries are
optional capabilities. A missing optional tool or cross-target library must be
recorded honestly; it must not be replaced by downloading during the lab.

## Lesson

### A target name selects output; it is not the whole contract

Rust and LLVM commonly identify targets with names shaped like
<code>architecture-vendor-system-environment</code>, for example
<code>x86_64-unknown-linux-gnu</code>. Components are sometimes omitted,
<code>unknown</code>, or historically named. Treat the full name as an opaque,
versioned compiler input first and a mnemonic second. Parsing its hyphens is
not authoritative evidence for an ABI or object format.

An **artifact tuple** for this course records at least:

| Field | Question answered | Example observation |
| --- | --- | --- |
| Compiler target | Which compiler target specification selected output? | <code>x86_64-unknown-linux-gnu</code> |
| ISA baseline | Which instruction family may ordinary generated code require? | x86-64 baseline |
| ABI | How do independently compiled artifacts call and lay out shared values? | target System V C ABI |
| Operating environment | Which loader, system interface, and runtime environment are expected? | Linux |
| Object format | How are headers, sections, symbols, and relocations encoded? | ELF |
| Endianness | In what byte order are multi-byte scalar objects represented for this target? | little-endian |
| Pointer width | How many bits does the selected target use for a data pointer in this model? | 64 |
| Required CPU features | Which optional capabilities may the artifact execute without dispatch? | none beyond baseline |

The values in the example column are not universal properties of all machines
with one matching word. A target specification, compiler documentation, ABI
document, and artifact inspection support different parts of the claim.

### ISA, ABI, operating system, and object format are different axes

An **instruction set architecture** defines machine instructions and their
architectural state. Two operating systems can run on the same ISA while using
different executable formats or calling conventions. Two targets can use the
same object format while selecting different ISAs. An ABI can constrain calling
conventions, register use, stack alignment, scalar and aggregate layout, symbol
rules, and unwinding without defining the operating system's complete API.

The source spelling <code>extern "C"</code> selects the target's supported C
ABI in Rust; it does not select one global C ABI. Likewise, a C17 source file
does not require ELF, Mach-O, PE/COFF, a 64-bit pointer, or little-endian object
representation. Those must come from the selected implementation and target.

Clang's official cross-compilation documentation describes the target triple
as a compiler selection and separately calls out the sysroot, headers,
libraries, assembler, and linker needed for a useful cross toolchain. A
successful compile-only object is not evidence that the target can link, load,
or run. Conversely, a target name printed by a compiler is not evidence that
the necessary target libraries are installed.

### Endianness and pointer width belong to the selected target

Rust exposes compiler-set <code>target_endian</code> and
<code>target_pointer_width</code> configuration values. Query them with:

~~~sh
rustc +1.96.1 --print cfg --target THE_EXACT_TARGET
~~~

The result describes that rustc target configuration. It is build-time
evidence, not runtime discovery and not a property of every machine sharing the
same architecture label. <code>usize::BITS</code> in one built Rust artifact
agrees with that artifact's pointer-sized integer width.

C17 does not define one endianness macro or require every pointer type to have
one universal byte count. <code>sizeof(void *)</code> is an observation for the
selected C implementation and target. Protocol byte order remains an explicit
format decision even when it happens to match the host.

### Build-time configuration cannot answer a runtime question

Rust <code>cfg</code> options are fixed during compilation. For example:

~~~rust
#[cfg(target_arch = "x86_64")]
fn x86_only_source_is_in_this_build() { /* ... */ }

let built_with_avx2 = cfg!(target_feature = "avx2");
~~~

These answer which source was included and which features the compiler may
assume for that compilation. They do not prove that an arbitrary future CPU
running a baseline artifact has an optional feature.

Runtime feature detection asks the running environment. On supported x86
targets, Rust's <code>is_x86_feature_detected!</code> checks a named CPU feature;
other architectures have their own supported mechanisms. A detector can itself
have operating-system and architecture preconditions. It is not interchangeable
with a build-time <code>cfg</code> test. The official x86 macro also expands to
<code>true</code> when the feature was enabled for the entire compilation, so
that result must be interpreted together with the build flags and artifact
baseline rather than as independent runtime-only evidence.

The safe dispatch condition is a conjunction:

~~~text
enter accelerated body
    only if body was built for this artifact
    AND required runtime features were positively observed
    AND the input contract for that body is satisfied.
~~~

If any term is false or unknown, choose the baseline. Never “try” an optional
instruction and hope to recover. An unsupported instruction can terminate the
process before application error handling is possible.

Compiler-wide feature flags require special care. Rust's rustc documentation
calls <code>-C target-feature</code> generally unsafe because inconsistent
features across the standard library, dependencies, and local code can create
ABI or behavior problems. A narrow feature-specific body plus checked dispatch
usually exposes a smaller audit surface than raising the baseline for the whole
artifact.

### SIMD is typed lane computation, not “several numbers at once”

A 128-bit vector could contain sixteen 8-bit lanes, eight 16-bit lanes, four
32-bit lanes, two 64-bit lanes, or another interpretation supported by an ISA.
Vector width alone does not state the lane count or type. A correct operation
names all three.

For four wrapping <code>u32</code> addition lanes:

~~~text
left  = [0, 1, 4294967295, 4294967295]
right = [0, 2,          0,          1]
sum   = [0, 3, 4294967295,          0]
~~~

Each lane wraps independently modulo <code>2^32</code>. There is no carry from
one lane into the next. Signed saturation, unsigned saturation, wrapping,
floating-point addition, integer multiplication, comparisons, shuffles, and
horizontal reductions are different operations even at the same vector width.

Four more contracts matter:

- **Alignment:** some loads accept arbitrary byte alignment while others
  require or benefit from stronger alignment. The intrinsic and ISA contract,
  not a guess based on vector width, decides.
- **Bounds:** a full-width load must not read past the initialized object, even
  if the extra bytes would be ignored later.
- **Tails:** when length is not a multiple of the lane count, use a bounded
  scalar tail, a proven masked operation, or padded storage whose extra access
  is actually valid.
- **Reductions:** changing grouping can change floating-point results and can
  change integer overflow points. “Same arithmetic expression” is not a proof
  of identical bits.

Compilers may auto-vectorize scalar source, decline to vectorize vector-shaped
source, or generate a different sequence after optimization. Source semantics
and inspected machine code are separate evidence. The supplied Rust function
models four independent lanes but deliberately makes no code-generation claim.

### Baseline and accelerated implementations need one semantic contract

A deployable design starts with a baseline implementation valid for the
minimum supported artifact tuple. An accelerated implementation must define:

1. the same input and output contract, including overflow and error behavior;
2. its required build features and runtime features;
3. its alignment, aliasing, length, and tail preconditions;
4. a dispatcher that checks all preconditions before entry; and
5. differential tests comparing both implementations on normal and endpoint
   inputs whenever the accelerated body can be executed safely.

Dispatch itself should be easy to test without special hardware. The
[Python policy model](examples/target_policy.py) represents a build manifest,
requires exactly one feature-free baseline, records lane width separately from
total implementation vector width, and selects a larger-vector variant only
when every required feature appears in the supplied runtime evidence. Its
accelerated result is a policy decision, not proof that native code exists.

The [Rust model](examples/dispatch_model.rs) tests the four truth-table cases
for “body built” and “runtime feature observed.” It never enters a target
feature body. The [C17 baseline](examples/baseline_add.c) supplies executable
scalar evidence for zero, normal, maximum, wrapping, null, and over-budget
cases on the native target.

## Worked example

Suppose the manifest says the native artifact contains a scalar baseline and a
128-bit body requiring <code>sse2</code>. The policy has four observations:

| Accelerated body in this build | Runtime feature observed | Selection |
| --- | --- | --- |
| no | no | baseline |
| no | yes | baseline |
| yes | no | baseline |
| yes | yes | simd128 |

The third row is the critical unsupported-instruction case: the compiled body
exists, but entry remains forbidden. The second row is equally important:
runtime hardware cannot select source that was not included in the artifact.
The Python example encodes those two facts separately and tests the table.

For semantic evidence, add these four wrapping u32 lanes:

~~~text
[0, 1, 4294967295, 4] + [0, 2, 1, 5]
    = [0, 3, 0, 9]
~~~

This proves the model's per-lane result, including one wrap. It does not prove
that a compiler emitted a 128-bit instruction. The C program then supplies an
independent scalar executable result for the current target. Finally, the
smoke check records <code>rustc -vV</code>, <code>rustc --print cfg</code>,
source hashes, and one capability-detected artifact inspection. Each evidence
kind answers only its own question.

### A capability matrix prevents wishful portability

Maintain one row per exact target and build mode:

| Target | Compiler/toolchain | Build | Link | Run | Inspector | Dispatch evidence | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Native tuple | exact versions | observed | observed | observed | optional result | baseline observed | supported in this envelope |
| Non-host tuple | exact versions | observed or failed | observed, failed, or not attempted | not run unless an authorized runner exists | optional result | not executed | scoped result |

“Listed by <code>rustc --print target-list</code>” means the compiler knows a
target specification. “Target library installed,” “object emitted,” “linked,”
and “ran under a matching environment” are later, distinct states. Do not fill
one column from another.

A cross build must never execute its output on the build host merely because a
filename looks executable. Preserve the exact command and status. A missing
target library, linker, sysroot, or inspector is useful negative evidence about
the current envelope, not a reason to relabel a host artifact.

### Artifact inspection is reproducible evidence, not a universal guarantee

For every artifact retained as evidence, record:

- source hashes and the exact compiler identity;
- target and all code-generation, feature, optimization, and link flags;
- stdout, stderr, and immediate status for every build or inspection command;
- artifact hash before inspection;
- inspector name and version; and
- whether the artifact was merely built, linked, loaded, or executed.

Use an inspector only after capability detection. <code>readelf -h</code>,
<code>objdump -f</code>, or <code>file</code> may identify a format and machine
for an artifact they understand. Their output is an observation about those
bytes. Rust <code>cfg</code> output is a compiler configuration observation.
Successful execution is a runtime observation. A language or ABI guarantee
requires the relevant normative contract; it cannot be reverse-engineered from
one successful run.

## Check your understanding

1. Why can two artifacts with the same ISA require different loaders or calling
   conventions?
2. What does <code>cfg!(target_feature = "...")</code> establish, and what
   runtime fact does it not establish?
3. Why must “accelerated body built” and “runtime feature observed” be separate
   inputs to dispatch?
4. How many 16-bit lanes fit in 128 bits, and which other information is needed
   to specify their addition?
5. What must happen to a three-element tail after processing four-lane chunks?
6. Why does a successful cross compile not prove a successful link or run?
7. Which evidence can identify the format of one artifact, and why is that not
   a C17 guarantee?

## Next step

Complete the lab by producing native build/run evidence and an honest non-host
capability row. Preserve the baseline and dispatch truth table; do not add real
feature-specific intrinsics yet. The next systems module examines timing and
microarchitectural leakage, where the distinction between source semantics and
observed execution becomes a security boundary.

## Sources

- The [Rust Reference: conditional compilation](https://doc.rust-lang.org/reference/conditional-compilation.html)
  defines compiler-set target configuration including architecture, OS,
  environment, features, endianness, and pointer width.
- The [rustc targets chapter](https://doc.rust-lang.org/rustc/targets/index.html)
  documents <code>--target</code> and warns that target features change the
  instruction sets available to generated code.
- Rust's [x86 runtime feature-detection macro](https://doc.rust-lang.org/std/macro.is_x86_feature_detected.html)
  documents runtime detection and its relationship to compile-time enabled
  features.
- The rustc [target-feature known issues](https://doc.rust-lang.org/rustc/targets/known-issues.html)
  explains why inconsistent target-feature selection can create undefined
  behavior and ABI mismatches.
- The official [Clang cross-compilation guide](https://clang.llvm.org/docs/CrossCompilation.html)
  distinguishes target selection from sysroot, headers, libraries, assembler,
  and linker availability.
- GCC's [developer options](https://gcc.gnu.org/onlinedocs/gcc/Developer-Options.html)
  document <code>-dumpmachine</code> as the compiler's target machine value.

The web documentation is supporting guidance for the pinned toolchain. Preserve
the exact compiler output used by an assessment because current online pages
can describe a later release.
