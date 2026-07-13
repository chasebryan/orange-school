#!/usr/bin/env python3
"""Bounded SHA-256, HMAC, and PBKDF2 mechanics for CRY-102.

This module demonstrates standard-library APIs and input contracts. It does not
implement encryption or AEAD, manage production secrets, or define a production
parameter profile.
"""

from __future__ import annotations

import hashlib
import hmac


MAX_MESSAGE_BYTES = 1_048_576
MIN_HMAC_KEY_BYTES = 16
MAX_HMAC_KEY_BYTES = 64
MAX_PASSWORD_BYTES = 1_024
MIN_SALT_BYTES = 16
MAX_SALT_BYTES = 64
MIN_LAB_PBKDF2_ITERATIONS = 1
MAX_LAB_PBKDF2_ITERATIONS = 50_000
MIN_DERIVED_KEY_BYTES = 16
MAX_DERIVED_KEY_BYTES = 64
SHA256_BYTES = 32


def _bounded_bytes(
    value: object,
    label: str,
    *,
    minimum: int,
    maximum: int,
) -> bytes:
    if type(value) is not bytes:
        raise TypeError(f"{label} must be bytes")
    if not minimum <= len(value) <= maximum:
        raise ValueError(f"{label} must contain {minimum} through {maximum} bytes")
    return value


def _plain_int(value: object, label: str, *, minimum: int, maximum: int) -> int:
    if type(value) is not int:
        raise TypeError(f"{label} must be an integer")
    if not minimum <= value <= maximum:
        raise ValueError(f"{label} must be from {minimum} through {maximum}")
    return value


def sha256_digest(message: object) -> bytes:
    """Return the SHA-256 digest of a bounded byte string."""

    checked = _bounded_bytes(
        message,
        "message",
        minimum=0,
        maximum=MAX_MESSAGE_BYTES,
    )
    return hashlib.sha256(checked).digest()


def hmac_sha256_tag(key: object, message: object) -> bytes:
    """Return a full-length HMAC-SHA-256 tag within the lab envelope."""

    checked_key = _bounded_bytes(
        key,
        "key",
        minimum=MIN_HMAC_KEY_BYTES,
        maximum=MAX_HMAC_KEY_BYTES,
    )
    checked_message = _bounded_bytes(
        message,
        "message",
        minimum=0,
        maximum=MAX_MESSAGE_BYTES,
    )
    return hmac.new(checked_key, checked_message, hashlib.sha256).digest()


def verify_hmac_sha256(key: object, message: object, received_tag: object) -> bool:
    """Verify a full tag with compare_digest; malformed tag lengths fail closed."""

    if type(received_tag) is not bytes:
        raise TypeError("received_tag must be bytes")
    expected = hmac_sha256_tag(key, message)
    if len(received_tag) != SHA256_BYTES:
        return False
    return hmac.compare_digest(expected, received_tag)


def derive_pbkdf2_sha256(
    password: object,
    salt: object,
    iterations: object,
    output_bytes: object,
) -> bytes:
    """Exercise PBKDF2-HMAC-SHA-256 under a deliberately bounded lab profile.

    The iteration interval exists to keep an offline smoke check fast. It is
    not a deployment recommendation. Production password storage needs a
    reviewed, benchmarked, versioned profile and a maintained library.
    """

    checked_password = _bounded_bytes(
        password,
        "password",
        minimum=1,
        maximum=MAX_PASSWORD_BYTES,
    )
    checked_salt = _bounded_bytes(
        salt,
        "salt",
        minimum=MIN_SALT_BYTES,
        maximum=MAX_SALT_BYTES,
    )
    checked_iterations = _plain_int(
        iterations,
        "iterations",
        minimum=MIN_LAB_PBKDF2_ITERATIONS,
        maximum=MAX_LAB_PBKDF2_ITERATIONS,
    )
    checked_output_bytes = _plain_int(
        output_bytes,
        "output_bytes",
        minimum=MIN_DERIVED_KEY_BYTES,
        maximum=MAX_DERIVED_KEY_BYTES,
    )
    return hashlib.pbkdf2_hmac(
        "sha256",
        checked_password,
        checked_salt,
        checked_iterations,
        dklen=checked_output_bytes,
    )
