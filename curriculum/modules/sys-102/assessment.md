# Assessment: independent owned-region transfer

## Instructions

Complete this assessment independently in a fresh temporary workspace. Do not
copy or import the module's <code>owned_buffer</code> sources. Create a distinct
C17 API, C harness, Rust 1.96.1 wrapper and tests, build script, lifetime and
ownership traces, unsafe-assumption ledger, destruction-evidence audit, and
reproducibility record.

Use <code>cc -std=c17</code> and
<code>rustc +1.96.1 --edition=2024</code> directly. Use no Cargo, network,
third-party code, administrator access, global configuration change, or build
output outside the temporary workspace. Preserve stdout, stderr, and immediate
status for every required run.

This assessment covers:

- **SYS-102-01:** C object lifetime, storage duration, allocation,
  deallocation, and undefined behavior;
- **SYS-102-02:** Rust ownership, moves, borrows, aliasing, mutation, slices,
  and provenance obligations;
- **SYS-102-03:** a bounded C-to-Rust allocation ownership transfer and safe FFI
  wrapper; and
- **SYS-102-04:** accurate zeroization and destruction evidence.

## Knowledge check

1. Distinguish an object's storage duration, lifetime, allocation, address,
   owner, and a borrowed region. Give one case in which storage still exists
   but a particular typed access is invalid.
2. State the C requirements for passing a non-null pointer to
   <code>free</code>. Explain why a length field cannot prove that a pointer is
   the live original allocation base.
3. Trace successful and failed <code>realloc</code> ownership transitions for a
   nonzero size without losing or using the old allocation incorrectly.
4. Compare a Rust move, <code>&amp;[u8]</code>, and
   <code>&amp;mut [u8]</code>. State which one owns, what aliases are permitted,
   and when each becomes unusable.
5. List every safety requirement used to construct a Rust slice from raw
   pointer and length. Explain the special handling needed for C null plus zero.
6. Explain how undefined behavior in linked C can invalidate a Rust program and
   why an <code>unsafe</code> block neither proves nor contains the C contract.
7. Distinguish: source-level wipe intent, volatile-store execution, selected
   allocation zero readback, allocator release, key destruction, and storage
   media sanitization. State why none of the first four alone implies either of
   the last two.

## Independent task

Implement a maximum-48-byte **transfer region** whose allocation is created by
C and owned through one Rust wrapper.

1. **Define the C state machine — SYS-102-01.** Create
   <code>transfer_region.h</code> with an independent status enum and:

   ~~~c
   struct transfer_region {
       uint8_t *base;
       size_t length;
   };

   int transfer_region_import(
       const uint8_t *source,
       size_t length,
       struct transfer_region *destination
   );

   int transfer_region_count(
       const struct transfer_region *region,
       uint8_t needle,
       size_t *out_count
   );

   int transfer_region_scrub(struct transfer_region *region);
   int transfer_region_release(struct transfer_region *region);
   ~~~

   The empty state is <code>{NULL, 0}</code>. Import accepts 0–48 bytes,
   allocates and copies on nonempty success, retains no source pointer, and
   transfers the fresh allocation to the destination only on success. The
   destination must already be initialized empty and must not overlap the
   source region. No failure may replace a destination or leak an allocation.
   Document which premises C cannot validate.
2. **Implement bounded C behavior — SYS-102-01.** Validate all statically
   checkable state before access. Count reads exactly <code>length</code> bytes
   and leaves <code>*out_count</code> unchanged on failure. Scrub performs one
   volatile zero store for each selected live byte but does not allocate,
   release, or change length. Release scrubs, passes only the original base to
   the matching <code>free</code>, and resets the descriptor. Releasing the
   reset empty state again is valid.

   Document that fabricated, interior, stale, already-freed, undersized, or
   otherwise invalid plausible pointers are outside the contract and that
   accessing or releasing them can have undefined behavior. Do not claim shape
   checks detect those states.
3. **Test raw C states.** Cover import/count/scrub/release for empty, one byte,
   exactly 48 bytes, and a normal repeated-byte input. Cover length 49, null
   source with positive length, null destination, occupied destination, null
   count output, <code>{NULL, 1}</code>, and unchanged output/destination on
   every applicable failure. Confirm the independent source remains unchanged,
   selected-region readback is zero after scrub, release resets the descriptor,
   and the reset state can be released again. Do not intentionally dereference
   or free a fabricated non-null pointer.
