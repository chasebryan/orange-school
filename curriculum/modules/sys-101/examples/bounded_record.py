#!/usr/bin/env python3
"""A strict, bounded 16-bit word and binary-record teaching model."""

from __future__ import annotations

from dataclasses import dataclass


WORD_BITS = 16
WORD_BYTES = WORD_BITS // 8
WORD_MODULUS = 1 << WORD_BITS
U16_MAX = WORD_MODULUS - 1
I16_MIN = -(1 << (WORD_BITS - 1))
I16_MAX = (1 << (WORD_BITS - 1)) - 1

MAGIC = 0xA5
VERSION = 1
HEADER_SIZE = 8
MAX_FLAGS = 0x0F
MAX_PAYLOAD_BYTES = 32
MAX_RECORDS = 16
MAX_RECORD_BYTES = HEADER_SIZE + MAX_PAYLOAD_BYTES
MAX_STREAM_BYTES = MAX_RECORDS * MAX_RECORD_BYTES


def _plain_int(value: object, label: str) -> int:
    if type(value) is not int:
        raise TypeError(f"{label} must be an integer")
    return value


def _bounded_int(value: object, minimum: int, maximum: int, label: str) -> int:
    checked = _plain_int(value, label)
    if not minimum <= checked <= maximum:
        raise ValueError(f"{label} must be from {minimum} through {maximum}")
    return checked


def _exact_bytes(value: object, label: str) -> bytes:
    if type(value) is not bytes:
        raise TypeError(f"{label} must be bytes")
    return value


def _byteorder(value: object) -> str:
    if type(value) is not str:
        raise TypeError("byteorder must be a string")
    if value not in ("big", "little"):
        raise ValueError("byteorder must be 'big' or 'little'")
    return value


def require_u16(value: object, label: str = "value") -> int:
    """Return a mathematical integer only when it fits an unsigned 16-bit word."""

    return _bounded_int(value, 0, U16_MAX, label)


def require_i16(value: object, label: str = "value") -> int:
    """Return a mathematical integer only when it fits a signed 16-bit word."""

    return _bounded_int(value, I16_MIN, I16_MAX, label)


def word_hex(value: object) -> str:
    """Format an unsigned 16-bit word as four hexadecimal digits."""

    return f"0x{require_u16(value):04x}"


def word_bits(value: object) -> str:
    """Format an unsigned 16-bit word as exactly sixteen binary digits."""

    return f"{require_u16(value):016b}"


def unsigned_to_signed(value: object) -> int:
    """Interpret one u16 bit pattern as a two's-complement i16 value."""

    unsigned = require_u16(value)
    sign_bit = 1 << (WORD_BITS - 1)
    return unsigned if unsigned < sign_bit else unsigned - WORD_MODULUS


def signed_to_unsigned(value: object) -> int:
    """Return the u16 bit pattern for one two's-complement i16 value."""

    signed = require_i16(value)
    return signed % WORD_MODULUS


def encode_u16(value: object, byteorder: object) -> bytes:
    return require_u16(value).to_bytes(WORD_BYTES, _byteorder(byteorder), signed=False)


def decode_u16(data: object, byteorder: object) -> int:
    octets = _exact_bytes(data, "data")
    if len(octets) != WORD_BYTES:
        raise ValueError(f"data must contain exactly {WORD_BYTES} bytes")
    return int.from_bytes(octets, _byteorder(byteorder), signed=False)


def encode_i16(value: object, byteorder: object) -> bytes:
    return require_i16(value).to_bytes(WORD_BYTES, _byteorder(byteorder), signed=True)


def decode_i16(data: object, byteorder: object) -> int:
    octets = _exact_bytes(data, "data")
    if len(octets) != WORD_BYTES:
        raise ValueError(f"data must contain exactly {WORD_BYTES} bytes")
    return int.from_bytes(octets, _byteorder(byteorder), signed=True)


def checked_add_u16(left: object, right: object) -> int:
    """Add two u16 values, rejecting a result outside the representation."""

    result = require_u16(left, "left") + require_u16(right, "right")
    if result > U16_MAX:
        raise OverflowError("u16 checked addition overflowed")
    return result


def wrapping_add_u16(left: object, right: object) -> int:
    """Add modulo 2**16."""

    return (require_u16(left, "left") + require_u16(right, "right")) % WORD_MODULUS


def saturating_add_u16(left: object, right: object) -> int:
    """Add and clamp a result above u16::MAX to u16::MAX."""

    return min(require_u16(left, "left") + require_u16(right, "right"), U16_MAX)


def checked_shift_left_u16(value: object, count: object) -> int:
    """Shift left only when count and result both fit the declared word model."""

    word = require_u16(value)
    distance = _bounded_int(count, 0, WORD_BITS - 1, "count")
    result = word << distance
    if result > U16_MAX:
        raise OverflowError("u16 left shift discarded a set bit")
    return result


