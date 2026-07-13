# C and Rust systems bridge

C exposes memory and calling conventions directly. Rust puts ownership,
borrowing, and lifetime checks around the same machine resources, then requires
an explicit <code>unsafe</code> boundary when those guarantees cannot be
verified by the compiler. This module teaches a narrow, bounded bridge; it does
not claim that either language makes foreign code safe automatically.

## Learning objectives

- **PRG-104-01:** Compare C memory, pointer, and bounds contracts with Rust
  ownership and borrowing using concrete traces.
- **PRG-104-02:** Build and test bounded C and Rust functions with explicit
  success and error behavior.
- **PRG-104-03:** Integrate one C function through a narrow Rust FFI wrapper and
  document every unsafe assumption.

## Prerequisites

Pass <code>prg-102</code> and <code>prg-103</code>. You should already be able
to choose collections, state input and resource bounds, write focused tests,
use explicit result types, reproduce failures, and read command exit status.
No prior C, Rust, pointer, ownership, linker, or FFI knowledge is assumed.

The reference environment requires:

~~~sh
cc --version
rustc +1.96.1 --version
~~~

The lab compiles C17 with <code>cc</code> and selects the pinned Rust toolchain
with <code>rustc +1.96.1 --edition=2024</code>. A compiler translates one
source file into machine code. A linker combines separately compiled code and
resolves a symbol such as <code>bounded_sum_i32</code>. If either tool is
unavailable or the Rust version differs, record the blocker rather than
changing global configuration.

## Lesson

**C represents memory as objects and addresses.** An
<code>int32_t values[3]</code> array contains three consecutive signed
32-bit integer objects. In most function calls, that array is passed as a
pointer to its first element:

~~~c
int bounded_sum_i32(
    const int32_t *values,
    size_t len,
    int64_t *out_sum
);
~~~

A <code>.h</code> header publishes declarations shared by callers and the
implementation. A <code>.c</code> source supplies definitions.
<code>#include "bounded_sum.h"</code> asks the C preprocessor to make those
declarations visible before compilation. Header guards prevent accidental
duplicate inclusion.

Read the signature from the inside out:

| C text | Meaning |
| --- | --- |
| <code>int32_t</code> | An available exact-width signed 32-bit integer type |
| <code>size_t</code> | The unsigned type used for object sizes and indexes |
| <code>const int32_t *values</code> | Pointer used to read, not write, input integers |
| <code>int64_t *out_sum</code> | Pointer through which one 64-bit result may be written |
| <code>values[index]</code> | Read the indexed object after its validity is established |
| <code>&amp;output</code> | Form a pointer to the local output object |
| <code>*out_sum</code> | Access the object designated by the output pointer |
| <code>NULL</code> | A null pointer value that designates no object |

The pointer does not carry its length, lifetime, allocation size, alignment, or
nullability. Those facts are a contract between caller and callee.
<code>const</code> says this function will not modify values through that
pointer; it does not prove that the memory is valid or unaliased.

For this module's C function, the caller promises:

- <code>out_sum</code> points to one live, aligned, writable
  <code>int64_t</code>;
- <code>len</code> is at most 8;
- if <code>len &gt; 0</code>, <code>values</code> points to at least
  <code>len</code> live, aligned, readable <code>int32_t</code> objects; and
- both pointers remain valid for the whole call.

The callee checks what it can before dereferencing: output null, length, then
input null. C cannot generally determine whether an arbitrary non-null pointer
has the promised provenance, lifetime, alignment, or allocation extent.
Passing a pointer that violates those requirements and then dereferencing it
has undefined behavior. A test run cannot turn an invalid pointer into a valid
contract.

The return status is separate from the result:

| Status | Meaning | Output behavior |
| ---: | --- | --- |
| 0 | Success | Writes the mathematical sum |
| 1 | Required pointer is null | Leaves output unchanged when an output exists |
| 2 | Length exceeds 8 | Leaves output unchanged |

With at most eight <code>int32_t</code> values, the mathematical sum fits in
<code>int64_t</code>. The implementation widens each value before addition.
That arithmetic argument and the pointer contract are separate obligations.

**Trace C one memory action at a time.** For values
<code>[4, -1, 7]</code>, length 3, and output initialized to -99:

