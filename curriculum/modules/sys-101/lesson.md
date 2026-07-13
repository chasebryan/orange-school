# Representation, arithmetic, and resource bounds

A mathematical integer has no fixed number of bits. A machine field does. The
same two bytes can denote different values under different byte orders or
signed interpretations, and an operation that is ordinary integer addition in
mathematics may be rejected, wrapped, clamped, or undefined in a programming
language. Professional systems work makes every one of those choices explicit.

This module uses Python 3.11 to model a portable 16-bit word and a bounded
binary record. Python is the modeling language, not the specification of C or
Rust behavior. The comparison sections cite C17's public ballot draft and the
official Rust 1.96.1 and Python documentation.

## Learning objectives

- **SYS-101-01:** Distinguish mathematical integers from fixed-width unsigned
  and two's-complement representations, including bits, bytes, hexadecimal,
  and endian order.
- **SYS-101-02:** Select and justify checked, wrapping, or saturating arithmetic
  plus bounded shifts and conversions at representation boundaries.
- **SYS-101-03:** Encode and parse a bounded binary record with validated
  length/offset arithmetic and explicit input, time, and memory budgets.

## Prerequisites

Pass <code>prg-102</code>. You should be able to write and test Python
functions, choose bounded collections, distinguish a representation invariant
from an example, and state concrete input, time, and space limits. This module
uses Python 3.11 or newer and only the standard library. No C or Rust compiler,
network access, administrator access, or knowledge of cryptography is needed.

## Lesson

### A value is not its representation

The mathematical integer 300 is an abstract value. It is not inherently
signed, 16 bits wide, big-endian, or hexadecimal. Those properties belong to a
chosen representation.

An unsigned 16-bit word has exactly 16 binary positions and represents the
set

~~~text
{0, 1, ..., 2^16 - 1} = {0, 1, ..., 65535}.
~~~

The mapping from a valid bit pattern to an unsigned value is

~~~text
b15*2^15 + b14*2^14 + ... + b1*2 + b0,
~~~

where each <code>b</code> is zero or one. The word
<code>0000000100101100</code> therefore denotes 300. A Python
<code>int</code> can represent values beyond that range, so the supplied model
checks <code>0 &lt;= value &lt;= 65535</code> before calling a value a
<code>u16</code>.

A **bit** is one binary digit. This record format defines one **byte** as eight
bits, so a 16-bit word occupies two bytes. That octet definition is a protocol
choice. In C, a byte is the size of <code>char</code> and
<code>CHAR_BIT</code> is not universally required to be eight; do not silently
substitute C object layout for a wire-format definition.

Hexadecimal is compact bit notation. One hex digit covers four bits, so four
digits cover one 16-bit word:

| Binary | Hex | Unsigned decimal |
| --- | --- | ---: |
| <code>0000 0000 0000 0000</code> | <code>0x0000</code> | 0 |
| <code>0000 0001 0010 1100</code> | <code>0x012c</code> | 300 |
| <code>1000 0000 0000 0000</code> | <code>0x8000</code> | 32768 |
| <code>1111 1111 1111 1111</code> | <code>0xffff</code> | 65535 |

Preserve leading zeros when the width matters. <code>0x2a</code> and
<code>0x002a</code> have the same mathematical value, but only the second
spelling displays the complete 16-bit field width.

### Unsigned and two's-complement interpretations

An interpretation maps a bit pattern to a value. The unsigned interpretation
above uses all patterns for nonnegative values. A 16-bit **two's-complement**
signed interpretation uses the high bit as having weight <code>-2^15</code>:

~~~text
-b15*2^15 + b14*2^14 + ... + b0.
~~~

Equivalently, interpret the pattern as unsigned <code>u</code>. If
<code>u &lt; 32768</code>, the signed value is <code>u</code>; otherwise it is
<code>u - 65536</code>.

| Pattern | Unsigned | Signed two's complement |
| --- | ---: | ---: |
| <code>0x0000</code> | 0 | 0 |
| <code>0x7fff</code> | 32767 | 32767 |
| <code>0x8000</code> | 32768 | -32768 |
| <code>0xffff</code> | 65535 | -1 |

