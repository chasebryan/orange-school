"""Strict public-transcript record validation for a teaching profile.

This module performs no cryptographic protocol operation.  It accepts only
public messages and metadata, validates a fixed record shape, and produces an
unambiguous byte encoding that a separately reviewed protocol could bind.  A
valid record is evidence of structural consistency, not key authenticity,
confidentiality, integrity, standards conformance, or production security.
"""

from __future__ import annotations

import hashlib
import re
from typing import Any


PROFILE_ID = "orange-school-kem-record-v1"
KEM_ID = "ML-KEM-768"
KDF_ID = "HKDF-SHA256"
AEAD_ID = "AES-256-GCM"
AUTHENTICITY_REQUIREMENT = "external-pki-path-validation-required"
NONCE_REQUIREMENT = "implementation-managed-unique-per-key"
FAILURE_POLICY = "single-public-reject"

MAX_MESSAGES = 16
MAX_MESSAGE_BYTES = 2_048
MAX_IDENTIFIER_BYTES = 64
MAX_PURPOSE_BYTES = 96
MAX_PROTOCOL_VERSION = 65_535

_TOKEN_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:@/-]*$")
_LOWER_HEX_256_RE = re.compile(r"^[0-9a-f]{64}$")
_RECORD_KEYS = frozenset(
    {
        "profile_id",
        "kem_id",
        "kdf_id",
        "aead_id",
        "protocol_id",
        "protocol_version",
        "role",
        "initiator_key_id",
        "responder_key_id",
        "purpose",
        "offered_profile_ids",
        "transcript_hash",
        "key_authenticity_requirement",
        "nonce_requirement",
        "failure_policy",
    }
)
_CONTEXT_ORDER = (
    "profile_id",
    "kem_id",
    "kdf_id",
    "aead_id",
    "protocol_id",
    "protocol_version",
    "role",
    "initiator_key_id",
    "responder_key_id",
    "purpose",
    "offered_profile_ids",
    "transcript_hash",
    "key_authenticity_requirement",
    "nonce_requirement",
    "failure_policy",
)


def _validate_token(value: object, name: str) -> str:
    if type(value) is not str:
        raise TypeError(f"{name} must be a string")
    try:
        encoded = value.encode("ascii")
    except UnicodeEncodeError as error:
        raise ValueError(f"{name} must contain ASCII only") from error
    if not 1 <= len(encoded) <= MAX_IDENTIFIER_BYTES:
        raise ValueError(f"{name} length is outside 1..{MAX_IDENTIFIER_BYTES}")
    if _TOKEN_RE.fullmatch(value) is None:
        raise ValueError(f"{name} contains a disallowed character")
    return value


def _validate_purpose(value: object) -> str:
    if type(value) is not str:
        raise TypeError("purpose must be a string")
    try:
        encoded = value.encode("ascii")
    except UnicodeEncodeError as error:
        raise ValueError("purpose must contain ASCII only") from error
    if not 1 <= len(encoded) <= MAX_PURPOSE_BYTES:
        raise ValueError(f"purpose length is outside 1..{MAX_PURPOSE_BYTES}")
    if any(byte < 0x20 or byte > 0x7E for byte in encoded):
        raise ValueError("purpose must contain printable ASCII only")
    if value != value.strip():
        raise ValueError("purpose must not have surrounding whitespace")
    return value


def validate_public_messages(messages: object) -> tuple[bytes, ...]:
    """Validate an ordered tuple of bounded, public transcript messages."""

    if type(messages) is not tuple:
        raise TypeError("public messages must be a tuple")
    if not 1 <= len(messages) <= MAX_MESSAGES:
        raise ValueError(f"public message count is outside 1..{MAX_MESSAGES}")
    checked: list[bytes] = []
    for index, message in enumerate(messages):
        if type(message) is not bytes:
            raise TypeError(f"public message {index} must be bytes")
        if not 1 <= len(message) <= MAX_MESSAGE_BYTES:
            raise ValueError(
                f"public message {index} length is outside 1..{MAX_MESSAGE_BYTES}"
            )
        checked.append(message)
    return tuple(checked)


def _frame(value: bytes) -> bytes:
    if len(value) > 65_535:
        raise ValueError("framed value is too long")
    return len(value).to_bytes(2, "big") + value


