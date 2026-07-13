# Memory, ownership, regions, and zeroization

Memory safety is not a property of an address. A valid access depends on an
object or allocation that is still live, a pointer derived under the relevant
language rules, a range within that allocation, initialized values of the right
type, permitted aliasing and mutation, and an owner that will release the
resource exactly once. Professional systems work states and audits all of those
facts, especially where C and Rust meet.

This module compares the public C17 ballot draft with the Rust 1.96.1
Reference, standard library, Book, and Nomicon. It uses a small C-owned
allocation and a safe Rust wrapper to make the boundary executable. The code is
evidence for the cases and target tested, not a proof of all possible executions
and not evidence about Orange.

## Learning objectives

- **SYS-102-01:** Trace C object lifetime, storage duration, allocation, and
  deallocation, and identify accesses or releases whose behavior is undefined.
- **SYS-102-02:** Apply Rust ownership, moves, shared and exclusive borrows,
  slices, aliasing rules, and pointer-provenance obligations to concrete memory
  regions.
- **SYS-102-03:** Specify and implement one bounded C-to-Rust ownership transfer
  with a narrow safe wrapper and a complete unsafe-assumption ledger.
- **SYS-102-04:** Produce and evaluate zeroization and destruction evidence
  without claiming that one wipe proves every copy or physical representation
  was erased.

## Prerequisites

Pass <code>prg-104</code> and <code>sys-101</code>. You should be able to compile
C17 and Rust 1.96.1 code directly, read a narrow FFI declaration, distinguish a
mathematical bound from an allocation extent, and trace fixed-width bytes and
resource limits. The lab uses only <code>cc</code>,
<code>rustc +1.96.1</code>, Python 3.11 or newer, and local files. It requires no
network, package installation, Cargo, administrator access, or Orange compiler.

## Lesson

### Object, storage, lifetime, owner, and region are different facts

An **object** is a typed region of data storage in the C abstract machine. An
**allocation** is storage returned by an allocation operation. An object can
occupy all or part of an allocation, and an allocation can contain several
objects. An address is only a numeric location; it does not by itself establish
that an object exists there or that an access is allowed.

**Storage duration** classifies how storage is reserved. **Lifetime** is the
execution interval during which an object exists and its storage is reserved.
The C17 ballot draft specifies four storage durations:

| C storage duration | Typical source | Lifetime boundary |
| --- | --- | --- |
| Static | file-scope object or <code>static</code> declaration | complete program execution |
| Thread | <code>_Thread_local</code> object | execution of the creating thread |
| Automatic | ordinary block parameter or local | entry into and exit from the associated block, with VLA details handled separately |
| Allocated | <code>malloc</code>, <code>calloc</code>, or <code>realloc</code> result | successful allocation until deallocation |

These descriptions are summaries, not replacements for C17 §6.2.4. A pointer
can remain in a variable after the pointed-to lifetime ends, but using its value
as though it still designates the old live object is not valid. The draft says
that referring to an object outside its lifetime has undefined behavior and
that a pointer value becomes indeterminate when the object it points to, or just
past, reaches the end of its lifetime.

In this module, **region** is an audit term for one base allocation plus a
bounded subrange and lifetime. C17 does not provide a general region type, and
calling something a region does not make the access safe. A useful region record
contains:

~~~text
allocator identity, original base, byte extent, initialized/type state,
current owner, permitted borrowers, mutation permission, lifetime end,
and required destruction operation
~~~

### C allocation creates obligations the type system does not discharge

For a positive size, <code>malloc</code> either returns a null pointer or a
pointer to the requested space suitably aligned for an object type with a
fundamental alignment requirement. The returned storage has no declared type
and its bytes are initially indeterminate. The program establishes effective
types and initialized values through valid stores or copies before typed reads.

