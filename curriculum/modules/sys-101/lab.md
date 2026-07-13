# Lab: bounded little-endian telemetry records

## Goal

Trace fixed-width values, choose explicit arithmetic policies, and implement a
strict little-endian binary-record codec whose lengths, offsets, loop work, and
retained data are bounded before processing.

## Setup

From the repository root, inspect and run the supplied model:

~~~sh
cd curriculum/modules/sys-101
python3 --version
PYTHONDONTWRITEBYTECODE=1 python3 examples/record_worked.py
PYTHONDONTWRITEBYTECODE=1 python3 checks/lab_smoke.py
~~~

The final command must print <code>sys-101 lab smoke: PASS</code> and exit 0.
It uses Python 3.11's standard library and local files only.

Create a separate temporary workspace:

~~~sh
workdir="$(mktemp -d)"
cd -- "$workdir"
pwd
~~~

Keep source, tests, stdout, stderr, and status records under the printed path.
Set <code>PYTHONDONTWRITEBYTECODE=1</code> for every Python run. No network,
external package, administrator access, permission change, or deletion command
is required.

## Tasks

1. **Trace words and bytes.** For mathematical values 0, 1, 255, 256, 32767,
   32768, 65535, -1, and -32768, make a table showing whether each fits u16 and
   i16. For every fitting value, show the exact four-digit hex pattern and 16
   bits under the declared interpretation. For <code>0x0102</code>, show its
   big- and little-endian byte sequence and show what bytes
   <code>01 02</code> mean under both orders. Label values separately from bit
   patterns.
2. **Choose arithmetic behavior.** For each case, select checked, wrapping, or
   saturating behavior and justify the choice from the contract:

   - advancing a parser byte offset;
   - incrementing an explicitly modulo-65536 wire sequence;
   - increasing a display level whose values above 65535 all mean “full”; and
   - multiplying a payload count by an item width before allocation.

   Give endpoint examples. State why the other two policies would violate each
   selected contract. Specify that all shift counts are from 0 through 15 and
   that a checked left shift rejects a set bit leaving the word.
3. **Define a changed record format.** Implement this format in
   <code>telemetry_record.py</code>; do not import the module example:

   | Offset | Width | Field | Contract |
   | ---: | ---: | --- | --- |
   | 0 | 1 | Magic | Exactly <code>0xd2</code> |
   | 1 | 1 | Version/flags | High nibble version 2; low nibble flags 0–15 |
   | 2 | 2 | Sample ID | Little-endian u16 |
   | 4 | 2 | Reading | Little-endian two's-complement i16 |
   | 6 | 1 | Payload length | Unsigned 0–24 |
   | 7 | Declared length | Payload | Exact immutable bytes |

   Use an immutable record type. Reject Boolean values wherever the contract
   says integer. Accept only exact <code>bytes</code> payload and input, not a
   mutable byte array or arbitrary iterable. Reject wrong magic, unsupported
   version, truncated data, a declaration above 24, declaration/actual-length
   mismatch, and trailing bytes.
4. **Implement bounded streams and word operations.** A stream contains at
   most 12 records and at most 372 bytes
   (<code>12 * (7 + 24)</code>). Implement encode and parse functions that:

   - accept a list or tuple rather than first materializing an arbitrary
     iterable;
   - validate the stream byte count and record count;
   - check the complete seven-byte header before reading its length;
   - prove <code>length &lt;= limit - offset</code> before adding; and
   - return at most 12 immutable records.

   Also implement separately named u16 checked, wrapping, and saturating
   addition; a checked u16 left shift; a logical u16 right shift; and checked
   conversions between mathematical integers, u16 patterns, and i16
   two's-complement values. Do not use a modulo expression inside checked or
   saturating addition.
5. **Test positive, endpoint, and invalid behavior.** Create
   <code>test_telemetry_record.py</code> with <code>unittest</code>. Cover:

   - exact bytes and round trip for flags 5, sample ID <code>0x1234</code>,
     reading -2, and payload <code>b"OK"</code>;
   - empty and 24-byte payloads, zero and maximum flags/sample ID, and minimum
     and maximum i16 readings;
   - empty stream, exactly 12 maximum-size records, and a thirteenth record;
   - both endian orders for <code>0x1234</code> and both signed interpretations
     at <code>0x7fff</code>, <code>0x8000</code>, and <code>0xffff</code>;
   - each addition mode at <code>65535 + 1</code>;
   - shift counts 0 and 15, counts -1 and 16, and a left shift that loses a set
     bit;
   - negative/oversized conversion, Boolean, mutable byte array, wrong magic,
     wrong version, short header, short payload, trailing bytes, oversized
     declaration, and over-budget stream; and
   - an offset equal to the limit with zero length, an offset beyond the limit,
     and a length one byte beyond the remainder.
6. **Prove the tests can fail.** Change the expected wrapping result for
   <code>65535 + 1</code> from 0 to 1. Run only that test, redirect stdout and
   stderr to files in the temporary workspace, and immediately record its
   nonzero status. Restore 0, rerun the test, and record status 0. Preserve both
   outputs. A passing run without the observed deliberate failure is incomplete.
7. **Write a budget and reproducibility record.** Record the Python version,
   absolute workspace, source-file hashes, commands, stdout, stderr, and
   immediate statuses. State the input limits, maximum parser loop iterations,
   maximum encoded record and stream sizes, and O(b) time/O(b+n) model storage
   with <code>b &lt;= 372</code> and <code>n &lt;= 12</code>. Note that Python
   object overhead is implementation-dependent. Explain that the magic and
   version fields identify a representation but provide no authentication or
   cryptographic protection.

## Verification

From the temporary workspace, run:

~~~sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v \
  >passing.stdout 2>passing.stderr
test_status=$?
printf 'test status: %s\n' "$test_status"
~~~

Status 0 is necessary but not sufficient. Inspect the implementation and
evidence and confirm that:

- value, pattern, signedness, width, and byte order are never conflated;
- each overflow mode is separately named and contract-justified;
- conversion and shift boundaries are checked before the operation is trusted;
- the parser validates the header and subtraction-form span bound before each
  slice;
- declared payload length must exactly consume one record;
- byte-count and record-count budgets precede data-dependent processing;
- the deliberate wrong expectation produced a nonzero run before restoration;
  and
- every learner-created artifact and run output remains under the temporary
  workspace.

Rerun <code>PYTHONDONTWRITEBYTECODE=1 python3 checks/lab_smoke.py</code> from the
module directory as separate evidence that the repository example is unchanged.

## Reflection

Write five to seven sentences:

- Where did you distinguish a mathematical integer from a fixed-width pattern?
- Which operation legitimately wrapped, and which contract made that correct?
- Why was subtraction-form length checking used even though Python integers do
  not wrap?
- Which byte sequence exposed an endian assumption?
- What exact time/input/storage claim follows from 12 records and 372 bytes?
- Why do successful parsing and a magic byte provide no authenticity claim?