The bits do not announce which column to use. A field contract must do that.
The inverse signed-to-unsigned mapping is <code>s mod 65536</code> after first
checking <code>-32768 &lt;= s &lt;= 32767</code>.

Python documents its bitwise operations as behaving as though integers used
two's complement with infinitely many sign bits. That is useful, but it is not
a 16-bit type. The model validates the range and masks or reduces only when a
named policy requires it.

### Endianness orders bytes, not bits within a byte

A two-byte field must say which byte comes first. For value
<code>0x1234</code>:

| Order | Byte at lower record offset | Next byte |
| --- | --- | --- |
| Big-endian | <code>0x12</code> (most significant) | <code>0x34</code> |
| Little-endian | <code>0x34</code> (least significant) | <code>0x12</code> |

Reading the sequence <code>12 34</code> as big-endian yields
<code>0x1234 = 4660</code>; reading the same two bytes as little-endian yields
<code>0x3412 = 13330</code>. Neither is “the natural order” for a portable file
or message. The format must name one.

Python's <code>int.to_bytes</code> and <code>int.from_bytes</code> take explicit
<code>byteorder</code> and <code>signed</code> arguments. The model accepts only
the strings <code>big</code> and <code>little</code>; it does not use host-native
order. Rust's fixed-width integers similarly provide
<code>to_be_bytes</code>, <code>to_le_bytes</code>,
<code>from_be_bytes</code>, and <code>from_le_bytes</code>. C17 does not impose
one byte order on all implementations, so portable C code must encode the
chosen field order explicitly rather than copy an integer object's bytes.

### Overflow is a policy decision

For <code>u16</code>, the mathematical sum <code>65535 + 1 = 65536</code> is
outside the representation. Three common policies answer different questions:

| Policy | Result of 65535 + 1 | Suitable claim |
| --- | --- | --- |
| Checked | Error; no word result | The operation must remain in range |
| Wrapping | 0 | Arithmetic is intentionally modulo <code>2^16</code> |
| Saturating | 65535 | The result is intentionally clamped to the endpoint |

These are not interchangeable fallback strategies. A byte offset should
usually be checked: wrapping an out-of-range offset can point at an unrelated
location. A cyclic sequence number might intentionally wrap if its protocol
defines comparisons across the wrap. A display level might saturate if values
above its maximum all mean “full.” Write the reason next to the choice.

The example provides separately named
<code>checked_add_u16</code>, <code>wrapping_add_u16</code>, and
<code>saturating_add_u16</code>. Plain Python addition grows to 65536; the
model then applies the selected 16-bit contract.

Cross-language names do not erase semantic differences:

- C17 unsigned arithmetic is reduced modulo one more than the largest value of
  the type. Signed overflow is undefined behavior. The C17 language does not
  provide a general named saturating integer operator. Code that needs a
  checked result must establish a range precondition before the overflowing
  expression could be evaluated.
- Rust 1.96.1 exposes named methods such as <code>checked_add</code>,
  <code>wrapping_add</code>, and <code>saturating_add</code>. Ordinary operator
  overflow checks are affected by compilation settings, so a systems contract
  should use the method that states the intended policy.
- Python integer addition does not overflow at a fixed word width. A Python
  model must enforce the width itself. <code>int.to_bytes</code> raises
  <code>OverflowError</code> when the value cannot fit the requested byte count.

C17 did not require every signed integer type to use two's complement. Its
optional exact-width <code>int16_t</code>, when an implementation provides that
typedef, has exactly 16 bits, no padding, and a two's-complement representation;
<code>uint16_t</code> is likewise an optional exact-width unsigned type. Rust's
<code>i16</code> and <code>u16</code> are fixed-width types with the documented
two's-complement signed representation. Python's ordinary <code>int</code> is
neither type, even when this model restricts one Python value to the same range.

The public WG14 document used here is N2176, the C17 ballot draft. It is not
the separately published ISO/IEC 9899:2018 text. It is useful public evidence
for the relevant C17 clauses, but the source label must remain honest.

### Shifts and conversions have boundaries too

