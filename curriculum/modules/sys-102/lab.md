# Lab: audit and extend one owned FFI region

## Goal

Trace one C allocation through a Rust owner, distinguish moves from borrows,
extend the copied boundary with one exclusive mutation, and preserve evidence
that separates a selected-allocation wipe from complete key destruction.

## Setup

From the repository root, run the supplied smoke check:

~~~sh
cd curriculum/modules/sys-102
PYTHONDONTWRITEBYTECODE=1 python3 checks/lab_smoke.py
smoke_status=$?
printf 'smoke status: %s\n' "$smoke_status"
~~~

It must print <code>sys-102 lab smoke: PASS</code> and exit 0. The check copies
sources to a fresh temporary directory, compiles C with
<code>cc -std=c17</code>, compiles Rust with
<code>rustc +1.96.1 --edition=2024</code>, runs positive, exact-boundary, and
invalid cases, observes a deliberately wrong C expectation fail and recover,
and observes rustc reject an aliasing conflict.

Create a separate temporary workspace and copy, rather than edit, the examples:

~~~sh
workdir="$(mktemp -d)"
mkdir -- "$workdir/src" "$workdir/build" "$workdir/evidence"
cp -- examples/owned_buffer.h examples/owned_buffer.c \
    examples/c_harness.c examples/ownership_bridge.rs "$workdir/src/"
cd -- "$workdir"
pwd
~~~

Every source edit, object, executable, stdout, stderr, status, hash, and note
must remain under the printed temporary path. Use no Cargo, network command,
third-party code, administrator access, global configuration change, or output
path inside the module source tree.

## Tasks

1. **Build an owner-state ledger — SYS-102-01.** For source bytes
   <code>[4, 8, 15, 16, 23, 42]</code>, make a table with one row for each of:
   source automatic array, empty C descriptor, successful C allocation,
   <code>first_owner</code>, moved <code>second_owner</code>, shared slice,
   exclusive slice, wiped allocation, freed allocation, and reset descriptor.
   Record storage duration, lifetime start/end, base and length facts, current
   owner, permitted borrowers, mutation permission, and next valid transition.
   State why a retained source pointer, interior <code>free</code>, use after
   free, or second free of the original base would be outside the contract and
   can have undefined behavior in C.
2. **Reproduce the bounded build.** Compile only the copied sources:

   ~~~sh
   cc -std=c17 -Wall -Wextra -Wpedantic -Werror -I src \
       -c src/owned_buffer.c -o build/owned_buffer.o
   cc -std=c17 -Wall -Wextra -Wpedantic -Werror -I src \
       src/c_harness.c build/owned_buffer.o -o build/c_harness
   build/c_harness >evidence/c.stdout 2>evidence/c.stderr
   c_status=$?

   rustc +1.96.1 --edition=2024 --test -D warnings \
       -C "link-arg=$workdir/build/owned_buffer.o" \
       src/ownership_bridge.rs -o build/ownership_tests
   build/ownership_tests --test-threads=1 \
       >evidence/rust.stdout 2>evidence/rust.stderr
   rust_status=$?
   printf 'C status: %s\nRust status: %s\n' \
       "$c_status" "$rust_status" | tee evidence/statuses.txt
   ~~~

   Record <code>cc --version</code>, <code>rustc +1.96.1 --version</code>, and
   <code>rustc +1.96.1 -vV</code>. Inspect both output channels before claiming
   success. Explain which source or test covers normal, empty, exact-32,
   length-33, null, inconsistent-state, move, borrow, wipe, and destruction
   behavior.
3. **Trace provenance and slices — SYS-102-02.** For every unsafe block in the
   Rust source, map each documented premise to the line that establishes it or
   to the external C promise on which it depends. Include allocation identity,
   base pointer, one-allocation extent, alignment, initialized bytes, lifetime,
   aliasing, mutation, target layout, callbacks, unwinding, and pointer
   retention. Explain why null plus zero is a valid C empty representation but
   cannot be passed directly to <code>slice::from_raw_parts</code>.
4. **Add an exclusive mutation.** In the copied header and C source, add:

   ~~~c
   int sys102_buffer_xor(
       struct sys102_buffer *buffer,
       uint8_t mask
   );
   ~~~

   It must validate the descriptor before access, mutate exactly
   <code>len</code> live bytes, retain nothing, allocate and free nothing, and
   reject null or inconsistent state without partial mutation. Add raw C tests
   for empty, ordinary, exact-32, null descriptor, and
   <code>{NULL, 1}</code>. State that applying the same mask twice restores the
   bytes but is not encryption, authentication, or secure erasure.
