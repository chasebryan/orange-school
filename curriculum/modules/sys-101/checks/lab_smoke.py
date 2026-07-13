#!/usr/bin/env python3
"""Smoke-check the strict bounded-word and binary-record examples."""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile
from pathlib import Path


sys.dont_write_bytecode = True
MODULE_ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = MODULE_ROOT / "examples"
sys.path.insert(0, str(EXAMPLES))

from bounded_record import (  # noqa: E402
    HEADER_SIZE,
    I16_MAX,
    I16_MIN,
    MAX_FLAGS,
    MAX_PAYLOAD_BYTES,
    MAX_RECORDS,
    MAX_STREAM_BYTES,
    U16_MAX,
    Record,
    checked_add_u16,
    checked_end,
    checked_shift_left_u16,
    decode_i16,
    decode_record,
    decode_u16,
    encode_i16,
    encode_record,
    encode_stream,
    encode_u16,
    logical_shift_right_u16,
    parse_stream,
    require_i16,
    require_u16,
    saturating_add_u16,
    signed_to_unsigned,
    unsigned_to_signed,
    word_bits,
    word_hex,
    wrapping_add_u16,
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def expect_error(error_type: type[BaseException], action, message: str) -> None:
    try:
        action()
    except error_type:
        return
    raise AssertionError(message)


def check_words_and_endianness() -> None:
    require(word_hex(0) == "0x0000", "zero hex rendering changed")
    require(word_hex(U16_MAX) == "0xffff", "maximum hex rendering changed")
    require(word_bits(0x8001) == "1000000000000001", "bit rendering changed")
    require(unsigned_to_signed(0x7FFF) == I16_MAX, "positive signed endpoint is wrong")
    require(unsigned_to_signed(0x8000) == I16_MIN, "negative signed endpoint is wrong")
    require(unsigned_to_signed(U16_MAX) == -1, "all-one signed interpretation is wrong")
    require(signed_to_unsigned(I16_MIN) == 0x8000, "minimum i16 pattern is wrong")
    require(signed_to_unsigned(-1) == U16_MAX, "negative-one pattern is wrong")

    require(encode_u16(0x1234, "big") == bytes.fromhex("12 34"), "big-endian encoding is wrong")
    require(
        encode_u16(0x1234, "little") == bytes.fromhex("34 12"),
        "little-endian encoding is wrong",
    )
    require(decode_u16(bytes.fromhex("12 34"), "big") == 0x1234, "big decode is wrong")
    require(
        decode_u16(bytes.fromhex("12 34"), "little") == 0x3412,
        "little decode is wrong",
    )
    require(encode_i16(I16_MIN, "big") == bytes.fromhex("80 00"), "signed encoding is wrong")
    require(decode_i16(bytes.fromhex("ff ff"), "big") == -1, "signed decode is wrong")

    expect_error(TypeError, lambda: require_u16(True), "Boolean was accepted as u16")
    expect_error(ValueError, lambda: require_u16(-1), "negative u16 was accepted")
    expect_error(ValueError, lambda: require_u16(U16_MAX + 1), "oversized u16 was accepted")
    expect_error(ValueError, lambda: require_i16(I16_MIN - 1), "undersized i16 was accepted")
    expect_error(ValueError, lambda: require_i16(I16_MAX + 1), "oversized i16 was accepted")
    expect_error(TypeError, lambda: decode_u16(bytearray(2), "big"), "bytearray was accepted")
    expect_error(ValueError, lambda: decode_u16(b"\x00", "big"), "short word was accepted")
    expect_error(TypeError, lambda: encode_u16(1, ["big"]), "non-string byte order was accepted")
    expect_error(ValueError, lambda: encode_u16(1, "native"), "implicit native order was accepted")


def check_arithmetic_shifts_and_spans() -> None:
    require(checked_add_u16(1, 2) == 3, "checked addition is wrong")
    require(wrapping_add_u16(U16_MAX, 1) == 0, "wrapping addition is wrong")
    require(saturating_add_u16(U16_MAX, 1) == U16_MAX, "saturating addition is wrong")
    require(checked_add_u16(U16_MAX, 0) == U16_MAX, "checked endpoint is wrong")
    expect_error(
        OverflowError,
        lambda: checked_add_u16(U16_MAX, 1),
        "checked overflow was accepted",
    )

    require(checked_shift_left_u16(1, 15) == 0x8000, "maximum left shift is wrong")
    require(checked_shift_left_u16(U16_MAX, 0) == U16_MAX, "zero shift is wrong")
    require(logical_shift_right_u16(0x8000, 15) == 1, "maximum right shift is wrong")
    expect_error(
        OverflowError,
        lambda: checked_shift_left_u16(0x8000, 1),
        "discarding left shift was accepted",
    )
    expect_error(ValueError, lambda: checked_shift_left_u16(1, -1), "negative shift was accepted")
    expect_error(ValueError, lambda: checked_shift_left_u16(1, 16), "word-size shift was accepted")
    expect_error(TypeError, lambda: logical_shift_right_u16(1, True), "Boolean shift was accepted")

    require(checked_end(0, 0, 0) == 0, "empty span is wrong")
    require(
        checked_end(MAX_STREAM_BYTES, 0, MAX_STREAM_BYTES) == MAX_STREAM_BYTES,
        "endpoint span is wrong",
    )
    require(checked_end(8, 32, 40) == 40, "normal span is wrong")
    expect_error(ValueError, lambda: checked_end(41, 0, 40), "offset beyond limit was accepted")
    expect_error(ValueError, lambda: checked_end(8, 33, 40), "span beyond limit was accepted")


def check_records_positive_and_endpoints() -> None:
    record = Record(flags=3, sequence=0x1234, delta=-2, payload=b"AB")
    expected = bytes.fromhex("a5 13 12 34 ff fe 00 02 41 42")
    require(encode_record(record) == expected, "record bytes changed")
    require(decode_record(expected) == record, "record round trip failed")

    endpoint = Record(
        flags=MAX_FLAGS,
        sequence=U16_MAX,
        delta=I16_MIN,
        payload=b"\xff" * MAX_PAYLOAD_BYTES,
    )
    encoded_endpoint = encode_record(endpoint)
    require(len(encoded_endpoint) == HEADER_SIZE + MAX_PAYLOAD_BYTES, "maximum record size is wrong")
    require(decode_record(encoded_endpoint) == endpoint, "maximum record round trip failed")

    records = [endpoint] * MAX_RECORDS
    stream = encode_stream(records)
    require(len(stream) == MAX_STREAM_BYTES, "maximum stream size is wrong")
    require(parse_stream(stream) == tuple(records), "maximum stream did not round trip")
    require(encode_stream([]) == b"", "empty stream encoding is wrong")
    require(parse_stream(b"") == (), "empty stream parsing is wrong")


def check_record_failures() -> None:
    record = Record(flags=0, sequence=1, delta=0, payload=b"x")
    encoded = bytearray(encode_record(record))

    expect_error(TypeError, lambda: Record(0, 1, 0, bytearray()), "mutable payload was accepted")
    expect_error(ValueError, lambda: Record(MAX_FLAGS + 1, 1, 0, b""), "bad flags were accepted")
    expect_error(ValueError, lambda: Record(0, 1, 0, b"x" * 33), "large payload was accepted")
    expect_error(TypeError, lambda: encode_record((0, 1, 0, b"")), "non-record was accepted")
    expect_error(TypeError, lambda: encode_stream(iter(())), "unbounded iterable was accepted")
    expect_error(
        ValueError,
        lambda: encode_stream([record] * (MAX_RECORDS + 1)),
        "too many records were accepted",
    )
    expect_error(TypeError, lambda: decode_record(bytearray(encoded)), "mutable record bytes were accepted")
    expect_error(ValueError, lambda: decode_record(bytes(encoded[:7])), "short header was accepted")

    bad_magic = encoded.copy()
    bad_magic[0] = 0
    expect_error(ValueError, lambda: decode_record(bytes(bad_magic)), "bad magic was accepted")
    bad_version = encoded.copy()
    bad_version[1] = 0x20
    expect_error(ValueError, lambda: decode_record(bytes(bad_version)), "bad version was accepted")
    bad_length = encoded.copy()
    bad_length[7] = 2
    expect_error(ValueError, lambda: decode_record(bytes(bad_length)), "truncation was accepted")
    oversized_declaration = bytes.fromhex("a5 10 00 00 00 00 00 21")
    expect_error(
        ValueError,
        lambda: decode_record(oversized_declaration),
        "oversized payload declaration was accepted",
    )
    trailing = bytes(encoded) + b"z"
    expect_error(ValueError, lambda: decode_record(trailing), "trailing record byte was accepted")

    header_only = encode_record(Record(0, 0, 0, b""))
    expect_error(
        ValueError,
        lambda: parse_stream(header_only * (MAX_RECORDS + 1)),
        "stream record-count budget was not enforced",
    )
    expect_error(
        ValueError,
        lambda: parse_stream(b"\x00" * (MAX_STREAM_BYTES + 1)),
        "stream byte budget was not enforced",
    )


def check_program_and_deliberate_failure() -> None:
    environment = dict(os.environ)
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    with tempfile.TemporaryDirectory(prefix="sys-101-smoke-") as temporary_value:
        temporary = Path(temporary_value)
        worked = subprocess.run(
            [sys.executable, "-B", str(EXAMPLES / "record_worked.py")],
            cwd=temporary,
            env=environment,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=8,
            check=False,
        )
        require(worked.returncode == 0, f"worked example failed: {worked.stderr}")
        require(worked.stderr == "", "worked example wrote a diagnostic")
        require(
            "record bytes: a5 13 12 34 ff fe 00 02 41 42" in worked.stdout,
            "worked record output is missing",
        )
        require("parsed records: 2" in worked.stdout, "worked parse output is missing")
        evidence = temporary / "worked.stdout"
        evidence.write_text(worked.stdout, encoding="utf-8")
        require(evidence.read_text(encoding="utf-8") == worked.stdout, "temporary evidence changed")

        deliberate = temporary / "deliberate_failure.py"
        import_line = f"import sys; sys.path.insert(0, {str(EXAMPLES)!r})\n"
        deliberate.write_text(
            import_line
            + "from bounded_record import wrapping_add_u16\n"
            + "assert wrapping_add_u16(65535, 1) == 1, 'intentionally wrong expected wrap'\n",
            encoding="utf-8",
        )
        failed = subprocess.run(
            [sys.executable, "-B", str(deliberate)],
            cwd=temporary,
            env=environment,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=8,
            check=False,
        )
        require(failed.returncode != 0, "deliberately wrong expectation did not fail")
        require(failed.stdout == "", "deliberate failure wrote success output")
        require("AssertionError" in failed.stderr, "deliberate failure was not observable")

        deliberate.write_text(
            import_line
            + "from bounded_record import wrapping_add_u16\n"
            + "assert wrapping_add_u16(65535, 1) == 0\n"
            + "print('deliberate recovery: PASS')\n",
            encoding="utf-8",
        )
        recovered = subprocess.run(
            [sys.executable, "-B", str(deliberate)],
            cwd=temporary,
            env=environment,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=8,
            check=False,
        )
        require(recovered.returncode == 0, "corrected expectation did not pass")
        require(recovered.stderr == "", "corrected run wrote a diagnostic")
        require(recovered.stdout == "deliberate recovery: PASS\n", "corrected output changed")


def main() -> int:
    check_words_and_endianness()
    check_arithmetic_shifts_and_spans()
    check_records_positive_and_endpoints()
    check_record_failures()
    check_program_and_deliberate_failure()
    print("sys-101 lab smoke: PASS")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as error:
        print(f"sys-101 lab smoke: FAIL: {error}", file=sys.stderr)
        raise SystemExit(1)
