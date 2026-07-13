#!/usr/bin/env python3
"""Smoke-check the bounded CRY-103 teaching examples."""

from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys
import tempfile


sys.dont_write_bytecode = True
MODULE_ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = MODULE_ROOT / "examples"
sys.path.insert(0, str(EXAMPLES))

from protocol_record import (  # noqa: E402
    MAX_IDENTIFIER_BYTES,
    MAX_MESSAGE_BYTES,
    MAX_MESSAGES,
    MAX_PROTOCOL_VERSION,
    MAX_PURPOSE_BYTES,
    PROFILE_ID,
    build_record,
    encode_bound_context,
    public_transcript_hash,
    validate_record,
)
from toy_group import (  # noqa: E402
    MAX_TOY_SCALAR,
    MIN_TOY_SCALAR,
    TOY_GENERATOR,
    TOY_PRIME,
    TOY_SUBGROUP_ORDER,
    enumerate_toy_subgroup,
    toy_agreement_value,
    toy_public_value,
    validate_toy_public,
    validate_toy_scalar,
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


def _messages() -> tuple[bytes, ...]:
    return (
        b"initiator-offer:orange-school-kem-record-v1",
        b"responder-select:orange-school-kem-record-v1",
        b"public-recipient-key-id:training-responder-7",
    )


def _record(messages: tuple[bytes, ...]) -> dict[str, object]:
    return build_record(
        messages,
        protocol_id="orange-school-transfer",
        protocol_version=1,
        role="initiator",
        initiator_key_id="training-initiator-3",
        responder_key_id="training-responder-7",
        purpose="bind a public teaching transcript",
    )


def check_toy_mechanics() -> None:
    require((TOY_PRIME, TOY_SUBGROUP_ORDER, TOY_GENERATOR) == (23, 11, 2), "toy profile changed")
    subgroup = enumerate_toy_subgroup()
    require(len(subgroup) == TOY_SUBGROUP_ORDER, "toy subgroup length is wrong")
    require(len(set(subgroup)) == TOY_SUBGROUP_ORDER, "toy generator order is wrong")
    require(set(subgroup) == {1, 2, 3, 4, 6, 8, 9, 12, 13, 16, 18}, "toy subgroup changed")

    alice_public = toy_public_value(3)
    bob_public = toy_public_value(7)
    require((alice_public, bob_public) == (8, 13), "toy public values are wrong")
    require(
        toy_agreement_value(3, bob_public) == toy_agreement_value(7, alice_public) == 12,
        "toy agreement mechanics are wrong",
    )
    require(toy_public_value(MIN_TOY_SCALAR) == 2, "minimum toy scalar failed")
    require(toy_public_value(MAX_TOY_SCALAR) == 12, "maximum toy scalar failed")

    expect_error(TypeError, lambda: validate_toy_scalar(True), "Boolean toy scalar was accepted")
    expect_error(TypeError, lambda: validate_toy_public(8.0), "float toy public value was accepted")
    expect_error(ValueError, lambda: validate_toy_scalar(0), "zero toy scalar was accepted")
    expect_error(
        ValueError,
        lambda: validate_toy_scalar(MAX_TOY_SCALAR + 1),
        "oversized toy scalar was accepted",
    )
    expect_error(ValueError, lambda: validate_toy_public(1), "identity public value was accepted")
    expect_error(ValueError, lambda: validate_toy_public(TOY_PRIME - 1), "minus-one value was accepted")
    expect_error(ValueError, lambda: validate_toy_public(5), "out-of-subgroup value was accepted")


def check_record_positive_and_boundaries() -> None:
    messages = _messages()
    record = _record(messages)
    validate_record(record, messages)
    require(record["profile_id"] == PROFILE_ID, "record profile is wrong")
    require(record["transcript_hash"] == public_transcript_hash(messages), "record hash is wrong")
    context = encode_bound_context(record, messages)
    require(context.startswith(b"orange-school-bound-context-v1\x00"), "context domain is missing")
    require(context == encode_bound_context(record, messages), "context encoding is unstable")

    changed_purpose = dict(record)
    changed_purpose["purpose"] = "bind a different public teaching transcript"
    validate_record(changed_purpose, messages)
    require(
        encode_bound_context(changed_purpose, messages) != context,
        "purpose was not included in the bound context",
    )
    changed_role = dict(record)
    changed_role["role"] = "responder"
    validate_record(changed_role, messages)
    require(
        encode_bound_context(changed_role, messages) != context,
        "role was not included in the bound context",
    )

    maximum_messages = tuple(b"m" * MAX_MESSAGE_BYTES for _ in range(MAX_MESSAGES))
    maximum_record = build_record(
        maximum_messages,
        protocol_id="p" * MAX_IDENTIFIER_BYTES,
        protocol_version=MAX_PROTOCOL_VERSION,
        role="responder",
        initiator_key_id="i" * MAX_IDENTIFIER_BYTES,
        responder_key_id="r" * MAX_IDENTIFIER_BYTES,
        purpose="x" * MAX_PURPOSE_BYTES,
    )
    require(len(encode_bound_context(maximum_record, maximum_messages)) > 0, "maximum record failed")


def check_record_invalid_inputs() -> None:
    messages = _messages()
    record = _record(messages)

    expect_error(TypeError, lambda: validate_record([], messages), "non-dictionary record was accepted")
    expect_error(TypeError, lambda: public_transcript_hash(list(messages)), "message list was accepted")
    expect_error(ValueError, lambda: public_transcript_hash(()), "empty transcript was accepted")
    expect_error(ValueError, lambda: public_transcript_hash((b"",)), "empty message was accepted")
    expect_error(
        TypeError,
        lambda: public_transcript_hash(("public text",)),
        "text message was accepted instead of bytes",
    )
    expect_error(
        ValueError,
        lambda: public_transcript_hash(tuple(b"x" for _ in range(MAX_MESSAGES + 1))),
        "too many messages were accepted",
    )
    expect_error(
        ValueError,
        lambda: public_transcript_hash((b"x" * (MAX_MESSAGE_BYTES + 1),)),
        "oversized message was accepted",
    )

    missing = dict(record)
    del missing["purpose"]
    expect_error(ValueError, lambda: validate_record(missing, messages), "missing field was accepted")
    extra = dict(record)
    extra["unknown"] = "value"
    expect_error(ValueError, lambda: validate_record(extra, messages), "unknown field was accepted")

    invalid_changes: tuple[tuple[type[BaseException], str, object], ...] = (
        (ValueError, "profile_id", "orange-school-kem-record-v2"),
        (ValueError, "kem_id", "unregistered-kem"),
        (ValueError, "role", "observer"),
        (ValueError, "protocol_id", "bad protocol"),
        (TypeError, "protocol_version", True),
        (ValueError, "protocol_version", 0),
        (ValueError, "purpose", "line one\nline two"),
        (ValueError, "offered_profile_ids", (PROFILE_ID, PROFILE_ID)),
        (ValueError, "transcript_hash", "A" * 64),
        (ValueError, "nonce_requirement", "caller-selected"),
        (ValueError, "failure_policy", "detailed-secret-dependent-errors"),
    )
    for error_type, field, value in invalid_changes:
        changed = dict(record)
        changed[field] = value
        expect_error(
            error_type,
            lambda changed=changed: validate_record(changed, messages),
            f"invalid {field} was accepted",
        )

    same_identity = dict(record)
    same_identity["responder_key_id"] = same_identity["initiator_key_id"]
    expect_error(ValueError, lambda: validate_record(same_identity, messages), "same peer IDs were accepted")
    changed_messages = messages[:-1] + (b"public-recipient-key-id:attacker",)
    expect_error(
        ValueError,
        lambda: validate_record(record, changed_messages),
        "transcript mutation was not detected",
    )


def check_worked_program() -> None:
    with tempfile.TemporaryDirectory(prefix="cry-103-smoke-") as temporary:
        environment = os.environ.copy()
        environment["PYTHONDONTWRITEBYTECODE"] = "1"
        result = subprocess.run(
            [sys.executable, "-B", str(EXAMPLES / "worked_case.py")],
            cwd=temporary,
            env=environment,
            text=True,
            capture_output=True,
            timeout=8,
            check=False,
        )
        require(result.returncode == 0, f"worked example failed: {result.stderr}")
        require(result.stderr == "", "worked example wrote a diagnostic")
        require("toy public values: 8, 13" in result.stdout, "toy public output is missing")
        require("toy public teaching result: 12" in result.stdout, "toy agreement output is missing")
        require(f"record profile: {PROFILE_ID}" in result.stdout, "profile output is missing")
        require("public transcript hash:" in result.stdout, "transcript output is missing")
        require(
            "no encryption, signature, KEM, or production security" in result.stdout,
            "worked example lost its security boundary",
        )
        evidence = Path(temporary) / "worked.stdout"
        evidence.write_text(result.stdout, encoding="utf-8")
        require(evidence.read_text(encoding="utf-8") == result.stdout, "temporary evidence changed")


def main() -> int:
    check_toy_mechanics()
    check_record_positive_and_boundaries()
    check_record_invalid_inputs()
    check_worked_program()
    print("cry-103 lab smoke: PASS")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as error:
        print(f"cry-103 lab smoke: FAIL: {error}", file=sys.stderr)
        raise SystemExit(1)
