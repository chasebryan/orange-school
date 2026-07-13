# Assessment: independent native artifact and ABI audit

## Instructions

Complete this assessment independently in a fresh temporary directory. Do not
copy, import, rename, or lightly translate the module examples or lab solution.
Use C17 and <code>rustc +1.96.1 --edition=2024</code> directly with warnings
denied. Use only local toolchain components after capability detection; do not
use a package manager, third-party dependency, network operation, administrator
access, global configuration change, or source-tree output path.

Submit source files, tests, an artifact graph, an ABI contract, inspection
records, safe deliberate-failure evidence, and a reproducible command/result
record. This assessment covers:

- **SYS-103-01:** Trace C17 translation units through relocatable objects,
  archives, linking, and executable loading; inspect sections, symbols, and
  relocations while distinguishing C linkage from toolchain visibility.
- **SYS-103-02:** Specify and measure a target-scoped C/Rust ABI contract for
  calling convention, exact-width values, field order, size, alignment,
  padding, and offsets without promoting an observation to a language
  guarantee.
- **SYS-103-03:** Design a narrow FFI boundary with explicit pointer,
  ownership, lifetime, aliasing, mutation, retention, status, output, panic,
  and unwind rules and a fail-closed safe Rust wrapper.
- **SYS-103-04:** Produce reproducible, target-specific artifact evidence with
  capability-detected tools and positive, endpoint, invalid, and deliberate
  link-failure observations.

## Knowledge check

1. Distinguish preprocessing output, C translation unit, relocatable object,
   static archive, shared object, executable, and loaded process image. At
   which stages may an unresolved external reference remain?
2. For a call from <code>consumer.o</code> to a function defined in
   <code>provider.o</code>, explain the separate jobs of a section header, a
   symbol-table entry, and a relocation. Explain why none is a universal C17
   requirement.
3. Compare external C linkage, file-scope <code>static</code> internal linkage,
   toolchain symbol visibility, stripping, static-library selection, and
   dynamic symbol resolution. Include one false inference prevented by each
   distinction.
4. Define ABI and list target, object-format, symbol, type, layout, register or
   stack, aggregate-passing, and unwind facts needed for one foreign call.
   Explain why <code>extern "C"</code> is target-relative.
5. For C fields <code>uint16_t code</code>, <code>uint64_t total</code>, and
   <code>uint8_t state</code> in that order, draw two layouts permitted by the
   broad source description, including inter-field and tail padding. State
   what must be measured and compared with Rust <code>#[repr(C)]</code>.
6. Explain why exact-width C typedef availability is an implementation fact
   and why fixed width still does not by itself prove compatible calling ABI.
   Compare with C <code>long</code>, <code>enum</code>,
   <code>size_t</code>, Rust <code>bool</code>, a Rust enum, and a Rust slice.
7. List every validity, lifetime, alignment, extent, aliasing, mutation, and
   ownership obligation for a C pointer/length pair borrowed from a Rust slice.
   Which can the C callee check from values alone?
8. Design a status/output protocol that distinguishes success with no match,
   invalid input, unknown foreign status, and an impossible success output.
   Explain why output remains unchanged on failure.
9. State a safe policy for Rust panic and C/C++ unwinding at a non-unwinding
   <code>"C"</code> boundary. Explain why <code>catch_unwind</code> is not a
   universal foreign-exception or abort recovery mechanism.
10. Explain how optimization, stripping, object format, and absent inspection
    tools limit an <code>nm</code>/<code>readelf</code>/<code>objdump</code>
    claim. Identify the versions, hashes, flags, target, output channels, and
    statuses needed to reproduce it.

## Independent task

Create these independent files:

- <code>audit_abi.h</code> with declarations and fixed-width status constants;
- <code>first_above.c</code> with the operation definition;
- <code>audit_layout.c</code> with C layout probes;
- <code>c_tests.c</code> with positive, endpoint, and checked-invalid tests;
- <code>rust_tests.rs</code> with matching <code>repr(C)</code> types, a safe
  wrapper, and tests;
- <code>bad_provider.c</code> used only in a separate fail-closed result test;
  and
- <code>build_and_audit.sh</code> that builds and records evidence under its
  own fresh temporary workspace.

1. **Define the interface — SYS-103-02 and SYS-103-03.** Use this request:

   ~~~c
   typedef struct audit_request {
       uint32_t job_id;
       uint16_t flags;
       uint8_t version;
       uint8_t item_count;
   } audit_request;
   ~~~

   Version must equal 2, flags must be from 0 through 15, and item count must be
   from 0 through 24. Define a separate layout-witness structure with fields
   <code>uint16_t code</code>, <code>uint64_t total</code>, and
   <code>uint8_t state</code> in that order. Probe C size, alignment, and every
   offset for both types. Define matching Rust structures with
   <code>#[repr(C)]</code> and compare every measurement at runtime. Do not
   hard-code one platform's padding as the compatibility check.
2. **Implement a bounded C operation — SYS-103-03.** Define:

   ~~~c
   int32_t audit_first_above(
       const audit_request *request,
       const int32_t *values,
       uint32_t value_count,
       int32_t threshold,
       uint32_t *out_index
   );
   ~~~

   Status 0 means success. On success, write the first index whose value is
   strictly greater than the threshold or <code>UINT32_MAX</code> when absent.
   Give distinct fixed-width statuses to null, length mismatch/excess, version,
   and flags errors. Validate output and request before dereference; validate
   count, header fields, and the nonempty values pointer before the first read.
   Empty input may use null. On every error leave output unchanged. Read at
   most 24 values, retain no pointer, invoke no callback, perform no allocation,
   and do not unwind.
