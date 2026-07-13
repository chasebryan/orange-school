#!/usr/bin/env python3
"""Validate a non-secret CRY-102 protocol-review manifest.

The accepted values form a course audit profile, not universal algorithm
approval. This module validates metadata consistency only. It implements no
cipher, AEAD, key generation, key storage, or wire protocol.
"""

from __future__ import annotations

import re
from collections.abc import Mapping


SCHEMA = "cry-102-review-manifest-v1"
DEPLOYMENT_PROFILE = "course-audit-only"
LABEL_RE = re.compile(r"^[a-z0-9][a-z0-9./_-]{15,127}$")


def make_course_manifest() -> dict[str, object]:
    """Return a fresh, non-secret manifest that satisfies the course profile."""

    return {
        "schema": SCHEMA,
        "deployment_profile": DEPLOYMENT_PROFILE,
        "domains": {
            "aead_aad": "orange.example/records/aead-aad/v1",
            "hkdf_info": "orange.example/records/hkdf-info/v1",
            "audit_hmac": "orange.example/records/audit-hmac/v1",
        },
        "key_labels": {
            "record_aead": "record-aead-key-v1",
            "audit_mac": "audit-mac-key-v1",
            "password_verifier": "password-verifier-v1",
        },
        "aead": {
            "algorithm": "AES-256-GCM",
            "key_bits": 256,
            "nonce_bytes": 12,
            "tag_bytes": 16,
            "nonce_rule": "unique-per-key",
            "aad_domain_ref": "aead_aad",
            "key_ref": "record_aead",
            "failure_policy": "reject-before-plaintext",
        },
        "key_derivation": {
            "algorithm": "HKDF-SHA-256",
            "source_kind": "high-entropy-shared-secret",
            "salt_rule": "protocol-defined",
            "info_domain_ref": "hkdf_info",
            "output_key_ref": "record_aead",
        },
        "password_storage": {
            "algorithm": "PBKDF2-HMAC-SHA-256",
            "parameter_authority": "deployment-security-policy",
            "salt_bytes_min": 16,
            "work_factor_rule": "benchmarked-versioned-cost",
            "output_key_ref": "password_verifier",
        },
        "audit_mac": {
            "algorithm": "HMAC-SHA-256",
            "tag_bytes": 32,
            "input_domain_ref": "audit_hmac",
            "key_ref": "audit_mac",
            "failure_policy": "reject",
        },
    }


def _mapping(value: object, label: str, errors: list[str]) -> Mapping[str, object]:
    if not isinstance(value, Mapping):
        errors.append(f"{label} must be a mapping")
        return {}
    return value


def _exact_keys(
    value: Mapping[str, object],
    expected: set[str],
    label: str,
    errors: list[str],
) -> None:
    actual = set(value)
    for name in sorted(expected - actual):
        errors.append(f"{label} is missing {name}")
    for name in sorted(actual - expected):
        errors.append(f"{label} has unexpected field {name}")


def _require_equal(
    value: Mapping[str, object],
    name: str,
    expected: object,
    label: str,
    errors: list[str],
) -> None:
    if value.get(name) != expected or type(value.get(name)) is not type(expected):
        errors.append(f"{label}.{name} must equal {expected!r}")


def _validate_named_values(
    value: Mapping[str, object],
    expected_names: set[str],
    label: str,
    errors: list[str],
) -> None:
    _exact_keys(value, expected_names, label, errors)
    observed: list[str] = []
    for name in sorted(expected_names):
        item = value.get(name)
        if not isinstance(item, str) or not LABEL_RE.fullmatch(item):
            errors.append(f"{label}.{name} must be a bounded lowercase label")
            continue
        observed.append(item)
    if len(observed) != len(set(observed)):
        errors.append(f"{label} values must be distinct")


def validate_manifest(candidate: object) -> tuple[str, ...]:
    """Return every deterministic course-profile violation, or an empty tuple."""

    errors: list[str] = []
    manifest = _mapping(candidate, "manifest", errors)
    expected_top = {
        "schema",
        "deployment_profile",
        "domains",
        "key_labels",
        "aead",
        "key_derivation",
        "password_storage",
        "audit_mac",
    }
    _exact_keys(manifest, expected_top, "manifest", errors)
    _require_equal(manifest, "schema", SCHEMA, "manifest", errors)
    _require_equal(
        manifest,
        "deployment_profile",
        DEPLOYMENT_PROFILE,
        "manifest",
        errors,
    )

    domains = _mapping(manifest.get("domains"), "domains", errors)
    domain_names = {"aead_aad", "hkdf_info", "audit_hmac"}
    _validate_named_values(domains, domain_names, "domains", errors)

    key_labels = _mapping(manifest.get("key_labels"), "key_labels", errors)
    key_names = {"record_aead", "audit_mac", "password_verifier"}
    _validate_named_values(key_labels, key_names, "key_labels", errors)

    aead = _mapping(manifest.get("aead"), "aead", errors)
    _exact_keys(
        aead,
        {
            "algorithm",
            "key_bits",
            "nonce_bytes",
            "tag_bytes",
            "nonce_rule",
            "aad_domain_ref",
            "key_ref",
            "failure_policy",
        },
        "aead",
        errors,
    )
    for name, expected in (
        ("algorithm", "AES-256-GCM"),
        ("key_bits", 256),
        ("nonce_bytes", 12),
        ("tag_bytes", 16),
        ("nonce_rule", "unique-per-key"),
        ("aad_domain_ref", "aead_aad"),
        ("key_ref", "record_aead"),
        ("failure_policy", "reject-before-plaintext"),
    ):
        _require_equal(aead, name, expected, "aead", errors)

    derivation = _mapping(manifest.get("key_derivation"), "key_derivation", errors)
    _exact_keys(
        derivation,
        {
            "algorithm",
            "source_kind",
            "salt_rule",
            "info_domain_ref",
            "output_key_ref",
        },
        "key_derivation",
        errors,
    )
    for name, expected in (
        ("algorithm", "HKDF-SHA-256"),
        ("source_kind", "high-entropy-shared-secret"),
        ("salt_rule", "protocol-defined"),
        ("info_domain_ref", "hkdf_info"),
        ("output_key_ref", "record_aead"),
    ):
        _require_equal(derivation, name, expected, "key_derivation", errors)

    password = _mapping(manifest.get("password_storage"), "password_storage", errors)
    _exact_keys(
        password,
        {
            "algorithm",
            "parameter_authority",
            "salt_bytes_min",
            "work_factor_rule",
            "output_key_ref",
        },
        "password_storage",
        errors,
    )
    for name, expected in (
        ("algorithm", "PBKDF2-HMAC-SHA-256"),
        ("parameter_authority", "deployment-security-policy"),
        ("salt_bytes_min", 16),
        ("work_factor_rule", "benchmarked-versioned-cost"),
        ("output_key_ref", "password_verifier"),
    ):
        _require_equal(password, name, expected, "password_storage", errors)

    audit_mac = _mapping(manifest.get("audit_mac"), "audit_mac", errors)
    _exact_keys(
        audit_mac,
        {
            "algorithm",
            "tag_bytes",
            "input_domain_ref",
            "key_ref",
            "failure_policy",
        },
        "audit_mac",
        errors,
    )
    for name, expected in (
        ("algorithm", "HMAC-SHA-256"),
        ("tag_bytes", 32),
        ("input_domain_ref", "audit_hmac"),
        ("key_ref", "audit_mac"),
        ("failure_policy", "reject"),
    ):
        _require_equal(audit_mac, name, expected, "audit_mac", errors)

    return tuple(errors)
