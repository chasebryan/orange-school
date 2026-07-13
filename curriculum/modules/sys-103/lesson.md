# Objects, linking, calling conventions, and ABIs

A function call across source files or languages succeeds only when several
contracts agree. Source declarations must describe compatible types. The
compiler must emit definitions and references in a format the linker
understands. The linker or loader must bind each reference to the intended
definition. Both sides must agree on layout, calling convention, ownership,
failure, and unwinding for the exact target. A successful build establishes
some of those facts for one artifact; it does not create a portable ABI by
accident.

This module uses C17 and Rust 1.96.1 edition 2024 to expose those boundaries.
The supplied check builds only in a temporary directory. It probes the actual
target instead of hard-coding one platform's offsets or symbol spelling.

## Learning objectives

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

## Prerequisites

Pass <code>sys-102</code>. You should be able to reason about object lifetime,
regions, borrowing, aliasing, mutation, zeroization limits, and unsafe
preconditions. You should also be able to compile a bounded C17 function and
call it through a narrow Rust wrapper from <code>prg-104</code>.

The reference envelope provides <code>cc</code> with C17 support and the exact
<code>rustc +1.96.1</code> toolchain. The smoke check detects
<code>ar</code>, <code>nm</code>, <code>readelf</code>, and
<code>objdump</code> before invoking them. A missing optional inspector changes
the available evidence, not the object model. If a required compiler is
missing or the Rust version differs, record a blocker rather than changing a
global installation.

## Lesson

### Translation units are the C language boundary

After preprocessing, one C source file plus the headers it includes forms a
**translation unit**. A declaration tells the compiler that an identifier and
type exist. A definition supplies the function body or object storage. For
example, [the header](examples/abi_contract.h) declares
<code>sys103_checksum</code>, while
[checksum.c](examples/checksum.c) defines it.

The C17 language specifies preprocessing, translation units, declarations,
definitions, compatible types, and identifier linkage. It does not require an
ELF file, a <code>.o</code> suffix, a static archive, a dynamic loader, or a
particular command-line linker. Those belong to the implementation and
platform.

This module observes a common native pipeline:

~~~text
abi_contract.h ----included----> checksum.c ------compile------> checksum.o
             \-----------------> layout_probe.c --> layout_probe.o

checksum.o + layout_probe.o --archive if ar exists--> libsys103.a

c_harness.c --compile--> c_harness.o --link with library--> c_harness
ffi_probe.rs --------------------rustc and link---------------> ffi_tests
~~~

A **relocatable object** contains code or data that has not yet been assigned
all final addresses. It is input to another link step and normally is not a
standalone process image. An **executable** has the target's process-image
metadata and an entry point suitable for loading. A filename extension is a
convention; inspect the artifact and its producing command instead of deciding
from the name alone.

Compilation and linking answer different questions. Compiling
<code>c_harness.c</code> can succeed while leaving an unresolved reference to
<code>sys103_checksum</code>. The link succeeds only when a compatible
definition is selected. The supplied
[unresolved consumer](examples/unresolved_consumer.c) deliberately references
a definition that is never supplied. Its successful compilation followed by
failed link is failure-sensitive evidence for that distinction.

### Sections, symbols, and relocations connect objects

An object format commonly groups content into **sections**. Examples include
machine instructions, initialized writable data, read-only data, zero-filled
storage descriptions, symbol/string tables, relocations, and debugging or
unwind metadata. Those names and meanings are format-specific. ELF often uses
names such as <code>.text</code>, <code>.data</code>,
<code>.rodata</code>, <code>.bss</code>, <code>.symtab</code>, and
<code>.rela.text</code>; C17 does not.

A **symbol** is object-format metadata describing a definition or reference,
often with a name, binding, type, section, value, and size. A definition in
one object can satisfy an undefined reference in another. A **relocation**
identifies a place whose encoded value depends on final placement or symbol
binding. The linker or loader applies the target relocation rule after it knows
the relevant address or offset.

Use each inspection tool for the claim it supports:

| Tool, when available | Useful observation | Unsupported conclusion |
| --- | --- | --- |
| <code>nm object</code> | Displayed definitions/references and their tool-specific type letters | Every source identifier must appear with this spelling |
| <code>readelf -S/-s/-r</code> | ELF sections, symbols, and relocations | Every target uses ELF |
| <code>objdump -h/-t/-r</code> | Format-dependent headers, symbols, and relocations | Displayed addresses are source-language semantics |
| <code>readelf -d</code> or <code>objdump -p</code> | Dynamic metadata in this executable, if supported | The program is wholly static or portable because one dependency is absent |