The deallocation contract is exact. <code>free(NULL)</code> has no effect. A
non-null argument to <code>free</code> must match a pointer earlier returned by
an allocation function and not already deallocated. Passing an interior
pointer, a pointer to an automatic object, or the same allocation twice has
undefined behavior. Access after deallocation is also outside the object's
lifetime and has undefined behavior. C cannot generally inspect a pointer and
recover its allocation extent, whether it is the original base, or whether a
different owner already freed it.

<code>realloc</code> deserves a separate trace. On failure for a nonzero size,
the old allocation remains owned by the caller. On success, the old object is
deallocated and the returned pointer owns the new object, even if its numeric
address happens to compare equal to the former address. Code must update the
owner only after interpreting the result under the exact size contract.

Undefined behavior is not a recoverable error status. Once an execution
dereferences a dangling or out-of-bounds pointer, reads an invalid typed value,
violates an applicable alias rule, races on an object, or frees invalid storage,
the C standard imposes no requirements on that execution. A later null check or
test assertion cannot repair it.

### Aliasing and mutation require a per-access account

Two pointers **alias** when they can designate overlapping storage. C permits
many aliases; it does not impose Rust's general “shared or mutable” reference
discipline. Restrictions instead arise from the accessed object's effective
type, character-type exceptions, <code>const</code> and
<code>volatile</code> qualifications, <code>restrict</code> promises,
sequencing, atomic rules, and the program's own API contracts. Saying “C
pointers may alias” is therefore as incomplete as saying “C pointers never
alias.” State which accesses overlap and why each read or write is permitted.

The example's C clone contract requires the source byte range and output owner
object not to overlap. It copies all source bytes into a fresh allocation and
retains no source pointer. Mutation through the returned owner therefore cannot
mutate the separate source copy. The contract also requires the output value to
start as <code>{NULL, 0}</code>; silently replacing a live owner would leak its
allocation.

The C structure performs useful shape checks—length at most 32 and null exactly
for the empty state—but shape is not provenance. A fabricated non-null pointer
with a plausible length can pass those integer checks and still be dangling,
misaligned, outside one allocation, too short, or already freed. Such a value
is outside the API's calling contract.

### Rust separates ownership from borrowing

Rust gives each non-<code>Copy</code> value one current owner. Assignment or a
function call normally **moves** that value; the old binding can no longer be
used. A move transfers responsibility but need not physically copy allocation
bytes. When an initialized value reaches a drop scope, Rust runs its destructor
and then recursively destroys its fields according to the Reference's rules.

A reference borrows rather than owns:

| Rust view | Access during the borrow | Key exclusion rule in safe Rust |
| --- | --- | --- |
| <code>&amp;T</code> or <code>&amp;[T]</code> | shared read | referent is not mutated, except through permitted interior mutability |
| <code>&amp;mut T</code> or <code>&amp;mut [T]</code> | exclusive read/write | no overlapping active reference accesses the same referent |

Lifetimes let the borrow checker reject references that could outlive their
referent. They do not make an unbounded input bounded, prove a cryptographic
protocol, or guarantee that a destructor will run on every process termination
path. Rust's <code>mem::forget</code> is safe, reference-count cycles can leak,
and process termination can skip destructors. Unsafe code must remain
memory-safe even if destruction is leaked.

The example's <code>OwnedBuffer</code> is deliberately not
<code>Clone</code> or <code>Copy</code>. Moving it transfers the one C allocation
owner. <code>as_slice(&amp;self)</code> lends a shared view;
<code>as_mut_slice(&amp;mut self)</code> requires exclusive access. Safe code
cannot keep the shared view live and mutate through the exclusive one. The smoke
check compiles an intentionally conflicting program and requires rustc to
reject it.

### A slice is a borrowed range, not allocation proof

A Rust slice reference combines a data pointer and element count under a
lifetime. Safe slicing starts from an already valid owner and checks indexes.
Constructing a slice from raw parts is unsafe because pointer and length alone
do not prove its requirements.