3. **Build separate artifacts — SYS-103-01.** Compile
   <code>first_above.c</code>, <code>audit_layout.c</code>, and
   <code>c_tests.c</code> as three distinct C17 translation units and objects.
   If <code>ar</code> is available, archive the first two objects and link the C
   and Rust tests against it. Otherwise link both objects explicitly and state
   that archive behavior was not exercised. Draw and submit the exact artifact
   graph. Explain each definition, unresolved reference, relocation, archive
   selection, and final link edge relevant to
   <code>audit_first_above</code>.
4. **Write a safe Rust wrapper — SYS-103-03.** The public Rust function accepts
   job ID, flags, version, and <code>&[i32]</code> and returns
   <code>Result&lt;Option&lt;u32&gt;, AuditError&gt;</code>. Reject invalid version,
   flags, or more than 24 values before unsafe entry. Convert the length only
   after the bound. Construct a local request and output, use the documented
   null convention for an empty slice, and make exactly one foreign call.
   Translate <code>UINT32_MAX</code> to <code>None</code> only after success.
   Reject any other returned index at least as large as the input. Map every
   known status distinctly and fail closed on an unknown status.

   Put a numbered safety ledger adjacent to the call. It must cover the exact
   linked symbol/artifacts and source hashes, target C ABI, fixed-width types,
   measured request layout, pointer provenance, initialized extent, alignment,
   lifetime, length, aliasing, mutation, output exclusivity and write rules,
   empty input, retention, synchronization, callbacks, constants/statuses,
   result semantics, and panic/unwind policy.
5. **Test transfer behavior.** C and Rust must cover first, middle, last, and no
   match; empty input; 1 and exactly 24 values; a 25th value; thresholds at
   <code>INT32_MIN</code> and <code>INT32_MAX</code>; version 1 and 2; flags 0,
   15, and 16; item-count mismatch; null request, nonempty values, and output in
   raw C; and unchanged output after every failure. Safe Rust tests must show
   invalid fields and excessive input are rejected before the call. Never
   execute a dangling, misaligned, undersized, or illegally overlapping
   pointer.
6. **Test a hostile but ABI-compatible provider.** In a separate Rust test
   executable, link <code>bad_provider.c</code> instead of
   <code>first_above.c</code>. Its function must return success but write an
   index equal to <code>value_count</code>. Confirm the safe wrapper returns an
   explicit impossible-result error rather than indexing or accepting the
   value. Label this as fail-closed result validation, not evidence that the
   intended provider is correct. Never link both providers into one executable.
7. **Inspect target artifacts — SYS-103-01 and SYS-103-04.** First record exact
   paths or unavailability for <code>cc</code>, <code>rustc</code>,
   <code>ar</code>, <code>nm</code>, <code>readelf</code>, and
   <code>objdump</code>. When <code>nm</code> is available, identify the
   operation's definition and consumer references before and after linking.
   When supported, use <code>readelf</code> or <code>objdump</code> to annotate
   relevant sections, symbols, relocations, and final dynamic metadata. State
   exactly which inspector, options, object format, and artifact produced each
   observation. Do not convert missing tooling into invented evidence.
8. **Preserve deliberate failure evidence — SYS-103-04.** Compile the consumer
   object successfully, then link it without either provider and preserve the
   immediate nonzero status and diagnostic. Separately change only the Rust
   layout-witness field order, run only its comparison test, and preserve the
   nonzero status without making an FFI call through that type. Restore the
   field order and intended provider, rebuild in a new build directory, and
   preserve all-passing C and Rust results. Hash the source state associated
   with every failed and restored run.
9. **Submit reproducible evidence — SYS-103-04.** Record absolute temporary
   path, tool identities, <code>rustc +1.96.1 -vV</code>, target, exact commands,
   source and inspected-artifact SHA-256 hashes, stdout, stderr, and immediate
   statuses. State the 24-element/read/loop bound and O(n) operation time for
   <code>0 &lt;= n &lt;= 24</code>. Record artifact byte sizes only as observations,
   not universal bounds. Separate language guarantees, target ABI assumptions,
   tool observations, runtime test evidence, and untested obligations. State
   that the assessment establishes no Orange syntax, compiler, object format,
   ABI, linker, FFI, package, deployment, or professional-operation behavior.

## Completion criteria

Use [the rubric](rubric.md). Passing requires at least 80/100 and every critical
criterion. The submission must:

- accurately trace separate translation units through objects, optional
  archive selection, relocations, final links, and target-supported inspection
  for **SYS-103-01**;
- compare C and Rust request/witness size, alignment, and every field offset on
  the recorded target and distinguish measurements from guarantees for
  **SYS-103-02**;
- implement the bounded C function and narrow safe Rust wrapper with complete
  ownership, lifetime, aliasing, error/output, result, panic, and unwind
  contracts for **SYS-103-03**;
- preserve positive, exact-endpoint, checked-invalid, unresolved-link,
  harmless-layout-mismatch, hostile-provider, and restored-pass evidence for
  **SYS-103-04**; and
- keep all work temporary, offline, source-identified, target-scoped, and free
  of unsupported Orange or cross-platform claims.