Optimization, link-time optimization, section garbage collection, stripping,
and symbol localization can remove, merge, rename, or hide evidence. Preserve
tool versions, flags, target, and the inspected artifact hash with the output.

### Linkage, symbol visibility, and library kind are separate

C17 identifiers can have **external linkage**, **internal linkage**, or no
linkage. Compatible declarations with external linkage can denote the same
entity across translation units. At file scope, this module's
<code>sys103_checksum</code> definition has external linkage. The
<code>static fold_byte</code> helper has internal linkage and is private to
<code>checksum.c</code>.

Do not overload the word “static”:

- file-scope <code>static</code> on <code>fold_byte</code> gives the identifier
  internal linkage;
- block-scope <code>static</code> gives an object static storage duration; and
- a **static library** is a toolchain archive from which a linker selects
  relocatable object content.

Likewise, an <code>extern</code> declaration does not request dynamic linking.
It describes linkage and a declaration context in C. **Symbol visibility**—for
example whether a definition is exported from a shared object—is a separate
object-format and toolchain policy. External C linkage is therefore neither a
promise that <code>nm</code> will show a universal spelling nor a promise that a
dynamic loader can import the symbol.

A static link commonly copies selected object content into the output during
the link. A dynamic link commonly leaves dependency and import metadata so a
runtime loader can map shared objects and resolve dynamic symbols. Exact archive
selection, interposition, search order, versioning, lazy binding, and loader
behavior are platform facts. The example archives its own two C objects when
<code>ar</code> is usable, but its executable may still dynamically depend on a
platform C runtime.

### An ABI is below a source API

An application programming interface can say “call
<code>checksum(request, payload)</code>.” An **application binary interface**
must additionally settle how compiled artifacts agree. Relevant facts include:

- target architecture, operating system, object format, and data model;
- external symbol spelling and binding;
- parameter and return-value representation;
- which registers or stack locations carry values;
- stack alignment and who preserves which registers;
- aggregate layout and aggregate passing rules;
- variadic-call behavior;
- thread-local storage and dynamic-link rules; and
- whether and how unwinding may cross a call boundary.

C17 does not define one C ABI. Rust <code>extern "C"</code> asks Rust to use
the C ABI supported for the selected target. It does not mean that one binary
can move unchanged between x86-64 Linux, AArch64 macOS, and 32-bit Windows.
Record <code>rustc +1.96.1 -vV</code>, the C compiler identity, build flags, and
the final target alongside ABI evidence.

### Layout has size, alignment, offsets, and padding

The **size** of a type is the spacing needed for array elements. Its
**alignment** restricts valid addresses. A structure field has an offset from
the structure's beginning. An implementation may place unnamed **padding**
between fields or after the last field so that each field and the next array
element meet alignment requirements.

C17 preserves structure member order and permits unnamed padding within and at
the end, but not before the first member. <code>sizeof</code>,
<code>_Alignof</code>, and <code>offsetof</code> observe the current C
implementation. They are not a substitute for a cross-language comparison.

Rust's default <code>repr(Rust)</code> is not a C FFI layout contract.
<code>#[repr(C)]</code> applies the Rust Reference's target-C representation
rules. The [Rust probe](examples/ffi_probe.rs) defines the same field sequence
and compares <code>size_of</code>, <code>align_of</code>, and
<code>offset_of!</code> with functions compiled by C. Even equal layout does
not by itself prove that every aggregate is passed identically as a function
argument; calling-ABI compatibility is a separate obligation.

The example has two structures:

| Structure | Fields | Purpose |
| --- | --- | --- |
| <code>sys103_request</code> | <code>uint32_t</code>, <code>uint16_t</code>, <code>uint16_t</code> | Actual FFI request with target-probed C/Rust layout |
| <code>sys103_layout_demo</code> | <code>uint8_t</code>, <code>uint32_t</code>, <code>uint16_t</code> | Makes possible inter-field and tail padding visible |

One common target reports request size 8/alignment 4 and demo size 12/alignment
4. Those numbers are an example observation, not the pass condition. The tests
pass when C and Rust agree on the values measured for the current build.

### Fixed width narrows an FFI contract