For <code>std::slice::from_raw_parts</code>, Rust 1.96.1 requires a non-null,
aligned pointer valid for reads of the complete range; one allocation containing
the complete slice; initialized values; no forbidden mutation for the returned
shared lifetime; and a total size within the documented address bound. Even a
zero-length slice reference requires a non-null aligned pointer, so the example
returns <code>&amp;[]</code> directly for C's null-plus-zero empty representation.

**Pointer provenance** connects a pointer to the allocation from which access
authority derives. Two allocations can be numerically adjacent without forming
one valid slice. Converting an address integer back to a pointer does not, by
the number alone, establish authority to access an allocation. Rust's unsafe
code must satisfy the pointer and allocation model documented for the operation
it invokes. The Rust Reference warns that its unsafe-behavior list and exact
aliasing model are not a complete frozen formal model, so an unsafe ledger
should cite the operations and toolchain actually used rather than claim more.

C17's public draft does not use the current Rust provenance APIs as its model.
For C, this module uses “provenance” as an audit label for the standard's
allocation origin, lifetime, pointer arithmetic, access, and deallocation
requirements; it does not pretend that C17 standardized Rust's model.

### FFI needs an ownership state machine

An FFI declaration establishes calling syntax, not truth. Rust cannot inspect
whether the linked C function obeys its contract. A safe wrapper is sound only
if every safe call establishes every premise of its unsafe operation.

The example uses this state machine:

~~~text
Rust input &[u8] --borrowed for one call-->
C clone --success transfers fresh allocation-->
OwnedBuffer --moves transfer its one owner-->
shared/exclusive borrows --never outlive owner-->
wipe --allocation remains live and owned-->
destroy/Drop --C wipes, frees original base, resets empty-->
empty --a repeated destroy is harmless
~~~

The explicit Rust <code>destroy(self)</code> path suppresses ordinary
<code>Drop</code> before it calls C. On success the allocation is gone. If the
foreign destroy unexpectedly fails, the consumed state is quarantined and may
leak while the error reaches the caller; issuing an automatic second call could
double-free after a partial foreign failure. A production boundary must choose
and document quarantine, retry under a proven contract, or fail-stop behavior.
It must not advertise a recoverable error while secretly retrying in
<code>Drop</code>.

The contract must name at least:

1. linked symbol and reviewed artifact identity;
2. calling convention, target, structure layout, widths, signedness, and status
   values;
3. pointer non-null, alignment, provenance, initialized extent, and lifetime;
4. source/output non-overlap and the allowed read/write aliases;
5. whether a null pointer is accepted for zero length;
6. who owns an allocation before success, after success, and on failure;
7. whether any pointer is retained or any callback, thread, or unwind can occur;
8. exact base pointer and allocator required for destruction; and
9. length, work, and allocation bounds checked before entering C.

The wrapper checks 32 bytes before FFI, initializes an empty output, converts
only a successful result into <code>OwnedBuffer</code>, exposes no raw pointer,
and fails closed on all known or unknown statuses. Its unsafe blocks are narrow
because each ledger is attached to one operation. C undefined behavior can make
the combined Rust/C program undefined too; an <code>unsafe</code> block is not a
containment boundary.

### Zeroization evidence must say what it observed

NIST SP 800-57 Part 1 Rev. 5 defines key destruction at the goal level: remove
the traces so the key cannot be recovered physically or electronically. It also
requires planning for every key copy. A byte-store loop is one mechanism inside
that larger lifecycle, not proof that the goal has been achieved.

The example issues C stores through a volatile-qualified byte pointer, reads
the selected live allocation back as zeros in the harness, passes its original
base to <code>free</code>, and resets the owner. The Rust helper's
<code>write_volatile</code> has the documented compiler guarantee that the
selected in-allocation writes are not elided and are ordered with respect to
other externally observable events. These are useful, bounded observations.