4. **Create a one-owner Rust type — SYS-102-02.** In
   <code>transfer_owner.rs</code>, define an owning wrapper that is neither
   <code>Copy</code> nor <code>Clone</code>. Its only public constructor accepts
   <code>&amp;[u8]</code>, rejects length 49 before FFI, and transfers the C
   allocation only after success. Provide shared bytes, exclusive bytes, count,
   scrub, explicit consuming release, and <code>Drop</code>. Expose no raw
   pointer and no public way to fabricate the raw descriptor.

   Specify the foreign-release failure policy. A consuming release must not
   return an error and then let <code>Drop</code> issue the same foreign destroy
   again. Choose and justify a fail-stop path or a quarantined, possibly leaked
   consumed state when the foreign API cannot prove whether a failed call
   partially freed the allocation.

   Tests must move the owner to a new binding, read through a shared slice,
   mutate through an exclusive slice only after the shared borrow ends, and
   show the source allocation remains separate. Cover empty, exact 48, length
   49, count present/absent, scrub readback, and explicit release.
5. **Justify every unsafe operation — SYS-102-03.** Use a C-layout raw
   descriptor and an edition-2024 <code>unsafe extern "C"</code> block. Put a
   numbered safety ledger at each call and each raw-slice construction. Across
   the ledgers, cover:

   - exact symbol and linked-artifact identity;
   - target ABI, structure layout, integer widths, signedness, and status values;
   - pointer origin, original base, non-null/alignment, initialized extent, one
     allocation, and lifetime;
   - null-plus-zero behavior and the Rust slice non-null rule;
   - shared versus exclusive aliases and mutation;
   - destination/output initialization and non-overlap;
   - allocation ownership before success, after success, on failure, and after
     release;
   - allocator pairing, pointer retention, callbacks, synchronization, and
     unwinding; and
   - 48-byte prevalidation plus fail-closed handling of unknown status values.

   A statement such as “C checked the pointer” is insufficient for an origin,
   extent, or lifetime premise.
6. **Demonstrate failure sensitivity.** Preserve two observed failures and two
   corrected reruns:

   - change the expected count for a repeated byte to a wrong value, compile
     and run only that test, and capture nonzero status before restoration; and
   - compile a Rust source that retains a shared slice, requests the exclusive
     slice, and then uses the shared slice, capturing rustc's nonzero status
     before correcting the borrow scopes.

   Build corrected sources in a fresh directory. Preserve all four stdout,
   stderr, command, and immediate-status records.
7. **Audit zeroization and destruction — SYS-102-04.** For input
   <code>10 20 10 30 10</code>, inventory the source, C allocation, every
   learner-created copy or serialization, and relevant unobservable or
   platform-managed representations. Record the exact scrub and readback
   observation for the C allocation and the unchanged source observation.

   Your conclusion must state, without qualification by implication, that a
   source wipe or volatile store does not prove all copies, caches, registers,
   swap, dumps, backups, snapshots, remapped device areas, or physical media
   were erased. Compare your evidence to NIST SP 800-57's key-destruction goal
   and SP 800-88 Rev. 2's media-sanitization scope. Identify at least four
   additional system or process controls needed before making a broader
   destruction claim.
8. **Build and evidence.** Write a Bash script that creates its own fresh
   temporary build directory, copies sources into it, compiles C17 and Rust
   1.96.1 edition 2024 with warnings denied, links only the copied C object, and
   runs all tests. It may delete only the temporary directory it created and
   must perform no network operation.

   Record compiler versions, Rust host target, absolute workspace, source
   SHA-256 hashes, exact commands, stdout, stderr, statuses, covered cases, and
   the build-output inventory. State the bound of 48 byte operations for each
   import, count, or scrub and one allocation of at most 48 bytes per live
   owner. Do not present that model as exact stack, allocator, cache, register,
   or resident-memory usage. State that this is host C/Rust evidence, not Orange
   evidence.

## Completion criteria

Use [the rubric](rubric.md). Passing requires at least 80/100 and every critical
criterion. The submission must:

- accurately trace storage duration, lifetime, allocation ownership, and C
  undefined-behavior boundaries for **SYS-102-01**;
- use moves, shared/exclusive borrows, bounded slices, and explicit raw-pointer
  provenance obligations correctly for **SYS-102-02**;
- implement one narrow, bounded, fail-closed ownership-transfer wrapper with a
  complete unsafe ledger for **SYS-102-03**;
- present observed wipe/release facts and a copy inventory without turning them
  into unsupported key-destruction or media-sanitization claims for
  **SYS-102-04**;
- preserve positive, endpoint, invalid, deliberate-failure, and restored-pass
  evidence; and
- build only copied sources in fresh temporary directories using the required
  offline compiler modes.
