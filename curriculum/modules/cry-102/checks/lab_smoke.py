#!/usr/bin/env python3
"""Smoke-check CRY-102 bounded mechanics and manifest failure behavior."""

from __future__ import annotations

from copy import deepcopy
import os
from pathlib import Path
import subprocess
import sys
import tempfile


sys.dont_write_bytecode = True
MODULE_ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = MODULE_ROOT / "examples"
RESOURCES = MODULE_ROOT / "resources"
sys.path.insert(0, str(EXAMPLES))

from crypto_mechanics import (  # noqa: E402
    MAX_DERIVED_KEY_BYTES,
    MAX_HMAC_KEY_BYTES,
    MAX_LAB_PBKDF2_ITERATIONS,
    MAX_MESSAGE_BYTES,
    MAX_PASSWORD_BYTES,
    MAX_SALT_BYTES,
    MIN_DERIVED_KEY_BYTES,
    MIN_HMAC_KEY_BYTES,
    MIN_LAB_PBKDF2_ITERATIONS,
    MIN_SALT_BYTES,
    derive_pbkdf2_sha256,
    hmac_sha256_tag,
    sha256_digest,
    verify_hmac_sha256,
)
from protocol_manifest import make_course_manifest, validate_manifest  # noqa: E402


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def expect_error(error_type: type[BaseException], action, message: str) -> None:
    try:
        action()
    except error_type:
        return
    raise AssertionError(message)


def check_public_vectors_and_verification() -> None:
    require(
        sha256_digest(b"abc").hex()
        == "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad",
        "SHA-256 public vector changed",
    )
    public_key = bytes.fromhex("0b" * 20)
    expected_tag = bytes.fromhex(
        "b0344c61d8db38535ca8afceaf0bf12b"
        "881dc200c9833da726e9376c2e32cff7"
    )
    require(hmac_sha256_tag(public_key, b"Hi There") == expected_tag, "HMAC vector changed")
    require(verify_hmac_sha256(public_key, b"Hi There", expected_tag), "valid HMAC failed")
    require(
        not verify_hmac_sha256(public_key, b"Hi There!", expected_tag),
        "changed message passed HMAC verification",
    )
    require(
        not verify_hmac_sha256(public_key, b"Hi There", expected_tag[:-1]),
        "truncated tag passed HMAC verification",
    )


def check_bounds_and_invalid_inputs() -> None:
    require(len(sha256_digest(b"")) == 32, "empty-message boundary failed")
    require(
        len(sha256_digest(b"x" * MAX_MESSAGE_BYTES)) == 32,
        "maximum-message boundary failed",
    )
    require(
        len(hmac_sha256_tag(b"k" * MIN_HMAC_KEY_BYTES, b"")) == 32,
        "minimum HMAC-key boundary failed",
    )
    require(
        len(hmac_sha256_tag(b"k" * MAX_HMAC_KEY_BYTES, b"message")) == 32,
        "maximum HMAC-key boundary failed",
    )

    salt_min = b"s" * MIN_SALT_BYTES
    salt_max = b"s" * MAX_SALT_BYTES
    low = derive_pbkdf2_sha256(
        b"public-test-password",
        salt_min,
        MIN_LAB_PBKDF2_ITERATIONS,
        MIN_DERIVED_KEY_BYTES,
    )
    high = derive_pbkdf2_sha256(
        b"p" * MAX_PASSWORD_BYTES,
        salt_max,
        MAX_LAB_PBKDF2_ITERATIONS,
        MAX_DERIVED_KEY_BYTES,
    )
    require(len(low) == MIN_DERIVED_KEY_BYTES, "minimum PBKDF2 boundary failed")
    require(len(high) == MAX_DERIVED_KEY_BYTES, "maximum PBKDF2 boundary failed")

    expect_error(TypeError, lambda: sha256_digest("abc"), "text hash input was accepted")
    expect_error(
        ValueError,
        lambda: sha256_digest(b"x" * (MAX_MESSAGE_BYTES + 1)),
        "oversized hash input was accepted",
    )
    expect_error(
        ValueError,
        lambda: hmac_sha256_tag(b"k" * (MIN_HMAC_KEY_BYTES - 1), b"message"),
        "short lab HMAC key was accepted",
    )
    expect_error(
        TypeError,
        lambda: derive_pbkdf2_sha256(b"password", salt_min, True, 32),
        "Boolean iteration count was accepted",
    )
    expect_error(
        ValueError,
        lambda: derive_pbkdf2_sha256(b"password", b"s" * (MIN_SALT_BYTES - 1), 1, 32),
        "short salt was accepted",
    )
    expect_error(
        ValueError,
        lambda: derive_pbkdf2_sha256(
            b"password",
            salt_min,
            MAX_LAB_PBKDF2_ITERATIONS + 1,
            32,
        ),
        "oversized lab iteration count was accepted",
    )
    expect_error(
        ValueError,
        lambda: derive_pbkdf2_sha256(b"", salt_min, 1, 32),
        "empty password was accepted by the lab contract",
    )