def public_transcript_hash(messages: object) -> str:
    """Hash an unambiguous encoding of public messages for recordkeeping."""

    checked = validate_public_messages(messages)
    digest = hashlib.sha256(b"orange-school-public-transcript-v1\x00")
    digest.update(len(checked).to_bytes(2, "big"))
    for message in checked:
        digest.update(_frame(message))
    return digest.hexdigest()


def build_record(
    messages: object,
    *,
    protocol_id: object,
    protocol_version: object,
    role: object,
    initiator_key_id: object,
    responder_key_id: object,
    purpose: object,
) -> dict[str, Any]:
    """Build and validate one metadata-only public transcript record."""

    record: dict[str, Any] = {
        "profile_id": PROFILE_ID,
        "kem_id": KEM_ID,
        "kdf_id": KDF_ID,
        "aead_id": AEAD_ID,
        "protocol_id": protocol_id,
        "protocol_version": protocol_version,
        "role": role,
        "initiator_key_id": initiator_key_id,
        "responder_key_id": responder_key_id,
        "purpose": purpose,
        "offered_profile_ids": (PROFILE_ID,),
        "transcript_hash": public_transcript_hash(messages),
        "key_authenticity_requirement": AUTHENTICITY_REQUIREMENT,
        "nonce_requirement": NONCE_REQUIREMENT,
        "failure_policy": FAILURE_POLICY,
    }
    validate_record(record, messages)
    return record


def validate_record(record: object, messages: object) -> None:
    """Reject every malformed, unknown, mismatched, or unbound field."""

    checked_messages = validate_public_messages(messages)
    if type(record) is not dict:
        raise TypeError("record must be a plain dictionary")
    if set(record) != _RECORD_KEYS:
        missing = sorted(_RECORD_KEYS - set(record))
        extra = sorted(set(record) - _RECORD_KEYS)
        raise ValueError(f"record keys mismatch; missing={missing}, extra={extra}")

    fixed_values = {
        "profile_id": PROFILE_ID,
        "kem_id": KEM_ID,
        "kdf_id": KDF_ID,
        "aead_id": AEAD_ID,
        "key_authenticity_requirement": AUTHENTICITY_REQUIREMENT,
        "nonce_requirement": NONCE_REQUIREMENT,
        "failure_policy": FAILURE_POLICY,
    }
    for name, expected in fixed_values.items():
        if type(record[name]) is not str or record[name] != expected:
            raise ValueError(f"{name} does not match the fixed teaching profile")

    _validate_token(record["protocol_id"], "protocol_id")
    version = record["protocol_version"]
    if type(version) is not int:
        raise TypeError("protocol_version must be an exact integer")
    if not 1 <= version <= MAX_PROTOCOL_VERSION:
        raise ValueError(f"protocol_version is outside 1..{MAX_PROTOCOL_VERSION}")
    if record["role"] not in {"initiator", "responder"}:
        raise ValueError("role must be initiator or responder")

    initiator = _validate_token(record["initiator_key_id"], "initiator_key_id")
    responder = _validate_token(record["responder_key_id"], "responder_key_id")
    if initiator == responder:
        raise ValueError("initiator and responder key identifiers must differ")
    _validate_purpose(record["purpose"])

    offered = record["offered_profile_ids"]
    if type(offered) is not tuple or offered != (PROFILE_ID,):
        raise ValueError("offered_profile_ids must bind the fixed one-profile offer")
    transcript_hash = record["transcript_hash"]
    if type(transcript_hash) is not str or _LOWER_HEX_256_RE.fullmatch(transcript_hash) is None:
        raise ValueError("transcript_hash must be 64 lowercase hexadecimal characters")
    if transcript_hash != public_transcript_hash(checked_messages):
        raise ValueError("transcript_hash does not match the supplied public messages")


def encode_bound_context(record: object, messages: object) -> bytes:
    """Encode every validated field in a fixed, length-delimited order."""

    validate_record(record, messages)
    assert isinstance(record, dict)
    output = bytearray(b"orange-school-bound-context-v1\x00")
    for name in _CONTEXT_ORDER:
        value = record[name]
        if type(value) is tuple:
            encoded_value = b"".join(_frame(item.encode("ascii")) for item in value)
        else:
            encoded_value = str(value).encode("ascii")
        output.extend(_frame(name.encode("ascii")))
        output.extend(_frame(encoded_value))
    return bytes(output)