C's <code>int32_t</code>, <code>uint16_t</code>, and related exact-width typedefs
are optional: an implementation defines them only when it provides a matching
type with exactly that width and no padding bits. Successful compilation proves
availability for this implementation. Rust <code>i32</code>,
<code>u16</code>, and <code>u32</code> have the named widths. The target ABI
must still agree on passing those types.

The example uses fixed-width integers for status, lengths, fields, and result.
It avoids C <code>long</code>, C <code>enum</code>, C
<code>_Bool</code>, Rust <code>bool</code>, Rust enums, and
<code>size_t</code>/<code>usize</code> at the boundary because their width,
valid-value, or ABI mapping needs extra target-specific work. It never passes a
Rust <code>String</code>, <code>Vec</code>, slice, trait object, reference, or
default-layout structure directly to C.

Pointer width is not payload length. A raw pointer does not carry allocation
extent, initialized state, lifetime, alignment, mutability, aliasing, or
ownership. Keep the length separate, bounded, and checked before access.

### The safe wrapper owns the boundary contract

The C function accepts a request pointer, payload pointer, fixed-width payload
length, and output pointer. It returns a fixed-width status. Its validation
order is part of the contract:

1. reject null output or request before dereferencing either;
2. reject a length above 16 or inconsistent with the request;
3. reject a kind outside 0 through 3;
4. reject null payload when length is nonzero;
5. read exactly the validated number of bytes;
6. write output only on success; and
7. retain no pointer after the synchronous return.

Non-null still does not prove a pointer valid. The caller must establish live,
aligned, initialized storage of sufficient extent and the required aliasing
relationship. C generally cannot recover those facts from the pointer value.

The Rust safe wrapper accepts <code>&[u8]</code>, checks kind and length before
unsafe code, constructs a local <code>#[repr(C)]</code> request and output, and
uses null only for the explicitly accepted empty-payload case. Its single
unsafe call has a numbered assumption ledger. Known C statuses become distinct
Rust errors; an unknown status fails closed rather than being interpreted as a
result.

Ownership remains with Rust. C receives borrowed access only for the call and
may not mutate or retain the inputs. The local output is exclusively writable
and disjoint from both inputs. If a future C implementation stores a pointer,
starts asynchronous work, invokes a callback, or writes on error, the wrapper
becomes unsound even when its Rust signature has not changed.

### Panic and unwind policy must be explicit

The example uses the non-unwinding <code>"C"</code> ABI and requires the C
callee not to unwind or call back into panicking Rust. A Rust panic or foreign
exception must not cross a boundary whose ABI does not permit unwinding.
Choosing <code>"C-unwind"</code> changes the ABI contract; it is not a general
repair for uncaught failures.

For Rust functions exported to C, prefer a non-panicking core, validate all
inputs, translate errors to a declared status, and keep destructor/ownership
effects explicit. <code>catch_unwind</code> can catch some unwinding Rust
panics when used correctly, but it does not catch aborting panics and does not
make arbitrary foreign exceptions or invalid pointers safe. Document the
process-failure policy as well as the return-value policy.

### Evidence is target-scoped

The smoke check records, inside its temporary workspace:

- hashes of the copied sources;
- C and Rust compiler identities plus the Rust host target;
- detected archive and inspection capabilities;
- object, archive, executable, and test build results;
- C/Rust agreement on layout and behavior;
- symbol/section/relocation output hashes when supported; and
- the nonzero status and diagnostic from the deliberately unresolved link.

Passing tests support only the paths executed. They do not prove every C
caller honors pointer contracts, every optimizer preserves an assumption, the
binary works on another target, a dynamic loader selects the intended library,
or Orange implements this ABI.

## Worked example

For request ID 100, kind 2, and payload bytes <code>02 04 08</code>, the header
length is 3. The C function starts at <code>100 + 2 + 3 = 105</code> and applies
the declared modulo-<code>2^32</code> fold:

~~~text
105 * 33 + 2 = 3,467
3,467 * 33 + 4 = 114,415
114,415 * 33 + 8 = 3,775,703
~~~

The C harness and Rust wrapper both require 3,775,703. They also test an empty
payload, exactly 16 bytes, an invalid kind, an excessive or mismatched length,
and checked null cases with unchanged error output.