1. Validate the output pointer; do not dereference it yet.
2. Validate <code>3 &lt;= 8</code>.
3. Validate the values pointer because length is nonzero.
4. Read only indexes 0, 1, and 2 while state <code>sum</code> changes
   0 → 4 → 3 → 10.
5. Write 10 through <code>out_sum</code>.
6. Return status 0.

If length is 9, step 2 returns status 2. No input element or output object is
accessed. Validation order is observable safety behavior.

**Rust ties safe references to ownership and lifetime rules.** A value has an
owner responsible for its lifetime. Moving a non-<code>Copy</code> value
transfers ownership. A shared borrow <code>&T</code> permits reading; a mutable
borrow <code>&mut T</code> permits exclusive mutation. The compiler prevents a
mutable borrow from overlapping active shared borrows in safe Rust.

A slice <code>&[i32]</code> is a shared borrowed view containing a pointer and
a length. Safe construction guarantees that its elements are initialized,
aligned, readable for the borrow lifetime, and not mutably aliased through safe
code during that borrow.

~~~rust
let mut values = vec![4_i32, -1, 7];
let view = &values[..];
let result = rust_bounded_sum(view);
// values.push(9); would be rejected here if view is used afterward
assert_eq!(result, Ok(10));
~~~

<code>Vec&lt;i32&gt;</code> is a growable, owned sequence.
<code>&amp;values[..]</code> borrows all its elements as a slice.
<code>Result&lt;T, E&gt;</code> is either <code>Ok(T)</code> or
<code>Err(E)</code>; callers can <code>match</code> those variants without
confusing an error with a valid numeric result. Rust raw pointers
<code>*const T</code> and <code>*mut T</code>, unlike references, carry no
compiler-enforced lifetime or aliasing promise.

The vector owns its allocation. <code>view</code> borrows all three elements.
The function borrows the slice without taking ownership, validates its length,
and returns <code>Result&lt;i64, RustSumError&gt;</code>. Safe Rust rules out
null and dangling slice references, but it does not choose the eight-item
application bound; the function must still enforce that contract.

| Concern | C pointer plus length | Rust shared slice |
| --- | --- | --- |
| Length | Separate value maintained by caller | Carried with the slice |
| Null | Must be specified and checked | A safe reference is non-null |
| Lifetime | Caller contract | Checked for safe borrows |
| Alignment/initialized memory | Caller contract | Required by safe reference construction |
| Aliasing | Must be documented and maintained | Shared borrow prevents safe mutation overlap |
| Application maximum | Explicit runtime check | Explicit runtime check |
| Failure | Integer status plus output contract | <code>Result</code> variant |

**Build each side with explicit language modes.** After copying sources into
its temporary workspace, the smoke check uses these essential invocations:

~~~sh
cc -std=c17 -Wall -Wextra -Wpedantic -Werror \
    -c bounded_sum.c -o "$workspace/bounded_sum.o"
rustc +1.96.1 --edition=2024 --test -D warnings \
    -C "link-arg=$workspace/bounded_sum.o" \
    ffi_bridge.rs -o "$workspace/ffi_tests"
~~~

<code>-std=c17</code> selects the C17 language mode. Warning flags make common
mistakes visible and turn warnings into failures. Rust edition 2024 selects
source-language rules; it is not the compiler version. Exact commands, compiler
versions, target, source identities, test output, and statuses belong in the
evidence record.

**FFI crosses a compiler-enforced boundary.** FFI means foreign function
interface. Rust declares a C symbol in an <code>unsafe extern "C"</code> block.
Calling it is unsafe because rustc cannot inspect the C implementation or prove
the pointer and ABI contracts. The module exposes only a safe wrapper accepting
<code>&[i32]</code>, validates length before the call, creates one local output,
and maps every known or unknown C status to <code>Result</code>.

<code>extern "C"</code> selects the C calling convention for the target.
<code>unsafe</code> does not disable Rust's checks or certify the operation; it
marks a place where the programmer must establish obligations rustc cannot.
Keep raw pointer creation and the call inside the smallest reviewable region.

Keep the unsafe block narrow, then document every premise needed for that one
call:

1. The linked symbol is the intended C definition.
2. Rust and C agree on calling convention, target, parameter widths, signedness,
   return type, and status values.