A left shift by <code>k</code> multiplies a nonnegative mathematical integer by
<code>2^k</code>. In a fixed 16-bit word, two questions precede it:

1. Is <code>0 &lt;= k &lt; 16</code>?
2. Does the shifted result still fit, or did a set bit leave the word?

The model's checked left shift rejects both an invalid count and a discarded
set bit. Thus <code>1 &lt;&lt; 15</code> yields <code>0x8000</code>,
<code>0x8000 &lt;&lt; 1</code> is rejected, and a count of 16 is rejected. Its
right shift is explicitly **logical** because the input is unsigned. A signed
right shift needs a separately documented arithmetic/logical policy.

In C17, a negative shift count or one at least as large as the promoted left
operand's width has undefined behavior. Signed left shift has additional
representability conditions, and right shift of a negative signed value is
implementation-defined. In Rust, an out-of-range shift is an overflow
condition; named methods such as <code>checked_shl</code> make rejection
explicit. Python permits arbitrarily large nonnegative shift counts and rejects
negative counts, so the model supplies the missing word-width limit.

Conversions require the same discipline. “Convert a mathematical integer to
u16” means reject values below 0 or above 65535. “Interpret this u16 pattern as
i16 two's complement” is a different operation and maps <code>0xffff</code> to
-1. A truncating or modulo conversion is a third operation and must be named as
such. Rust's <code>TryFrom</code> supports checked integer conversion, while
Rust <code>as</code> has specified truncation/sign behavior. C17 conversion to
an unsigned type uses repeated modular adjustment; conversion of an
out-of-range value to a signed integer type is implementation-defined or may
raise an implementation-defined signal. Do not translate code by spelling
alone.

### Check lengths and offsets before slicing

A parser commonly needs the half-open range
<code>[offset, offset + length)</code>. Its safety condition is

~~~text
0 <= offset <= limit
0 <= length <= limit - offset.
~~~

Check the second form before addition. In a fixed-width implementation,
testing only <code>offset + length &lt;= limit</code> can be wrong if the addition
wraps first. Python would grow the mathematical sum rather than wrap, but the
subtraction-first model teaches the portable invariant.

The supplied <code>checked_end</code> also caps each quantity at the complete
stream budget. It accepts the endpoint <code>offset == limit</code> only for a
zero-length span. It rejects negative quantities, Boolean values masquerading
as integers, an offset beyond the limit, and a length beyond the remaining
bytes.

### The example record has one canonical contract

The [bounded-record implementation](examples/bounded_record.py) defines this
big-endian format:

| Offset | Width | Field | Contract |
| ---: | ---: | --- | --- |
| 0 | 1 byte | Magic | Exactly <code>0xa5</code> |
| 1 | 1 byte | Version and flags | High nibble version 1; low nibble flags 0–15 |
| 2 | 2 bytes | Sequence | Big-endian unsigned 16-bit |
| 4 | 2 bytes | Delta | Big-endian signed two's-complement 16-bit |
| 6 | 2 bytes | Payload length | Big-endian unsigned; 0–32 |
| 8 | Declared length | Payload | Exact immutable bytes; no trailing data |

One record therefore occupies 8 through 40 bytes. One stream contains 0
through 16 concatenated records and at most 640 bytes. The decoder rejects an
unsupported version, wrong magic, truncated header or payload, over-budget
length, and trailing bytes. The stream parser checks the header span before
reading the length and checks the complete record span before slicing.

The format is a representation exercise, not cryptography. The magic byte is a
type marker, not authentication; the version is a compatibility gate, not
anti-replay protection; and successful parsing says nothing about who created
the bytes.

### Budgets turn “bounded” into evidence

For a stream of <code>n</code> records and <code>b</code> input bytes, the parser
performs at most <code>n &lt;= 16</code> loop iterations and examines each
record's bounded header and payload once: O(b) time with
<code>b &lt;= 640</code>. It returns at most 16 record objects. Python slicing
copies record bytes, and each immutable payload slice is retained, so a useful
model-level bound is O(b) additional byte content plus O(n) objects. Object
headers and allocator overhead depend on the Python implementation; do not
claim that O(b) proves an exact number of resident bytes.