5. **Expose only a safe exclusive Rust method.** Add the external declaration
   and <code>OwnedBuffer::xor(&amp;mut self, mask: u8)</code>. Its unsafe ledger must
   cover symbol/layout agreement, the live allocation, exclusive mutation,
   bounds, retention, callbacks, unwinding, statuses, and artifact identity.
   Test ordinary, zero mask, exact-32, and twice-applied behavior. Do not expose
   a raw pointer or accept <code>&amp;self</code> for mutation.
6. **Observe failure sensitivity.** First change one copied C assertion from the
   correct post-XOR sum to an incorrect value. Build and run only that test,
   redirect both channels, and immediately record a nonzero status. Restore the
   correct value, rebuild in a fresh <code>build/recovered</code> directory, and
   record status 0.

   Separately create a small Rust program that holds the result of
   <code>as_slice()</code>, calls <code>xor(&amp;mut self, ...)</code>, and then uses
   the shared slice. Compile it with the pinned toolchain. Preserve rustc's
   nonzero status and diagnostic, then end the shared borrow before mutation and
   preserve a successful compile and run. Do not “fix” the conflict with raw
   pointers or unsafe code.
7. **Audit destruction evidence — SYS-102-04.** Inventory every location that
   held the six input bytes during the lab: original source, C allocation,
   Rust views, compiler/runtime temporaries you cannot enumerate, stdout or
   diagnostic representations, allocator storage, and any operating-system or
   media copies that are in scope for your environment. For each, record what
   mechanism or observation applies and what remains unknown.

   Your conclusion must say that volatile stores and zero readback concern the
   selected live allocation. They do not prove erasure of the separate source,
   registers, caches, swap, dumps, backups, snapshots, remapped storage, or
   physical media. Compare that bounded evidence with NIST's recovery-oriented
   key-destruction goal and SP 800-88 Rev. 2 media-sanitization categories
   without claiming this lab satisfies either complete procedure.
8. **Record bounds and identities.** The input cap is 32 bytes. Each clone,
   sum, XOR, or wipe performs at most 32 byte operations, and one owner holds at
   most one 32-byte C allocation. State these as model bounds, not exact
   resident memory. Record absolute workspace, source SHA-256 hashes, exact
   compiler versions and target, commands, stdout, stderr, immediate statuses,
   covered cases, and the fact that all products stayed in the temporary
   workspace.

## Verification

The lab is complete only when:

- every C object and Rust executable was produced under the temporary path;
- C compilation used C17 with warnings denied and Rust compilation used exact
  toolchain 1.96.1, edition 2024, with warnings denied;
- C tests cover positive, empty, exact limit, over limit, null, inconsistent
  state, unchanged output on failure, wipe, and idempotent reset destruction;
- Rust tests cover move, shared and exclusive borrows, bounded rejection,
  narrow FFI status handling, wipe, and explicit destruction;
- each raw-to-slice and FFI unsafe block has a complete local premise ledger;
- the wrong runtime expectation and overlapping-borrow source both produced
  observed nonzero results before correction;
- corrected sources pass in a fresh build directory;
- the owner ledger has exactly one allocation owner after C success and none
  after destruction; and
- the zeroization conclusion names both what was observed and every important
  class of copy it does not cover.

Rerun the repository smoke check from the module directory as separate evidence
that your temporary edits did not change the supplied example:

~~~sh
PYTHONDONTWRITEBYTECODE=1 python3 checks/lab_smoke.py
~~~

Passing host tests do not establish Orange memory, ownership, FFI,
zeroization, or professional-toolchain behavior.

## Reflection

Write six to nine sentences:

- Which transition created allocated storage, and which transition ended its
  lifetime?
- Which pointer facts remained contractual rather than dynamically checked?
- What did a Rust move transfer, and what did each borrow permit?
- Why is numeric adjacency insufficient to join two raw ranges into one slice?
- Which unsafe premise is most likely to drift when the C artifact changes?
- What exactly did wipe readback establish?
- Which additional inventory and platform controls would be necessary before a
  key-destruction claim?