3. The slice pointer is readable and aligned for exactly its length.
4. The output pointer is uniquely writable for one <code>i64</code>.
5. The empty null-pointer convention matches.
6. C honors bounds, does not write through the input, and writes output only on
   success.
7. C retains neither pointer and finishes synchronously.
8. C neither unwinds into Rust nor calls back with hidden aliasing.
9. Header constants and Rust constants match the compiled objects.
10. Tests and review refer to the same source and target artifacts.

The safe wrapper's signature should make no promise stronger than those
premises support. If an unexpected status appears, fail closed with an explicit
error rather than treating it as success.

**Host evidence is not Orange evidence.** Compiling and testing these C and Rust
files demonstrates prerequisite host-language skills for the exact tools and
cases run. It does not test Orange syntax, semantics, code generation, ABI,
FFI, verification, packages, artifacts, or professional workflows.

## Worked example

The supplied [C implementation](examples/bounded_sum.c), [C
harness](examples/c_harness.c), and [Rust bridge](examples/ffi_bridge.rs) all
use maximum length 8.

For <code>[4, -1, 7]</code>:

| Boundary | Validated state | Reads | Result |
| --- | --- | --- | --- |
| C function | non-null output, length 3, non-null input | three <code>int32_t</code> objects | status 0, output 10 |
| Safe Rust function | slice length 3 | three borrowed values | <code>Ok(10)</code> |
| Rust FFI wrapper | slice length 3, local output, declared ABI assumptions | C performs three reads | <code>Ok(10)</code> |

For an empty input, safe Rust supplies a valid empty slice. The wrapper passes
null with length zero because the C contract explicitly accepts that pair.
Neither implementation reads an element, and both return zero.

For nine values, both safe functions reject the length. The wrapper returns
<code>TooManyItems</code> before entering unsafe code. The raw C harness also
calls C with length 9 and confirms status 2 and unchanged output. A separate raw
C case supplies null with length 1; the function returns status 1 before any
read. Safe Rust cannot construct that invalid slice.

## Check your understanding

1. Why are a non-null C pointer and a length insufficient to prove a valid
   read?
2. What additional information does <code>&[i32]</code> give Rust compared
   with <code>*const i32</code>?
3. Why does the safe Rust function still check a maximum length?
4. Why should C write the output only after every input has been validated and
   processing succeeds?
5. What must a safe wrapper do with an unknown C status?
6. Do passing C and Rust tests demonstrate an Orange FFI?

**Answers:** (1) lifetime, alignment, initialized extent, provenance, and
aliasing may still be wrong; (2) a safe shared slice carries length and a
compiler-checked borrow contract; (3) ownership rules do not enforce an
application resource limit; (4) failure then leaves no partial success result;
(5) return an explicit error and fail closed; (6) no, they are host-language
prerequisite evidence only.

## Next step

Run the [lab](lab.md), preserve the compiler and test record, and review every
line of the unsafe assumption ledger. Then complete the
[independent assessment](assessment.md). Passing requires at least 80/100 and
all critical criteria in the [rubric](rubric.md).

## Sources

- ISO/IEC JTC 1/SC 22/WG14, [N2176, C17 ballot
  draft](https://www.open-std.org/jtc1/sc22/wg14/www/docs/n2176.pdf), 2017.
  This is the public WG14 ballot draft, not the published ISO standard.
- ISO/IEC 9899:2018, *Programming Languages — C* (C17), clauses 6.2.5,
  6.5.3.2, 6.7.6.3, and 7.20.1.1 for types, pointer operators, function
  declarators, and exact-width integers.
- Rust Project, [The Rust Programming Language: Understanding
  Ownership](https://doc.rust-lang.org/book/ch04-00-understanding-ownership.html),
  ownership, borrowing, references, and slices.
- Rust Project, [Rust Reference: External
  blocks](https://doc.rust-lang.org/reference/items/external-blocks.html),
  edition-2024 unsafe external declarations and ABI contracts.
- Rust Project, [Rustonomicon: FFI](https://doc.rust-lang.org/nomicon/ffi.html),
  foreign declarations, linking, callbacks, and unwinding hazards.
- [Assessment system](../../../docs/assessment-system.md), independent evidence
  and pass policy.