The checks run with:

- input: at most 640 encoded bytes, 16 records, 32 payload bytes per record;
- work: at most 16 parse iterations and bounded 40-byte record decoding;
- retained model data: at most 16 records and 640 bytes of encoded content,
  plus interpreter-dependent object overhead; and
- external effects: local reads and temporary evidence only, with no network or
  package installation.

Bounds must be validated before allocating or iterating based on untrusted
lengths. The stream encoder therefore accepts only a list or tuple whose length
is already available; it does not first materialize an arbitrary iterable.

## Worked example

For flags 3, sequence <code>0x1234</code>, delta -2, and payload
<code>AB</code>, the bytes are:

~~~text
a5 13 12 34 ff fe 00 02 41 42
~~~

Trace them:

1. <code>a5</code> matches the magic.
2. <code>13</code> has high nibble 1 for the version and low nibble 3 for flags.
3. Big-endian <code>12 34</code> gives sequence 4660.
4. Big-endian signed <code>ff fe</code> has unsigned pattern 65534 and signed
   two's-complement value <code>65534 - 65536 = -2</code>.
5. Big-endian <code>00 02</code> declares a two-byte payload.
6. The header ends at offset 8. The check
   <code>2 &lt;= 10 - 8</code> succeeds, so the end is 10.
7. Bytes <code>41 42</code> are exactly the declared payload. No byte remains.

Run the [worked program](examples/record_worked.py) to observe this trace and
the three results for <code>0xffff + 1</code>.

## Check your understanding

1. Why is mathematical 65536 valid even though it is not a valid u16?
2. What signed i16 value does pattern <code>0x8000</code> denote?
3. What value do bytes <code>01 02</code> denote in big- and little-endian u16?
4. Which addition policy should a parser normally use for byte offsets, and
   why?
5. Why check <code>length &lt;= limit - offset</code> before calculating the end?
6. Does decoding this module's magic byte authenticate a record?

**Answers:** (1) mathematical integers are not confined to the selected
representation; (2) -32768; (3) 258 big-endian and 513 little-endian; (4)
checked, because wrapping or clamping could select the wrong range; (5) it
avoids relying on an addition that could overflow in a fixed-width
implementation; (6) no, it only recognizes a format marker.

## Next step

Complete the [lab](lab.md), including the intentional failed test and bounded
little-endian record implementation. Then complete the independent
[assessment](assessment.md). Passing requires at least 80/100 and every
critical criterion in the [rubric](rubric.md).

## Sources

- Python Software Foundation, [Python 3.11 built-in integer and bytes
  types](https://docs.python.org/3.11/library/stdtypes.html), especially
  bitwise operations, <code>int.to_bytes</code>, <code>int.from_bytes</code>,
  and bytes operations.
- ISO/IEC JTC 1/SC 22/WG14, [public document index containing
  N2176](https://www.open-std.org/jtc1/sc22/wg14/www/docs/) and [N2176, C17
  ballot draft](https://www.open-std.org/jtc1/sc22/wg14/www/docs/n2176.pdf),
  especially §§5.2.4.2.1, 6.2.5, 6.2.6.2, 6.3.1.3, 6.5, 6.5.7, and 7.20.1.1.
  N2176 is a public ballot draft, not the published ISO/IEC 9899:2018 text.
- The Rust Project, [Rust 1.96.1 primitive
  <code>u16</code>](https://doc.rust-lang.org/1.96.1/std/primitive.u16.html),
  including endian conversion and checked, wrapping, saturating, and shift
  methods.
- The Rust Project, [Rust Reference: numeric
  types](https://doc.rust-lang.org/1.96.1/reference/types/numeric.html) and
  [operator expressions, overflow, shifts, and numeric
  casts](https://doc.rust-lang.org/1.96.1/reference/expressions/operator-expr.html).
- The Rust Project, [Rust 1.96.1
  <code>TryFrom</code>](https://doc.rust-lang.org/1.96.1/std/convert/trait.TryFrom.html),
  for checked conversions.
- [Assessment system](../../../docs/assessment-system.md), independent evidence
  and pass policy.
