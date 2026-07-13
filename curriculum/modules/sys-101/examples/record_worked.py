#!/usr/bin/env python3
"""Print a deterministic trace through the bounded-record model."""

from bounded_record import (
    HEADER_SIZE,
    MAX_PAYLOAD_BYTES,
    MAX_RECORDS,
    MAX_STREAM_BYTES,
    Record,
    checked_add_u16,
    decode_u16,
    encode_record,
    encode_stream,
    parse_stream,
    saturating_add_u16,
    unsigned_to_signed,
    word_bits,
    word_hex,
    wrapping_add_u16,
)


def main() -> int:
    value = 0x1234
    print(f"word: {word_hex(value)} = {word_bits(value)}")
    print(f"big-endian 12 34: {decode_u16(bytes.fromhex('12 34'), 'big')}")
    print(f"little-endian 12 34: {decode_u16(bytes.fromhex('12 34'), 'little')}")
    print(f"0xffff interpreted as i16: {unsigned_to_signed(0xFFFF)}")

    try:
        checked_add_u16(0xFFFF, 1)
    except OverflowError:
        print("checked 0xffff + 1: overflow")
    print(f"wrapping 0xffff + 1: {word_hex(wrapping_add_u16(0xFFFF, 1))}")
    print(f"saturating 0xffff + 1: {word_hex(saturating_add_u16(0xFFFF, 1))}")

    first = Record(flags=3, sequence=value, delta=-2, payload=b"AB")
    second = Record(flags=0, sequence=0, delta=32767, payload=b"")
    encoded = encode_record(first)
    print(f"record bytes: {encoded.hex(' ')}")
    stream = encode_stream([first, second])
    print(f"parsed records: {len(parse_stream(stream))}")
    print(
        "budgets: "
        f"header={HEADER_SIZE}, payload<={MAX_PAYLOAD_BYTES}, "
        f"records<={MAX_RECORDS}, stream<={MAX_STREAM_BYTES}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