Neither observation proves that all secret copies, compiler temporaries,
registers, CPU caches, allocator remnants, swap, crash dumps, hibernation
images, logs, backups, snapshots, device remapping areas, or physical media are
erased. The separate source array in the example intentionally remains
unchanged after the owned clone is wiped. A prior copy is a different region
and needs its own inventory and destruction action.

Ordinary destruction is weaker still. Rust's <code>Vec</code> documentation
does not promise to overwrite removed or dropped elements and warns against
relying on removal or drop for erasure. A normal store can be removed when the
optimizer concludes it has no observable effect. A volatile store or a
specialized zeroization primitive can strengthen compiler-level evidence for a
selected object, but cannot by itself establish system-wide or physical media
sanitization.

Use an evidence ladder instead of a binary claim:

| Level | Defensible statement |
| --- | --- |
| Source review | the selected routine attempts a bounded wipe before release |
| Executed test | this build read the selected live bytes back as zero |
| Compiler/tool evidence | this selected primitive carries documented non-elision behavior for the tested toolchain |
| System controls | process, swap, dump, backup, allocator, and hardware policies were separately assessed |
| Destruction claim | every inventoried copy and representation was handled under an applicable destruction procedure |

The first three levels do not imply the fifth.

### Bounds make ownership review finite

The example accepts at most 32 bytes. C makes at most 32 copy accesses, 32 sum
accesses, and 32 wipe stores for a live owner. One successful owner holds one
allocation of at most 32 bytes plus a two-field descriptor. The model does not
claim an exact allocator, object-header, stack, cache, register, or resident-set
size.

The smoke check copies all sources into one temporary directory, builds C with
<code>cc -std=c17</code> and Rust with
<code>rustc +1.96.1 --edition=2024</code>, and writes every object and executable
under that temporary path. It performs no network operation. Passing establishes
only the source, toolchain, target, and cases actually run.

## Worked example

Start with Rust source bytes <code>[1, 2, 3, 4]</code>.

1. <code>OwnedBuffer::new</code> validates length 4 before FFI. Its shared slice
   is readable for the synchronous call and is disjoint from the local empty
   output descriptor.
2. C allocates four bytes, copies the values, and updates the output only after
   allocation and copy. Success transfers ownership of that allocation to the
   Rust wrapper. C retains no source pointer.
3. Moving <code>first_owner</code> to <code>moved_owner</code> transfers the
   wrapper value. It does not create a second allocation owner.
4. A shared slice reads <code>[1, 2, 3, 4]</code>. An exclusive slice then changes
   the owned allocation's second byte to 9. The separate source remains
   <code>[1, 2, 3, 4]</code>.
5. C's bounded sum observes 17. Its output is a separate uniquely writable
   <code>u64</code>; C retains neither pointer.
6. Wipe performs four stores in the owned allocation. Readback through that
   owner observes <code>[0, 0, 0, 0]</code>. The source copy still contains the
   original bytes, demonstrating why a single-region wipe is not key
   destruction proof.
7. Destroy wipes again, passes the original base to the matching C
   <code>free</code>, and resets the raw descriptor. The Rust value is consumed,
   so safe code cannot use its slices afterward.

For an empty input, the boundary uses C's <code>{NULL, 0}</code> representation
without constructing a Rust slice from a null raw pointer. For 33 bytes, Rust
returns <code>TooLong</code> before FFI. The raw C harness separately confirms
that null with a positive length, a nonempty output owner, and an inconsistent
null-plus-one state are rejected before byte access.

## Check your understanding

1. Why can a non-null C pointer with length 4 still be invalid?
2. Does moving <code>OwnedBuffer</code> copy its allocation or create a second
   owner?
3. Why does the wrapper special-case null plus zero instead of calling
   <code>from_raw_parts(NULL, 0)</code>?