At the artifact level, <code>checksum.o</code> defines an externally linked
checksum symbol while <code>c_harness.o</code> references it. The internal
<code>fold_byte</code> helper belongs only to the checksum translation unit.
The link selects the checksum definition from <code>libsys103.a</code> when an
archive tool is available. A separate object references
<code>sys103_missing_definition</code>; compilation succeeds, linking without a
definition fails, and no executable is accepted.

Run the complete observation:

~~~sh
cd curriculum/modules/sys-103
PYTHONDONTWRITEBYTECODE=1 python3 checks/lab_smoke.py
~~~

The exact final line is <code>sys-103 lab smoke: PASS</code>.

## Check your understanding

1. Why can one translation unit compile even though its later link will fail?
2. What different facts do a section, symbol, and relocation record?
3. Why are C internal linkage, hidden symbol visibility, and a static library
   three different ideas?
4. Does <code>extern "C"</code> select one calling convention for every target?
5. Why compare size, alignment, and every offset rather than only
   <code>sizeof</code>?
6. Why are <code>uint32_t</code> and Rust <code>u32</code> narrower choices than
   C <code>long</code> and a Rust enum at this boundary?
7. Which pointer obligations remain untestable from a non-null value and a
   length?
8. What must happen to an unknown C status? Can a panic cross this
   non-unwinding boundary?
9. Why can an <code>nm</code> observation change after optimization or stripping
   without changing the C source declarations?

**Answers:** (1) compilation can leave unresolved symbol references for the
linker; (2) sections group object content, symbols describe definitions or
references, and relocations identify values to adjust after placement or
binding; (3) they are respectively a C identifier rule, an object/toolchain
export rule, and an archive/link strategy; (4) no, it selects the target's C
ABI; (5) equal total size can hide incompatible field offsets or alignment;
(6) they exclude several width and valid-value ambiguities, subject to target
ABI verification; (7) provenance, lifetime, initialized extent, alignment,
aliasing, mutability, and ownership; (8) fail closed, and unwinding is forbidden
by this contract; (9) those build transformations change retained binary
metadata and reachability.

## Next step

Complete the [lab](lab.md) by extending the interface in a temporary copy and
preserving target evidence. Then complete the independent
[assessment](assessment.md). Passing requires at least 80/100 and every
critical criterion in the [rubric](rubric.md). The next systems module uses
this ABI discipline when reasoning about targets, SIMD features, and dispatch.

## Sources

- ISO/IEC JTC 1/SC 22/WG14, [N2176, public C17 ballot
  draft](https://www.open-std.org/jtc1/sc22/wg14/www/docs/n2176.pdf), especially
  §§5.1.1.1–5.1.1.2, 6.2.2, 6.2.8, 6.5.3.4, 6.7.2.1, 6.9, and 7.20.1.1.
  N2176 is public draft evidence, not the separately published ISO/IEC
  9899:2018 text.
- The Rust Project, [Rust 1.96.1 Reference: type
  layout](https://doc.rust-lang.org/1.96.1/reference/type-layout.html),
  including size, alignment, <code>repr(Rust)</code>, and
  <code>repr(C)</code> guarantees.
- The Rust Project, [Rust 1.96.1 Reference: external
  blocks](https://doc.rust-lang.org/1.96.1/reference/items/external-blocks.html),
  including target C ABI selection and unwind ABI variants.
- The Rust Project, [Rust Nomicon: FFI and
  unwinding](https://doc.rust-lang.org/1.96.1/nomicon/ffi.html#ffi-and-unwinding),
  for permitted and forbidden unwind behavior at foreign boundaries.
- System V ABI, [ELF sections](https://refspecs.linuxfoundation.org/elf/gabi4%2B/ch4.sheader.html),
  [symbol tables](https://refspecs.linuxfoundation.org/elf/gabi4%2B/ch4.symtab.html),
  and [relocations](https://refspecs.linuxfoundation.org/elf/gabi4%2B/ch4.reloc.html).
  These define ELF facts, not C language guarantees or every platform ABI.
- GNU Binutils, [<code>ar</code>](https://sourceware.org/binutils/docs/binutils/ar.html),
  [<code>nm</code>](https://sourceware.org/binutils/docs/binutils/nm.html),
  [<code>readelf</code>](https://sourceware.org/binutils/docs/binutils/readelf.html),
  and [<code>objdump</code>](https://sourceware.org/binutils/docs/binutils/objdump.html)
  manuals. Other implementations may expose different options and output.
- [Assessment system](../../../docs/assessment-system.md), independent
  evidence and pass policy.
