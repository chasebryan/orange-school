# Lab: extend and audit a C/Rust object boundary

## Goal

Reproduce the supplied multi-object build, inspect only the artifact properties
your target tools expose, then add a separately compiled bounded operation with
a compatible C/Rust ABI and complete ownership, error, and unwind contract.

## Setup

From the repository root, establish the unchanged baseline:

~~~sh
cd curriculum/modules/sys-103
PYTHONDONTWRITEBYTECODE=1 python3 checks/lab_smoke.py
smoke_status=$?
printf 'smoke status: %s\n' "$smoke_status"
~~~

The check must print <code>sys-103 lab smoke: PASS</code> and return status 0.
It compiles copied sources only in a fresh temporary directory. It performs no
package installation or global configuration.

Create a separate workspace and copy the example sources:

~~~sh
workdir="$(mktemp -d)"
mkdir -- "$workdir/src" "$workdir/build" "$workdir/evidence"
cp -- examples/abi_contract.h examples/checksum.c examples/layout_probe.c \
  examples/c_harness.c examples/ffi_probe.rs \
  examples/unresolved_consumer.c "$workdir/src/"
cd -- "$workdir"
pwd
~~~

Keep that absolute path. Every edited source, object, archive, executable, log,
hash, and status record must remain below it. Detect capabilities before using
them:

~~~sh
for tool in cc rustc ar nm readelf objdump; do
  if tool_path="$(command -v "$tool")"; then
    printf '%s\t%s\n' "$tool" "$tool_path"
  else
    printf '%s\t%s\n' "$tool" unavailable
  fi
done > evidence/capabilities.txt
~~~

Both <code>cc</code> with C17 support and exact
<code>rustc +1.96.1</code> are required. <code>ar</code> and the inspectors are
optional evidence capabilities. If <code>ar</code> is unavailable, link the two
library objects directly and record that no archive claim was tested. If no
object inspector is available, preserve the build/runtime evidence and state
the inspection gap. Do not install or fetch a replacement.

## Tasks

1. **Map source to artifact — SYS-103-01.** Draw the complete graph from each
   header/source translation unit to each object and then to the C and Rust
   executables. For every edge, name the producing command, input artifact,
   output artifact, and whether unresolved references are permitted at that
   stage. Explain why the header is not independently linked and why a
   relocatable object is not the completed executable.
2. **Reproduce separate compilation.** Compile copied C sources with the
   required language mode and warnings denied:

   ~~~sh
   cc -std=c17 -Wall -Wextra -Wpedantic -Werror -I src \
      -c src/checksum.c -o build/checksum.o
   cc -std=c17 -Wall -Wextra -Wpedantic -Werror -I src \
      -c src/layout_probe.c -o build/layout_probe.o
   cc -std=c17 -Wall -Wextra -Wpedantic -Werror -I src \
      -c src/c_harness.c -o build/c_harness.o
   ~~~

   If the capability record contains an <code>ar</code> path, use that exact
   path to create <code>build/libsys103.a</code> from the two library objects.
   Otherwise retain both objects as explicit link inputs. Link and run the C
   harness. Then compile the Rust test with
   <code>rustc +1.96.1 --edition=2024 --test -D warnings</code> and either
   <code>-L native=build -l static=sys103</code> or two explicit
   <code>-C link-arg=...</code> inputs. Preserve each command, stdout, stderr,
   and immediate status rather than relying on shell history.
3. **Inspect definitions and references — SYS-103-01.** When <code>nm</code> is
   available, inspect <code>checksum.o</code>, <code>c_harness.o</code>, the
   archive if present, and the final executable. Identify observed definitions
   and unresolved references for <code>sys103_checksum</code>. Find any
   observed spelling for the internal <code>fold_byte</code> helper and explain
   why internal C linkage is different from a hidden dynamic export. Do not
   require that optimization, stripping, or another object format retain the
   same spelling.

   When <code>readelf</code> supports the artifacts, record
   <code>-S</code>, <code>-s</code>, <code>-r</code>, and final-executable
   <code>-d</code> output. Otherwise, when <code>objdump</code> supports them,
   record <code>-h</code>, <code>-t</code>, <code>-r</code>, and
   <code>-p</code>. Annotate one instruction/data section, one symbol-table
   entry, and one relocation that participates in the call. Treat dynamic
   dependencies as observations from this executable, not as C requirements.
4. **Measure the target layout — SYS-103-02.** Record the C compiler identity,
   <code>rustc +1.96.1 -vV</code>, target, flags, source hashes, and C harness
   layout line. Make a table for both structures with C and Rust size,
   alignment, every field offset, and inferred inter-field/tail padding. Label
   each entry as a measurement from these artifacts. Explain what C17 and
   <code>repr(C)</code> guarantee separately and why equal size without equal
   offsets is insufficient.