4. What safe Rust rule rejects mutation while a shared slice remains live?
5. Why is <code>{NULL, 1}</code> rejection useful but insufficient to validate a
   fabricated <code>{non_null, 1}</code> value?
6. What does the wipe readback prove, and what does it not prove?
7. Can sound unsafe Rust require its destructor to run on every execution?

**Answers:** (1) it may be dangling, misaligned, too short, outside one
allocation, uninitialized, or derived without valid access authority; (2) no,
the move transfers the one owner and need not move the allocation bytes; (3)
Rust slice references require non-null alignment even for length zero; (4) a
live shared reference excludes overlapping mutation except through permitted
interior mutability; (5) shape checks cannot prove origin, extent, lifetime, or
prior deallocation of a plausible non-null pointer; (6) it proves the tested
selected live allocation read back as zero after the issued stores, not that all
copies or hardware/media representations were erased; (7) no, destructor leaks
are possible in safe Rust, so memory safety cannot depend on universal Drop
execution.

## Next step

Complete the [lab](lab.md), including the independent owner-state trace and the
observed deliberate failure. Then complete the transfer
[assessment](assessment.md). Passing requires at least 80/100 and every
critical criterion in the [rubric](rubric.md).

## Sources

- ISO/IEC JTC 1/SC 22/WG14, [N2176, C17 ballot
  draft](https://www.open-std.org/jtc1/sc22/wg14/www/docs/n2176.pdf), especially
  §§3.15, 5.1.2.3, 6.2.4, 6.5, 6.7.3, and 7.22.3. N2176 is the public WG14
  ballot draft, not the separately published ISO/IEC 9899:2018 standard.
- The Rust Project, [The Rust Programming Language: Understanding
  Ownership](https://doc.rust-lang.org/1.96.1/book/ch04-00-understanding-ownership.html)
  and [References and
  Borrowing](https://doc.rust-lang.org/1.96.1/book/ch04-02-references-and-borrowing.html).
- The Rust Project, [Rust Reference: Behavior considered
  undefined](https://doc.rust-lang.org/1.96.1/reference/behavior-considered-undefined.html),
  [destructors](https://doc.rust-lang.org/1.96.1/reference/destructors.html), and
  [external
  blocks](https://doc.rust-lang.org/1.96.1/reference/items/external-blocks.html).
- The Rust Project, Rust 1.96.1 standard-library documentation for
  [<code>slice::from_raw_parts</code>](https://doc.rust-lang.org/1.96.1/std/slice/fn.from_raw_parts.html),
  [<code>ptr::write_volatile</code>](https://doc.rust-lang.org/1.96.1/std/ptr/fn.write_volatile.html),
  [<code>Vec</code> guarantees](https://doc.rust-lang.org/1.96.1/std/vec/struct.Vec.html),
  and [<code>mem::forget</code>](https://doc.rust-lang.org/1.96.1/std/mem/fn.forget.html).
- The Rust Project, [Rustonomicon: FFI](https://doc.rust-lang.org/1.96.1/nomicon/ffi.html),
  [destructors](https://doc.rust-lang.org/1.96.1/nomicon/destructors.html), and
  [leaking](https://doc.rust-lang.org/1.96.1/nomicon/leaking.html).
- Elaine Barker, NIST, [SP 800-57 Part 1 Rev. 5: Recommendation for Key
  Management](https://csrc.nist.gov/pubs/sp/800/57/pt1/r5/final), especially
  §8.3.4 on key destruction, and the NIST CSRC [key-destruction
  definition](https://csrc.nist.gov/glossary/term/key_destruction).
- NIST, [SP 800-88 Rev. 2: Guidelines for Media
  Sanitization](https://csrc.nist.gov/pubs/sp/800/88/r2/final), for the separate
  clear, purge, and destroy treatment of storage media. This module does not
  equate an in-process byte wipe with media sanitization.
- [Assessment system](../../../docs/assessment-system.md), independent evidence
  and pass policy.
