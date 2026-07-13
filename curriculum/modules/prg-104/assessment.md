# Assessment: bounded first-match FFI

## Instructions

Complete this assessment independently in fresh temporary workspaces. Use
<code>cc -std=c17</code> and
<code>rustc +1.96.1 --edition=2024</code> directly;
do not use Cargo, third-party code, network access, global configuration, or
source-tree build output. Submit C and Rust sources, tests, a build script,
traces, an unsafe-assumption ledger, and a reproducible evidence record.

This assessment covers:

- **PRG-104-01:** Compare C memory, pointer, and bounds contracts with Rust
  ownership and borrowing using concrete traces.
- **PRG-104-02:** Build and test bounded C and Rust functions with explicit
  success and error behavior.
- **PRG-104-03:** Integrate one C function through a narrow Rust FFI wrapper and
  document every unsafe assumption.

## Knowledge check

1. Trace a C call with a three-element array, length 3, and writable output.
   State what is validated before each read or write. Then trace a Rust
   <code>&amp;[i32]</code> call over the same values.
2. Compare what a C pointer plus length promises with what ownership and a
   shared Rust slice establish. Include lifetime, nullability, alignment,
   initialized extent, aliasing, mutation, and application bounds.
3. Explain why a non-null C pointer can still be invalid and why C cannot
   generally validate its allocation extent.
4. Explain what <code>unsafe extern "C"</code> means and why a safe wrapper does
   not remove the need for an assumption ledger.
5. Distinguish a C status result, a Rust <code>Result</code>, a passing host
   test, and evidence about Orange.

## Independent task

Implement a bounded first-match operation with maximum length 32.

1. **Concrete comparison — PRG-104-01.** Trace C and safe Rust for target 7
   over <code>[4, 7, 7, 9]</code>. Record validation, pointer/borrow state,
   comparisons, output state, return value, and lifetime end. Also trace the
   validation path for empty input, 33 items, null C values with length 1, and
   null C output. Identify which invalid states cannot be constructed through
   the safe Rust API.
2. **Bounded implementations — PRG-104-02.** Create a C17 function:

   ~~~c
   int bounded_find_first_i32(
       const int32_t *values,
       size_t len,
       int32_t target,
       size_t *out_index
   );
   ~~~

   Define named status codes for success, null pointer, and excessive length.
   On success, write the first index or <code>SIZE_MAX</code> when absent.
   Empty input is valid and may use null values. On failure, leave output
   unchanged. Validate before dereferencing, retain no pointer, and document
   the contract.

   Implement the same behavior safely in Rust as a function from
   <code>&amp;[i32]</code> and target to
   <code>Result&lt;Option&lt;usize&gt;, FindError&gt;</code>. Reject more than
   32 items.
3. **Narrow FFI — PRG-104-03.** Declare the C symbol with exact-width and
   target-appropriate FFI types. Write a safe Rust wrapper accepting only a
   slice and target and returning
   <code>Result&lt;Option&lt;usize&gt;, FfiFindError&gt;</code>. Check length
   before the unsafe call, translate <code>SIZE_MAX</code> only after success,
   reject an impossible returned index, map all known statuses, and fail closed
   on an unknown status.

   Place a numbered <code>SAFETY</code> comment at the call. Cover symbol and
   artifact identity, C ABI, type widths/signedness, <code>size_t</code>
   compatibility, pointer provenance/alignment/initialized extent/lifetime,
   slice length, aliasing and mutation, output validity and write rules, empty
   input, pointer retention, synchronization, callbacks/unwinding, constants,
   status values, and result-index semantics.
4. **Tests and build evidence.** C tests must cover first/middle/last/absent
   matches, empty input, exactly 32 items, 33 items, null values with nonzero
   length, and null output. Confirm unchanged output on errors. Rust tests must
   cover equivalent safe cases, pre-call oversized rejection, FFI results, and
   lack of input mutation.

   Write a Bash build script that creates and cleans only its own fresh
   temporary directory, copies sources there, compiles C17 and Rust edition
   2024 with warnings denied, links the copied object, and runs all tests. It
   must select <code>rustc +1.96.1</code>, use no network, and modify no global
   configuration.
5. Record tool versions, target, absolute workspace, source identities, exact
   commands, stdout, stderr, exit statuses, covered cases, and evidence limits.
   State explicitly that the result is host-language prerequisite evidence and
   not Orange evidence.

## Completion criteria

Use [the rubric](rubric.md). Passing requires at least 80/100 and every critical
criterion. The submission must:

- produce accurate C-pointer and Rust-borrow traces and comparison for
  **PRG-104-01**;
- build bounded C and Rust functions with explicit success, absence, and error
  behavior plus normal/boundary/invalid tests for **PRG-104-02**;
- expose one narrow safe FFI wrapper, fail closed, and document every unsafe
  assumption for **PRG-104-03**;
- compile and test only in fresh temporary directories with the required
  language modes and tool version; and
- avoid every claim that host C/Rust evidence establishes Orange behavior.