def check_manifest_policy_and_failures() -> None:
    valid = make_course_manifest()
    require(validate_manifest(valid) == (), "course manifest was rejected")

    mutations: tuple[tuple[str, object], ...] = (
        ("nonce reuse rule", ("aead", "nonce_rule", "random-best-effort")),
        ("nonce size", ("aead", "nonce_bytes", 8)),
        ("tag size", ("aead", "tag_bytes", 12)),
        ("plaintext release", ("aead", "failure_policy", "return-then-check")),
        ("unknown AEAD", ("aead", "algorithm", "HOME-GROWN-AEAD")),
        ("password authority", ("password_storage", "parameter_authority", "source-code-default")),
        ("KDF source kind", ("key_derivation", "source_kind", "user-password")),
    )
    for label, mutation in mutations:
        section, field, replacement = mutation
        changed = deepcopy(valid)
        nested = changed[section]
        require(isinstance(nested, dict), "test fixture section is not mutable")
        nested[field] = replacement
        require(validate_manifest(changed) != (), f"manifest accepted invalid {label}")

    duplicate_key = deepcopy(valid)
    labels = duplicate_key["key_labels"]
    require(isinstance(labels, dict), "key label fixture is not mutable")
    labels["audit_mac"] = labels["record_aead"]
    require(validate_manifest(duplicate_key) != (), "reused key label was accepted")

    duplicate_domain = deepcopy(valid)
    domains = duplicate_domain["domains"]
    require(isinstance(domains, dict), "domain fixture is not mutable")
    domains["audit_hmac"] = domains["aead_aad"]
    require(validate_manifest(duplicate_domain) != (), "reused domain was accepted")

    secret_field = deepcopy(valid)
    secret_field["key_material"] = "not-permitted"
    errors = validate_manifest(secret_field)
    require(
        "manifest has unexpected field key_material" in errors,
        "manifest accepted an embedded key-material field",
    )
    require(validate_manifest([]) != (), "non-mapping manifest was accepted")


def check_assessment_profile_is_complete() -> None:
    profile = (RESOURCES / "station-assessment-profile-r7.md").read_text(
        encoding="utf-8"
    )
    required_evidence = (
        "station-assessment-profile-r7",
        "station-r7/sensor-record/aad/v1",
        "station-r7/sensor-record/key/v1",
        "station-r7/audit-envelope/key/v1",
        "station-r7/audit-envelope/input/v1",
        "u32be(writer_id) || u64be(writer_counter)",
        "2^10-1",
        "3 * 2^10",
        "65,536",
        "3 * 2^22",
        "not an assertion that reaching the cap is safe",
        "station-record-ingress-r7",
        "station-password-benchmark-2026-06-r7",
        "fictional operational limits",
    )
    for evidence in required_evidence:
        require(evidence in profile, f"assessment profile lost {evidence!r}")


def check_worked_program_in_temporary_directory() -> None:
    expected_stdout = (
        "SHA-256 public vector: PASS\n"
        "HMAC-SHA-256 public vector: PASS\n"
        "PBKDF2-HMAC-SHA-256 lab vector: PASS\n"
        "course manifest review: PASS\n"
        "no cipher or AEAD implementation is included\n"
    )
    with tempfile.TemporaryDirectory(prefix="cry-102-smoke-") as temporary:
        environment = os.environ.copy()
        environment["PYTHONDONTWRITEBYTECODE"] = "1"
        result = subprocess.run(
            [sys.executable, "-B", str(EXAMPLES / "worked_review.py")],
            cwd=temporary,
            env=environment,
            text=True,
            capture_output=True,
            timeout=8,
            check=False,
        )
        require(result.returncode == 0, f"worked review failed: {result.stderr}")
        require(result.stderr == "", "worked review wrote a diagnostic")
        require(result.stdout == expected_stdout, "worked review output changed")
        evidence = Path(temporary) / "worked-review.stdout"
        evidence.write_text(result.stdout, encoding="utf-8")
        require(evidence.read_text(encoding="utf-8") == expected_stdout, "evidence changed")


def main() -> int:
    check_public_vectors_and_verification()
    check_bounds_and_invalid_inputs()
    check_manifest_policy_and_failures()
    check_assessment_profile_is_complete()
    check_worked_program_in_temporary_directory()
    print("cry-102 lab smoke: PASS")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as error:
        print(f"cry-102 lab smoke: FAIL: {error}", file=sys.stderr)
        raise SystemExit(1)