def logical_shift_right_u16(value: object, count: object) -> int:
    """Logically shift an unsigned word right by 0 through 15 positions."""

    word = require_u16(value)
    distance = _bounded_int(count, 0, WORD_BITS - 1, "count")
    return word >> distance


def checked_end(offset: object, length: object, limit: object) -> int:
    """Return offset + length only when the half-open span is within limit."""

    checked_limit = _bounded_int(limit, 0, MAX_STREAM_BYTES, "limit")
    checked_offset = _bounded_int(offset, 0, MAX_STREAM_BYTES, "offset")
    checked_length = _bounded_int(length, 0, MAX_STREAM_BYTES, "length")
    if checked_offset > checked_limit:
        raise ValueError("offset exceeds limit")
    # Subtraction expresses the bound without depending on fixed-width addition.
    if checked_length > checked_limit - checked_offset:
        raise ValueError("offset and length exceed limit")
    return checked_offset + checked_length


@dataclass(frozen=True, slots=True)
class Record:
    """One immutable, bounded record value; payload excludes the eight-byte header."""

    flags: int
    sequence: int
    delta: int
    payload: bytes

    def __post_init__(self) -> None:
        _bounded_int(self.flags, 0, MAX_FLAGS, "flags")
        require_u16(self.sequence, "sequence")
        require_i16(self.delta, "delta")
        payload = _exact_bytes(self.payload, "payload")
        if len(payload) > MAX_PAYLOAD_BYTES:
            raise ValueError(
                f"payload must contain at most {MAX_PAYLOAD_BYTES} bytes"
            )


def encode_record(record: object) -> bytes:
    """Encode one record in the module's portable big-endian wire format."""

    if type(record) is not Record:
        raise TypeError("record must be a Record")
    tag = (VERSION << 4) | record.flags
    header = bytes((MAGIC, tag))
    header += encode_u16(record.sequence, "big")
    header += encode_i16(record.delta, "big")
    header += encode_u16(len(record.payload), "big")
    return header + record.payload


def decode_record(data: object) -> Record:
    """Decode exactly one record, rejecting truncation and trailing bytes."""

    encoded = _exact_bytes(data, "data")
    if not HEADER_SIZE <= len(encoded) <= MAX_RECORD_BYTES:
        raise ValueError(
            f"encoded record must contain {HEADER_SIZE} through {MAX_RECORD_BYTES} bytes"
        )
    if encoded[0] != MAGIC:
        raise ValueError("record magic is invalid")
    version = encoded[1] >> 4
    if version != VERSION:
        raise ValueError("record version is unsupported")
    flags = encoded[1] & MAX_FLAGS
    payload_length = decode_u16(encoded[6:8], "big")
    if payload_length > MAX_PAYLOAD_BYTES:
        raise ValueError("declared payload length exceeds the record budget")
    end = checked_end(HEADER_SIZE, payload_length, len(encoded))
    if end != len(encoded):
        raise ValueError("declared payload length does not match record size")
    return Record(
        flags=flags,
        sequence=decode_u16(encoded[2:4], "big"),
        delta=decode_i16(encoded[4:6], "big"),
        payload=encoded[HEADER_SIZE:end],
    )


def encode_stream(records: object) -> bytes:
    """Encode 0 through 16 records without accepting an unbounded iterable."""

    if type(records) not in (list, tuple):
        raise TypeError("records must be a list or tuple")
    if len(records) > MAX_RECORDS:
        raise ValueError(f"records must contain at most {MAX_RECORDS} values")
    encoded_parts: list[bytes] = []
    total = 0
    for record in records:
        part = encode_record(record)
        total = checked_end(total, len(part), MAX_STREAM_BYTES)
        encoded_parts.append(part)
    result = b"".join(encoded_parts)
    if len(result) != total:
        raise AssertionError("encoded stream length invariant failed")
    return result


def parse_stream(data: object) -> tuple[Record, ...]:
    """Parse a bounded concatenation of records with checked offsets."""

    encoded = _exact_bytes(data, "data")
    if len(encoded) > MAX_STREAM_BYTES:
        raise ValueError(f"stream must contain at most {MAX_STREAM_BYTES} bytes")
    records: list[Record] = []
    offset = 0
    while offset < len(encoded):
        if len(records) == MAX_RECORDS:
            raise ValueError(f"stream contains more than {MAX_RECORDS} records")
        header_end = checked_end(offset, HEADER_SIZE, len(encoded))
        if encoded[offset] != MAGIC:
            raise ValueError("record magic is invalid")
        if encoded[offset + 1] >> 4 != VERSION:
            raise ValueError("record version is unsupported")
        payload_length = decode_u16(encoded[header_end - WORD_BYTES : header_end], "big")
        if payload_length > MAX_PAYLOAD_BYTES:
            raise ValueError("declared payload length exceeds the record budget")
        record_end = checked_end(header_end, payload_length, len(encoded))
        records.append(decode_record(encoded[offset:record_end]))
        offset = record_end
    return tuple(records)
