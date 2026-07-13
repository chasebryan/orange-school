#!/usr/bin/env python3
"""Run public regression vectors and a non-secret manifest review."""

from __future__ import annotations

from crypto_mechanics import (
    derive_pbkdf2_sha256,
    hmac_sha256_tag,
    sha256_digest,
)
from protocol_manifest import make_course_manifest, validate_manifest


def main() -> int:
    sha_ok = sha256_digest(b"abc").hex() == (
        "ba7816bf8f01cfea414140de5dae2223"
        "b00361a396177a9cb410ff61f20015ad"
    )
    hmac_ok = hmac_sha256_tag(bytes.fromhex("0b" * 20), b"Hi There").hex() == (
        "b0344c61d8db38535ca8afceaf0bf12b"
        "881dc200c9833da726e9376c2e32cff7"
    )
    pbkdf2_ok = derive_pbkdf2_sha256(
        b"public-test-password",
        b"public-test-salt",
        1,
        32,
    ).hex() == "29fb0d372c7c0b61e7cc38657ef6b3f783e6b659e6e776875879aa2c6d0a85dd"
    manifest_ok = validate_manifest(make_course_manifest()) == ()

    checks = (
        ("SHA-256 public vector", sha_ok),
        ("HMAC-SHA-256 public vector", hmac_ok),
        ("PBKDF2-HMAC-SHA-256 lab vector", pbkdf2_ok),
        ("course manifest review", manifest_ok),
    )
    if not all(passed for _, passed in checks):
        raise AssertionError("one or more public mechanics checks failed")
    for label, _ in checks:
        print(f"{label}: PASS")
    print("no cipher or AEAD implementation is included")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
