# Assessment: bounded operation-log records

## Instructions

Complete this assessment independently with Python 3.11 or newer and only the
standard library. Work in a fresh temporary directory and keep every source,
test, output, and evidence file there. Do not copy, import, rename, or lightly
translate the module example or lab implementation. The field layout, version,
endianness, and budgets below are different and must be implemented from this
contract.

Submit the representation analysis, source, tests, deliberate-failure record,
resource budget, cross-language comparison, and reproducible command/result
record. This assessment covers:

- **SYS-101-01:** Distinguish mathematical integers from fixed-width unsigned
  and two's-complement representations, including bits, bytes, hexadecimal,
  and endian order.
- **SYS-101-02:** Select and justify checked, wrapping, or saturating arithmetic
  plus bounded shifts and conversions at representation boundaries.
- **SYS-101-03:** Encode and parse a bounded binary record with validated
  length/offset arithmetic and explicit input, time, and memory budgets.

## Knowledge check

1. Distinguish mathematical value, bit pattern, width, signed interpretation,
   and byte order. Show how one pattern can denote 65535 or -1 without its bits
   changing.
2. Derive the u16 and i16 ranges. Convert <code>0x8001</code> to unsigned and
   signed two's-complement decimal, showing the calculation.
3. Give the big- and little-endian byte sequences for <code>0xabcd</code>.
   Explain why reading a host integer object's bytes is not a portable wire
   format in C17.
4. Compare checked, wrapping, and saturating addition at
   <code>65530 + 10</code>. Give one systems contract for which each policy is
   correct and explain why policy selection is not an optimization detail.
5. State the valid shift-count range for a u16. Explain the separate questions
   “does the count fit?” and “does the result fit?”
6. Prove that <code>length &lt;= limit - offset</code>, after proving
   <code>offset &lt;= limit</code>, establishes that
   <code>offset + length &lt;= limit</code>. Explain why this ordering matters in
   a fixed-width implementation.
7. Compare relevant semantics without treating the languages as identical:
   Python's non-fixed-width integers and byte conversions; C17 unsigned
   arithmetic, signed overflow, shifts, conversions, and implementation byte
   order; and Rust 1.96.1 named checked/wrapping/saturating operations, shifts,
   checked conversion, and endian methods. Identify WG14 N2176 as the public
   C17 ballot draft, not the published ISO/IEC standard.

## Independent task

Create <code>operation_log.py</code> and <code>test_operation_log.py</code>.

1. **Representation — SYS-101-01.** Implement exact u16 and i16 range checks,
   four-digit hex and 16-bit binary rendering, u16-pattern/i16-value
   two's-complement interpretation, and explicit big- and little-endian
   conversion. Plain integer APIs must reject Boolean values. Byte decoders
   must accept exactly two immutable bytes and an explicit order. Checked
   mathematical-to-word conversions reject rather than truncate.
2. **Arithmetic — SYS-101-02.** Implement separately named u16 functions for:

   - checked addition that reports failure without returning a wrapped word;
   - modulo-<code>2^16</code> wrapping addition;
   - saturating addition clamped at 65535;
   - checked left shift with count 0 through 15 and rejection when a set bit
     leaves the word; and
   - logical right shift with count 0 through 15.

   Add a policy table for byte offsets, explicitly modulo sequence IDs, and a
   bounded gauge. Justify the selected mode and reject the two alternatives for
   each contract.
3. **Record codec — SYS-101-03.** Implement this independent big-endian format:

   | Offset | Width | Field | Contract |
   | ---: | ---: | --- | --- |
   | 0 | 2 bytes | Magic | ASCII bytes <code>OR</code> |
   | 2 | 1 byte | Version | Exactly 3 |
   | 3 | 1 byte | Flags | Unsigned 0–15 |
   | 4 | 2 bytes | Record ID | Big-endian u16 |
   | 6 | 2 bytes | Adjustment | Big-endian two's-complement i16 |
   | 8 | 2 bytes | Payload length | Big-endian u16 from 0 through 48 |
   | 10 | Declared length | Payload | Exact immutable bytes; no trailing data |

   Use an immutable record value. Encode exactly one canonical byte sequence
   and decode exactly one record. Reject mutable byte arrays and arbitrary
   iterables, wrong magic, wrong version, flags above 15, short headers,
   truncated or over-budget payloads, mismatched declarations, and trailing
   bytes.
4. **Bounded stream parser — SYS-101-03.** Encode and parse 0 through 32
   records and at most 1,856 bytes
   (<code>32 * (10 + 48)</code>). Before reading or slicing, validate:

   - the complete ten-byte header lies within the input;
   - the declared length is no more than 48;
   - offset and length are plain nonnegative integers within the complete
     stream budget;
   - offset is no more than limit; and
   - length is no more than <code>limit - offset</code> before the end offset is
     calculated.

   The encoder accepts only a list or tuple whose record count is known before
   encoding. The parser must stop with failure rather than return a partial
   result for any malformed record.
5. **Independent tests.** Include exact-byte and round-trip tests for flags 9,
   record ID <code>0xabcd</code>, adjustment -300, and payload
   <code>b"log"</code>. Cover zero and every exact endpoint; 0-, 1-, and
   48-byte payloads; 0 and exactly 32 records; the 33rd record; all three add
   modes across overflow; shifts at 0/15 and outside the range; signed and
   endian interpretation boundaries; every rejection named above; a 1,856-byte
   maximum stream; and a 1,857-byte input. Test output, error type, and absence
   of a partial result where applicable.
6. **Failure sensitivity.** Temporarily change one expected endian byte sequence
   and one expected length-boundary result. Run only those tests, preserve
   stdout/stderr and immediate nonzero status, restore both expectations, and
   preserve the passing rerun. All evidence files stay in the assessment's
   temporary directory.
7. **Budgets and evidence.** State <code>b &lt;= 1856</code> input bytes,
   <code>n &lt;= 32</code> records, at most 32 parser iterations, O(b) parse
   time, and O(b+n) model storage for returned payload bytes and records. State
   that Python interpreter and allocator overhead is not fixed by the model.
   Record Python version, absolute path, hashes of submitted source, exact
   commands, stdout, stderr, and immediate statuses. State that successful
   parsing recognizes structure only and makes no authentication,
   confidentiality, integrity, randomness, or cryptographic claim.

## Completion criteria

Use [the rubric](rubric.md). Passing requires at least 80/100 and every critical
criterion. The submission must:

- correctly separate values, 16-bit patterns, signed interpretation, and byte
  order for **SYS-101-01**;
- implement and contract-justify checked, wrapping, saturating, shift, and
  conversion behavior for **SYS-101-02**;
- encode and parse the independent record and bounded stream without accepting
  truncation, trailing bytes, wrapped ranges, partial results, or over-budget
  work for **SYS-101-03**;
- include positive, endpoint, invalid, and observed deliberate-failure evidence;
- state concrete input, iteration, time, and storage limits without presenting
  asymptotic notation as an exact memory measurement; and
- run offline using only Python's standard library and temporary output paths.
