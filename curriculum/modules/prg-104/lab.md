# Lab: extend a bounded C/Rust bridge

## Goal

Trace the supplied C and Rust memory contracts, reproduce their bounded tests,
then add one narrow count function on both sides of the FFI boundary with a
complete unsafe-assumption record.

## Setup

From the repository root:

~~~sh
cd curriculum/modules/prg-104
bash checks/lab_smoke.sh
smoke_status=$?
printf 'smoke status: %s\n' "$smoke_status"
~~~

The check must print <code>prg-104 lab smoke: PASS</code> and exit 0. It copies
the examples into a fresh temporary directory, compiles C17 and Rust 2024
there, runs normal/boundary/invalid cases, and removes only that directory.

Create your own workspace and copy the sources:

~~~sh
workdir="$(mktemp -d)"
mkdir -- "$workdir/src" "$workdir/build"
cp -- examples/bounded_sum.h examples/bounded_sum.c \
    examples/c_harness.c examples/ffi_bridge.rs "$workdir/src/"
cd -- "$workdir"
pwd
~~~

Use a plain-text editor. Every source copy, object, executable, and test record
you create must remain under the printed path. Do not use Cargo, a network
command, administrator access, global compiler configuration, or an output path
inside the module source tree.

## Tasks

1. **Trace both contracts.** For values <code>[3, 3, 5]</code>, length 3, and
   output initialized to 99, trace the supplied sum in C and Rust.
   Record each validation, pointer or borrow fact, loop index, read, state
   change, output write, and result. Repeat only the validation steps for null
   values with length 1 and for nine valid values.
2. **Reproduce the build manually.** In <code>build</code>, compile the copied
   C implementation and harness with C17, warnings as errors, and no source-tree
   output. Run the C harness and record its three result channels. Compile the
   Rust tests with <code>rustc +1.96.1 --edition=2024</code>, link the copied C
   object, and record the tests. Compare these results with the smoke check
   instead of assuming they match.

   From the temporary workspace, the complete commands are:

   ~~~sh
   cc -std=c17 -Wall -Wextra -Wpedantic -Werror -I src \
       -c src/bounded_sum.c -o build/bounded_sum.o
   cc -std=c17 -Wall -Wextra -Wpedantic -Werror -I src \
       src/c_harness.c build/bounded_sum.o -o build/c_harness
   build/c_harness > build/c.stdout 2> build/c.stderr
   c_status=$?

   rustc +1.96.1 --edition=2024 --test -D warnings \
       -C "link-arg=$workdir/build/bounded_sum.o" \
       src/ffi_bridge.rs -o build/ffi_tests
   build/ffi_tests --test-threads=1 \
       > build/rust.stdout 2> build/rust.stderr
   rust_status=$?

   printf 'C status: %s\nRust status: %s\n' "$c_status" "$rust_status"
   ~~~

   Record <code>rustc +1.96.1 -vV</code> as well as
   <code>rustc +1.96.1 --version</code>; verbose output names the host target.
   Read both stdout and stderr files before claiming success.
   <code>-I src</code> adds the copied header directory,
   <code>-c</code> stops after producing an object, and <code>-o</code> names
   each output. Rust <code>--test</code> builds the test harness, while
   <code>-C link-arg=...</code> gives its linker the copied C object.
3. **Add a bounded C function.** In the copied header and C source, add:

   ~~~c
   int bounded_count_i32(
       const int32_t *values,
       size_t len,
       int32_t target,
       size_t *out_count
   );
   ~~~

   Use the same maximum and status codes. Empty input is valid and has count
   zero. Output is required and changes only on success. Validate before reads,
   read exactly <code>len</code> elements, retain no pointer, and document the
   complete contract.
4. **Add C tests.** Exercise a repeated target, an absent target, empty input,
   exactly eight values, nine values, null values with nonzero length, and null
   output. For every error, confirm the status and unchanged output.
5. **Add safe Rust behavior.** Implement
   <code>rust_bounded_count(values: &amp;[i32], target: i32)</code> with
   <code>Result&lt;usize, ...&gt;</code>. Reject more than eight items and
   test the same safe normal and boundary cases.
6. **Add the FFI wrapper.** Add only the new count symbol to the supplied
   external declarations, expose a safe slice wrapper, validate length before
   unsafe code, use one local output, and map every C status including unknown
   values. Put a numbered
   <code>SAFETY</code> comment immediately above the call covering ABI/type
   agreement, pointer validity, length, aliasing, output initialization and
   exclusive write, empty input, mutation, retention, synchronization,
   unwinding/callbacks, constants/statuses, and linked artifact identity.
7. **Rebuild in a fresh directory.** Run all C and Rust tests for the original
   sum and new count. Preserve versions, exact commands, source identities,
   stdout, stderr, and statuses. State the normal, exact-limit, and invalid
   cases and what each establishes.

## Verification

The lab is complete only when:

- all objects and executables were written to fresh temporary workspaces;
- C17 compilation and pinned Rust 1.96.1 edition-2024 compilation use warnings as
  errors;
- raw C tests cover invalid pointers and length without dereferencing them;
- safe Rust accepts slices only, returns explicit results, and enforces length;
- the FFI wrapper contains one narrow unsafe call and a complete assumption
  ledger;
- output remains unchanged for every C error;
- all normal, empty, exact-eight, too-long, and null-pointer cases behave as
  specified; and
- unexpected statuses fail closed.

These are host C/Rust build and test observations. They are not evidence for any
Orange language feature, compiler behavior, FFI, ABI, artifact, or professional
workflow.

## Reflection

Write five to eight sentences:

- Which C pointer facts cannot be checked from pointer and length alone?
- Which of those facts does a safe Rust slice establish, and which application
  bound remains manual?
- Which single unsafe assumption would be most dangerous if stale?
- Why can tests support but not prove the full unsafe contract?
- Why must this lab remain separate from Orange evidence?