5. **Add a new translation unit.** Add <code>count_byte.c</code> and matching
   declarations for:

   ~~~c
   int32_t sys103_count_byte(
       const sys103_request *request,
       const uint8_t *payload,
       uint32_t payload_len,
       uint8_t needle,
       uint32_t *out_count
   );
   ~~~

   Reuse the 16-byte maximum and status constants. Require header length to
   match the argument. Empty payload is valid and has count zero. Validate all
   status-producing conditions before reading. Write output only on success;
   retain no pointer. Use fixed-width boundary types and document live extent,
   alignment, aliasing, ownership, mutation, synchronization, callbacks, and
   unwinding. Add the object to the archive or explicit link inputs without
   combining source files into one translation unit.
6. **Extend the safe Rust API — SYS-103-03.** Add the exact external
   declaration and a safe wrapper accepting a shared slice and byte. Check the
   kind and 16-byte bound before unsafe code. Use one local request and one
   local output. Map every known status and fail closed on an unknown value.
   Place a numbered safety ledger at the single call covering artifact/symbol
   identity, target C ABI, fixed-width types, measured structure layout,
   pointers and length, lifetime, initialized extent, alignment, aliasing,
   mutation, output write rules, empty input, retention, synchronization,
   callbacks, and panic/unwind behavior.
7. **Test normal, endpoints, and invalid contracts.** Add C and Rust cases for
   repeated and absent bytes; empty input; 1 and exactly 16 bytes; a 17th byte;
   zero and 255 needles; null request, payload, and output in C; mismatched
   length; invalid kind; and unchanged output after every error. Safe Rust tests
   must demonstrate pre-call rejection of invalid kind and excessive length.
   Do not construct a dangling, misaligned, undersized, or overlapping pointer
   merely to “test” undefined behavior.
8. **Prove failure sensitivity — SYS-103-04.** Preserve two safe deliberate
   failures:

   - compile <code>unresolved_consumer.c</code> to an object, link it without a
     defining object, and immediately record the nonzero status and diagnostic;
   - temporarily reverse only the two later fields in Rust
     <code>LayoutDemo</code>, run only the layout test, and preserve its nonzero
     status. This structure is never passed across FFI, so the mismatch test
     observes numbers without creating an invalid foreign call.

   Restore the field order, relink with every intended object, rerun all C and
   Rust tests, and preserve status 0. A described failure that was not observed
   is not evidence.
9. **Write the evidence boundary — SYS-103-04.** State that the checksum and
   count each read at most 16 payload bytes and perform O(n) work for
   <code>0 &lt;= n &lt;= 16</code>. State what temporary disk outputs were created
   without presenting file-size observations as universal object-size bounds.
   Separate C17/Rust language guarantees, target ABI requirements,
   tool-output observations, and untested assumptions. State explicitly that
   this host build establishes no Orange ABI, FFI, linker, package, or
   professional deployment behavior.

## Verification

The lab is complete only when:

- all source copies and build/evidence outputs stay in the fresh workspace;
- separate C translation units produce separate relocatable objects;
- the C17 and exact Rust 1.96.1 builds deny warnings and pass normal, endpoint,
  and checked-invalid tests;
- archive and inspection commands run only when the capability record names an
  available tool;
- symbol, relocation, section, layout, and dynamic-link claims remain scoped
  to the exact target and artifacts observed;
- the new wrapper exposes no raw pointer, rejects before unsafe entry, maps
  errors explicitly, retains ownership in Rust, and forbids unwinding;
- the unresolved-symbol link and harmless layout mismatch both produce
  preserved nonzero evidence before restoration; and
- the final full C and Rust reruns return zero with inspected stdout and
  stderr.

Finally, from the repository module directory, rerun:

~~~sh
PYTHONDONTWRITEBYTECODE=1 python3 checks/lab_smoke.py
~~~

Its exact final line must remain <code>sys-103 lab smoke: PASS</code>.

## Reflection

Write six to nine sentences:

- Which unresolved reference was legal in an object but fatal in an
  executable link?
- What did the relocation tell the linker that the symbol table alone did not?
- Where did you separate internal C linkage, object visibility, and archive
  selection?
- Which layout fact was target-specific, and which language rule constrained
  it?
- Which ownership or aliasing fact could no runtime null check prove?
- Why must an unknown status fail closed?
- What is the declared panic/unwind behavior?
- Which claim could not be tested because an optional inspector was absent?
- Why is this host evidence not Orange evidence?
