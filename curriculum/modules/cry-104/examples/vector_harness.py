"""Strict offline provenance and SHA-256 vector checks for CRY-104.

This is evidence plumbing around Python's library implementation. It is not a
cryptographic implementation and does not confer algorithm or module validation.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path
import re
import stat
from typing import Any


MAX_JSON_BYTES = 1_000_000
MAX_ARTIFACTS = 100
MAX_SOURCE_ARTIFACTS = 20
MAX_VECTORS = 1_000
MAX_MESSAGE_BYTES = 1_000_000
HEX_64_RE = re.compile(r"[0-9a-f]{64}")
ID_RE = re.compile(r"[a-z0-9][a-z0-9-]{0,63}")


@dataclass(frozen=True)
class VectorResult:
    vector_id: str
    passed: bool
    actual_digest: str


@dataclass(frozen=True)
class VerifiedArtifact:
    path: Path
    content: bytes
    sha256: str


def _strict_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    value: dict[str, Any] = {}
    for key, item in pairs:
        if key in value:
            raise ValueError(f"duplicate JSON key: {key}")
        value[key] = item
    return value


def _read_bounded_file(path: Path) -> bytes:
    descriptor: int | None = None
    try:
        flags = os.O_RDONLY | getattr(os, "O_NONBLOCK", 0) | getattr(os, "O_CLOEXEC", 0)
        flags |= getattr(os, "O_NOFOLLOW", 0)
        descriptor = os.open(path, flags)
        metadata = os.fstat(descriptor)
        if not stat.S_ISREG(metadata.st_mode):
            raise ValueError(f"JSON artifact is not a regular file: {path}")
        with os.fdopen(descriptor, "rb") as source:
            descriptor = None
            content = source.read(MAX_JSON_BYTES + 1)
    except OSError as error:
        raise ValueError(f"could not read JSON artifact {path}: {error}") from error
    finally:
        if descriptor is not None:
            os.close(descriptor)
    if len(content) > MAX_JSON_BYTES:
        raise ValueError(f"JSON artifact exceeds {MAX_JSON_BYTES} bytes")
    return content


def _parse_json(content: bytes, label: str) -> Any:
    try:
        return json.loads(content.decode("utf-8"), object_pairs_hook=_strict_object)
    except (UnicodeError, json.JSONDecodeError) as error:
        raise ValueError(f"could not read strict JSON from {label}: {error}") from error


def _read_json(path: Path) -> Any:
    try:
        return _parse_json(_read_bounded_file(path), str(path))
    except ValueError:
        raise
    except OSError as error:
        raise ValueError(f"could not read strict JSON from {path}: {error}") from error


def _require_exact_keys(value: dict[str, Any], expected: set[str], label: str) -> None:
    actual = set(value)
    if actual != expected:
        raise ValueError(
            f"{label} keys differ: missing={sorted(expected - actual)}, "
            f"extra={sorted(actual - expected)}"
        )


def _require_schema_one(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"{label} must be an object")
    if type(value.get("schema_version")) is not int or value["schema_version"] != 1:
        raise ValueError(f"{label}.schema_version must be integer 1")
    return value


def _safe_artifact(root: Path, relative: Any) -> Path:
    if (
        not isinstance(relative, str)
        or not relative
        or "\\" in relative
        or Path(relative).is_absolute()
        or any(part in {"", ".", ".."} for part in Path(relative).parts)
    ):
        raise ValueError(f"unsafe artifact path: {relative!r}")
    resolved_root = root.resolve()
    candidate = (resolved_root / relative).resolve()
    try:
        candidate.relative_to(resolved_root)
    except ValueError as error:
        raise ValueError(f"artifact escapes provenance root: {relative!r}") from error
    return candidate


def file_sha256(path: Path) -> str:
    return hashlib.sha256(_read_bounded_file(path)).hexdigest()


def verify_provenance(
    manifest_path: Path, artifact_root: Path
) -> list[VerifiedArtifact]:
    manifest = _require_schema_one(_read_json(manifest_path), "manifest")
    _require_exact_keys(manifest, {"schema_version", "artifacts"}, "manifest")
    artifacts = manifest["artifacts"]
    if not isinstance(artifacts, list) or not 1 <= len(artifacts) <= MAX_ARTIFACTS:
        raise ValueError(f"manifest.artifacts must contain 1 through {MAX_ARTIFACTS} items")

    verified: list[VerifiedArtifact] = []
    identifiers: set[str] = set()
    required = {
        "id",
        "path",
        "sha256",
        "publisher",
        "source_title",
        "source_url",
        "retrieved",
        "status",
    }
    for index, artifact in enumerate(artifacts):
        if not isinstance(artifact, dict):
            raise ValueError(f"artifact {index} must be an object")
        _require_exact_keys(artifact, required, f"artifact {index}")
        identifier = artifact["id"]
        if not isinstance(identifier, str) or not ID_RE.fullmatch(identifier):
            raise ValueError(f"artifact {index} has invalid id")
        if identifier in identifiers:
            raise ValueError(f"duplicate artifact id: {identifier}")
        identifiers.add(identifier)
        for field in ("publisher", "source_title", "source_url", "retrieved", "status"):
            if not isinstance(artifact[field], str) or not artifact[field].strip():
                raise ValueError(f"artifact {identifier}.{field} must be nonempty text")
        expected = artifact["sha256"]
        if not isinstance(expected, str) or not HEX_64_RE.fullmatch(expected):
            raise ValueError(f"artifact {identifier}.sha256 must be lowercase SHA-256 hex")
        path = _safe_artifact(artifact_root, artifact["path"])
        try:
            content = _read_bounded_file(path)
        except ValueError as error:
            raise ValueError(f"artifact {identifier} could not be captured: {error}") from error
        actual = hashlib.sha256(content).hexdigest()
        if actual != expected:
            raise ValueError(
                f"artifact {identifier} digest mismatch: expected {expected}, got {actual}"
            )
        verified.append(VerifiedArtifact(path, content, actual))
    return verified


def _decode_hex(value: Any, label: str, *, digest: bool = False) -> bytes:
    if not isinstance(value, str) or len(value) % 2 != 0:
        raise ValueError(f"{label} must be even-length lowercase hexadecimal")
    if value.lower() != value or any(character not in "0123456789abcdef" for character in value):
        raise ValueError(f"{label} must be even-length lowercase hexadecimal")
    if digest and len(value) != 64:
        raise ValueError(f"{label} must encode a 32-byte SHA-256 digest")
    try:
        decoded = bytes.fromhex(value)
    except ValueError as error:
        raise ValueError(f"{label} is not hexadecimal") from error
    if not digest and len(decoded) > MAX_MESSAGE_BYTES:
        raise ValueError(f"{label} exceeds {MAX_MESSAGE_BYTES} bytes")
    return decoded


def load_sha256_vectors(source: Path | VerifiedArtifact) -> list[dict[str, str]]:
    if isinstance(source, VerifiedArtifact):
        raw_bundle = _parse_json(source.content, str(source.path))
    else:
        raw_bundle = _read_json(source)
    bundle = _require_schema_one(raw_bundle, "vector bundle")
    _require_exact_keys(
        bundle,
        {"schema_version", "algorithm", "source", "source_artifacts", "vectors"},
        "vector bundle",
    )
    if bundle["algorithm"] != "SHA-256":
        raise ValueError("vector bundle algorithm must equal SHA-256")
    source = bundle["source"]
    if not isinstance(source, dict):
        raise ValueError("vector bundle source must be an object")
    _require_exact_keys(
        source,
        {"publisher", "specification", "vector_page", "url", "retrieved", "scope"},
        "vector bundle source",
    )
    if not all(isinstance(item, str) and item.strip() for item in source.values()):
        raise ValueError("every vector bundle source field must be nonempty text")

    source_artifacts = bundle["source_artifacts"]
    if (
        not isinstance(source_artifacts, list)
        or not 1 <= len(source_artifacts) <= MAX_SOURCE_ARTIFACTS
    ):
        raise ValueError(
            f"source_artifacts must contain 1 through {MAX_SOURCE_ARTIFACTS} items"
        )
    source_ids: set[str] = set()
    source_keys = {"id", "title", "url", "sha256", "retrieved", "coordinates"}
    for index, artifact in enumerate(source_artifacts):
        if not isinstance(artifact, dict):
            raise ValueError(f"source artifact {index} must be an object")
        _require_exact_keys(artifact, source_keys, f"source artifact {index}")
        identifier = artifact["id"]
        if not isinstance(identifier, str) or not ID_RE.fullmatch(identifier):
            raise ValueError(f"source artifact {index} has invalid id")
        if identifier in source_ids:
            raise ValueError(f"duplicate source artifact id: {identifier}")
        source_ids.add(identifier)
        for field in ("title", "url", "retrieved", "coordinates"):
            if not isinstance(artifact[field], str) or not artifact[field].strip():
                raise ValueError(f"source artifact {identifier}.{field} must be nonempty text")
        if not isinstance(artifact["sha256"], str) or not HEX_64_RE.fullmatch(
            artifact["sha256"]
        ):
            raise ValueError(
                f"source artifact {identifier}.sha256 must be lowercase SHA-256 hex"
            )

    vectors = bundle["vectors"]
    if not isinstance(vectors, list) or not 1 <= len(vectors) <= MAX_VECTORS:
        raise ValueError(f"vectors must contain 1 through {MAX_VECTORS} items")
    identifiers: set[str] = set()
    validated: list[dict[str, str]] = []
    for index, vector in enumerate(vectors):
        if not isinstance(vector, dict):
            raise ValueError(f"vector {index} must be an object")
        _require_exact_keys(
            vector,
            {
                "id",
                "message_hex",
                "digest_hex",
                "source_artifact_id",
                "source_location",
            },
            f"vector {index}",
        )
        identifier = vector["id"]
        if not isinstance(identifier, str) or not ID_RE.fullmatch(identifier):
            raise ValueError(f"vector {index} has invalid id")
        if identifier in identifiers:
            raise ValueError(f"duplicate vector id: {identifier}")
        identifiers.add(identifier)
        source_identifier = vector["source_artifact_id"]
        if not isinstance(source_identifier, str) or source_identifier not in source_ids:
            raise ValueError(f"vector {identifier} references an unknown source artifact")
        if not isinstance(vector["source_location"], str) or not vector[
            "source_location"
        ].strip():
            raise ValueError(f"vector {identifier}.source_location must be nonempty text")
        _decode_hex(vector["message_hex"], f"vector {identifier}.message_hex")
        _decode_hex(vector["digest_hex"], f"vector {identifier}.digest_hex", digest=True)
        validated.append(vector)
    return validated


def run_sha256_vectors(vectors: list[dict[str, str]]) -> list[VectorResult]:
    results: list[VectorResult] = []
    for vector in vectors:
        message = bytes.fromhex(vector["message_hex"])
        actual = hashlib.sha256(message).hexdigest()
        results.append(
            VectorResult(vector["id"], actual == vector["digest_hex"], actual)
        )
    return results
