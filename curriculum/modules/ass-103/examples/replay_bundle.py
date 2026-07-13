#!/usr/bin/env python3
"""Bounded, deterministic offline replay-bundle teaching model for ASS-103."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import io
import json
from pathlib import Path, PurePosixPath, PureWindowsPath
import platform
import re
import sys
import tarfile
import tempfile
from typing import Iterable, Mapping


sys.dont_write_bytecode = True

SCHEMA = "ass-103-replay-v1"
RECIPE = "framed-concat-sha256-v1"
MAX_ARCHIVE_BYTES = 131_072
MAX_MANIFEST_BYTES = 16_384
MAX_MATERIALS = 16
MAX_MEMBER_BYTES = 4_096
MAX_TOTAL_MATERIAL_BYTES = 65_536
MAX_OUTPUT_BYTES = 66_560
MAX_PATH_BYTES = 80
MAX_TEXT_BYTES = 120
MAX_REFS = 16
MAX_DEPENDENCY_DEPTH = 8
MAX_SEQUENCE = 2_147_483_647
BLOCK = 512
USTAR_RECORD = 10_240
SHA256_RE = re.compile(r"^sha256:[0-9a-f]{64}$")
ID_RE = re.compile(r"^[a-z][a-z0-9-]{0,39}$")
PORTABLE_COMPONENT_RE = re.compile(r"^[a-z0-9](?:[a-z0-9._-]*[a-z0-9_-])?$")
WINDOWS_RESERVED_STEMS = frozenset(
    {"con", "prn", "aux", "nul"}
    | {f"com{index}" for index in range(1, 10)}
    | {f"lpt{index}" for index in range(1, 10)}
)


@dataclass(frozen=True)
class Diagnostic:
    code: str
    message: str


class ReplayError(ValueError):
    """A stable, fail-closed replay rejection."""

    def __init__(self, code: str, message: str) -> None:
        self.diagnostic = Diagnostic(code, message)
        super().__init__(f"{code}: {message}")


@dataclass(frozen=True)
class MaterialSource:
    identifier: str
    path: str
    data: bytes
    depends_on: tuple[str, ...]
    provenance_id: str


@dataclass(frozen=True)
class ProvenanceSource:
    identifier: str
    producer: str
    origin: str
    revision: str


@dataclass(frozen=True)
class TrustAnchor:
    """Trusted out-of-bundle selection state."""

    manifest_sha256: str
    subject: str
    minimum_sequence: int
    approved_provenance: tuple[tuple[str, str], ...]
    approved_tcb: tuple[tuple[str, str], ...]


@dataclass(frozen=True)
class ReplayResult:
    subject: str
    sequence: int
    manifest_sha256: str
    dependency_closure: tuple[str, ...]
    material_sha256: tuple[tuple[str, str], ...]
    output_size: int
    output_sha256: str
    observed_environment: tuple[tuple[str, str], ...]
    temporary_path: str
    temporary_removed: bool


@dataclass(frozen=True)
class _ArchiveEntry:
    name: str
    offset: int
    size: int


def _fail(code: str, message: str) -> None:
    raise ReplayError(code, message)


def _canonical_json(value: object) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    ).encode("ascii")


def _sha256(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def _plain_text(value: object, label: str) -> str:
    if not isinstance(value, str) or not value:
        _fail("M002", f"{label} must be nonempty ASCII text")
    try:
        encoded = value.encode("ascii")
    except UnicodeEncodeError:
        _fail("M002", f"{label} must be nonempty ASCII text")
    if len(encoded) > MAX_TEXT_BYTES or any(byte < 32 or byte > 126 for byte in encoded):
        _fail("M002", f"{label} exceeds the printable ASCII text envelope")
    return value


def _identifier(value: object, label: str) -> str:
    if not isinstance(value, str) or ID_RE.fullmatch(value) is None:
        _fail("M003", f"{label} is not a canonical identifier")
    return value


def _digest(value: object, label: str) -> str:
    if not isinstance(value, str) or SHA256_RE.fullmatch(value) is None:
        _fail("M004", f"{label} is not a sha256 content identity")
    return value


def _safe_path(value: object) -> str:
    if type(value) is not str or not value:
        _fail("P001", "bundle path must be nonempty")
    try:
        encoded = value.encode("ascii")
    except UnicodeEncodeError:
        _fail("P001", "bundle path must be ASCII")
    path = PurePosixPath(value)
    windows_path = PureWindowsPath(value)
    parts = value.split("/")
    if (
        len(encoded) > MAX_PATH_BYTES
        or value.startswith("/")
        or "\\" in value
        or bool(windows_path.drive)
        or bool(windows_path.root)
        or any(PORTABLE_COMPONENT_RE.fullmatch(part) is None for part in parts)
        or any(part.split(".", 1)[0] in WINDOWS_RESERVED_STEMS for part in parts)
        or str(path) != value
    ):
        _fail("P001", "bundle path is absolute, traversing, or noncanonical")
    return value


def _validate_material_paths(paths: Iterable[str]) -> None:
    checked = tuple(paths)
    reserved = ("manifest.json", "replay-output.bin")
    if any(
        path == name or path.startswith(name + "/")
        for path in checked
        for name in reserved
    ):
        _fail("P001", "material path uses a reserved replay name")
    for path in checked:
        if any(other != path and other.startswith(path + "/") for other in checked):
            _fail("P001", "material paths must be prefix-free")


def _unique_sorted_strings(value: object, label: str) -> tuple[str, ...]:
    if not isinstance(value, list) or len(value) > MAX_REFS:
        _fail("M005", f"{label} must be a bounded array")
    items = tuple(_identifier(item, label) for item in value)
    if tuple(sorted(set(items))) != items:
        _fail("M005", f"{label} must be sorted and unique")
    return items


def _pairs_without_duplicates(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            _fail("M001", f"JSON object has duplicate key {key!r}")
        result[key] = value
    return result


def _parse_manifest(raw: bytes) -> dict[str, object]:
    if len(raw) > MAX_MANIFEST_BYTES:
        _fail("B006", "manifest exceeds its byte limit")
    try:
        value = json.loads(raw.decode("ascii"), object_pairs_hook=_pairs_without_duplicates)
    except ReplayError:
        raise
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        _fail("M001", f"manifest is not canonical ASCII JSON: {error}")
    if not isinstance(value, dict):
        _fail("M001", "manifest is not one canonical JSON object")
    try:
        recoded = _canonical_json(value)
    except (TypeError, ValueError):
        _fail("M001", "manifest contains a value outside canonical JSON")
    if recoded != raw:
        _fail("M001", "manifest is not one canonical JSON object")
    return value


def _tar_field(field: bytes, label: str) -> bytes:
    head, separator, tail = field.partition(b"\0")
    if separator and any(tail):
        _fail("B002", f"archive {label} field has data after NUL")
    return head


def _tar_octal(field: bytes, label: str) -> int:
    stripped = field.rstrip(b"\0 ").lstrip(b" ")
    if not stripped or any(byte not in b"01234567" for byte in stripped):
        _fail("B002", f"archive {label} is not canonical octal")
    return int(stripped, 8)


def _scan_archive(data: bytes) -> tuple[_ArchiveEntry, ...]:
    """Validate every header before any material payload is sliced or retained."""

    if type(data) is not bytes:
        _fail("B001", "bundle must be immutable bytes")
    if len(data) > MAX_ARCHIVE_BYTES:
        _fail("B001", "bundle exceeds its byte limit")
    if len(data) < 3 * BLOCK or len(data) % BLOCK != 0:
        _fail("B002", "bundle is not an aligned uncompressed USTAR archive")

    entries: list[_ArchiveEntry] = []
    names: set[str] = set()
    declared_total = 0
    cursor = 0
    while cursor + BLOCK <= len(data):
        header = data[cursor : cursor + BLOCK]
        if header == bytes(BLOCK):
            if cursor + 2 * BLOCK > len(data) or any(data[cursor:]):
                _fail("B002", "archive lacks a canonical all-zero terminator")
            expected_archive_size = (
                (cursor + 2 * BLOCK + USTAR_RECORD - 1) // USTAR_RECORD
            ) * USTAR_RECORD
            if len(data) != expected_archive_size:
                _fail("B002", "archive has noncanonical end padding")
            break
        if header[257:263] != b"ustar\0" or header[263:265] != b"00":
            _fail("B002", "archive member is not POSIX USTAR")
        stored_checksum = _tar_octal(header[148:156], "checksum")
        checksum_header = header[:148] + b" " * 8 + header[156:]
        if sum(checksum_header) != stored_checksum:
            _fail("B002", "archive header checksum mismatch")
        if header[148:156] != f"{stored_checksum:06o}\0 ".encode("ascii"):
            _fail("B002", "archive checksum encoding is not canonical")
        type_flag = header[156:157]
        if type_flag != b"0":
            _fail("B003", "links, devices, directories, and special members are forbidden")
        if any(header[157:257]):
            _fail("B003", "regular archive member has a link target")
        if (
            header[100:108] != b"0000644\0"
            or header[108:116] != b"0000000\0"
            or header[116:124] != b"0000000\0"
            or header[136:148] != b"00000000000\0"
            or any(header[265:345])
            or any(header[500:512])
        ):
            _fail("B002", "archive member metadata is not canonical")
        name_raw = _tar_field(header[0:100], "name")
        prefix_raw = _tar_field(header[345:500], "prefix")
        if prefix_raw:
            _fail("B002", "canonical bounded paths must not use a USTAR prefix")
        try:
            name = name_raw.decode("ascii")
            prefix = prefix_raw.decode("ascii")
        except UnicodeDecodeError:
            _fail("P001", "archive path must be ASCII")
        combined = f"{prefix}/{name}" if prefix else name
        combined = _safe_path(combined)
        if header[0:100] != combined.encode("ascii") + bytes(100 - len(combined)):
            _fail("B002", "archive path field encoding is not canonical")
        if combined in names:
            _fail("B004", "archive contains a duplicate path")
        names.add(combined)
        size = _tar_octal(header[124:136], "size")
        if header[124:136] != f"{size:011o}\0".encode("ascii"):
            _fail("B002", "archive size encoding is not canonical")
        if size > max(MAX_MANIFEST_BYTES, MAX_MEMBER_BYTES):
            _fail("B005", "archive member exceeds every permitted member limit")
        declared_total += size
        if declared_total > MAX_MANIFEST_BYTES + MAX_TOTAL_MATERIAL_BYTES:
            _fail("B005", "archive declared payload exceeds the total byte limit")
        data_offset = cursor + BLOCK
        padded_size = ((size + BLOCK - 1) // BLOCK) * BLOCK
        if data_offset + padded_size > len(data):
            _fail("B002", "archive member extends beyond the bundle")
        if any(data[data_offset + size : data_offset + padded_size]):
            _fail("B002", "archive member padding is not canonical zero padding")
        entries.append(_ArchiveEntry(combined, data_offset, size))
        if len(entries) > MAX_MATERIALS + 1:
            _fail("B005", "archive has too many members")
        cursor = data_offset + padded_size
    else:
        _fail("B002", "archive has no zero terminator")

    ordered = tuple(entry.name for entry in entries)
    if not ordered or ordered[0] != "manifest.json" or ordered[1:] != tuple(sorted(ordered[1:])):
        _fail("B007", "archive order must be manifest first then paths sorted")
    if entries[0].size > MAX_MANIFEST_BYTES:
        _fail("B006", "manifest exceeds its byte limit")
    if any(entry.size > MAX_MEMBER_BYTES for entry in entries[1:]):
        _fail("B005", "material member exceeds its byte limit")
    if sum(entry.size for entry in entries[1:]) > MAX_TOTAL_MATERIAL_BYTES:
        _fail("B005", "material payload exceeds the total byte limit")
    return tuple(entries)


def current_environment() -> tuple[tuple[str, str], ...]:
    return (
        ("implementation", platform.python_implementation()),
        ("python", platform.python_version()),
        ("recipe-engine", "ass-103-builtin-v1"),
    )


def current_tcb() -> tuple[dict[str, str], ...]:
    model_bytes = Path(__file__).read_bytes()
    runtime_record = dict(current_environment())
    return (
        {
            "id": "python-runtime",
            "role": "executes the bounded replay model",
            "version": platform.python_version(),
            "identity": _sha256(_canonical_json(runtime_record)),
        },
        {
            "id": "replay-model",
            "role": "parses, verifies, closes, and replays the bundle",
            "version": SCHEMA,
            "identity": _sha256(model_bytes),
        },
    )


def _provenance_identity(record: Mapping[str, object]) -> str:
    body = {key: value for key, value in record.items() if key != "identity"}
    return _sha256(_canonical_json(body))


def _framed_output(materials: Iterable[tuple[str, bytes]]) -> bytes:
    result = bytearray(b"ASS103\0")
    for identifier, payload in materials:
        name = identifier.encode("ascii")
        result.extend(len(name).to_bytes(1, "big"))
        result.extend(name)
        result.extend(len(payload).to_bytes(4, "big"))
        result.extend(payload)
    if len(result) > MAX_OUTPUT_BYTES:
        _fail("R003", "replay output exceeds its byte limit")
    return bytes(result)


def build_manifest(
    *,
    subject: str,
    sequence: int,
    materials: tuple[MaterialSource, ...],
    provenance: tuple[ProvenanceSource, ...],
    roots: tuple[str, ...],
) -> bytes:
    """Build a canonical manifest in memory; this function performs no I/O."""

    _plain_text(subject, "subject")
    if type(sequence) is not int or not 0 <= sequence <= MAX_SEQUENCE:
        _fail("M006", "sequence is outside the unsigned teaching envelope")
    if not 1 <= len(materials) <= MAX_MATERIALS:
        _fail("M007", "material count is outside 1 through 16")
    material_ids = tuple(item.identifier for item in materials)
    if tuple(sorted(set(material_ids))) != material_ids:
        _fail("M007", "material inputs must be sorted by unique identifier")
    provenance_ids = tuple(item.identifier for item in provenance)
    if (
        not provenance_ids
        or len(provenance_ids) > MAX_MATERIALS
        or tuple(sorted(set(provenance_ids))) != provenance_ids
    ):
        _fail("M008", "provenance inputs must be sorted and unique")

    material_records: list[dict[str, object]] = []
    data_by_id: dict[str, bytes] = {}
    for item in materials:
        identifier = _identifier(item.identifier, "material id")
        path = _safe_path(item.path)
        if type(item.data) is not bytes or len(item.data) > MAX_MEMBER_BYTES:
            _fail("M007", "material payload must be immutable bounded bytes")
        if tuple(sorted(set(item.depends_on))) != item.depends_on or len(item.depends_on) > MAX_REFS:
            _fail("M005", "material dependencies must be sorted and unique")
        for dependency in item.depends_on:
            _identifier(dependency, "dependency id")
        provenance_id = _identifier(item.provenance_id, "provenance id")
        data_by_id[identifier] = item.data
        material_records.append(
            {
                "depends_on": list(item.depends_on),
                "id": identifier,
                "path": path,
                "provenance_id": provenance_id,
                "sha256": _sha256(item.data),
                "size": len(item.data),
            }
        )
    if len({record["path"] for record in material_records}) != len(material_records):
        _fail("M007", "material paths must be unique")
    _validate_material_paths(str(record["path"]) for record in material_records)
    if sum(len(item.data) for item in materials) > MAX_TOTAL_MATERIAL_BYTES:
        _fail("M007", "total material bytes exceed the limit")

    provenance_records: list[dict[str, object]] = []
    for source in provenance:
        identifier = _identifier(source.identifier, "provenance id")
        governed = sorted(
            record["id"] for record in material_records if record["provenance_id"] == identifier
        )
        if not governed:
            _fail("M008", "every provenance record must govern a material")
        record: dict[str, object] = {
            "id": identifier,
            "materials": governed,
            "origin": _plain_text(source.origin, "provenance origin"),
            "producer": _plain_text(source.producer, "provenance producer"),
            "revision": _plain_text(source.revision, "provenance revision"),
        }
        record["identity"] = _provenance_identity(record)
        provenance_records.append(record)

    root_list = list(roots)
    if tuple(sorted(set(root_list))) != roots or not roots or len(roots) > MAX_REFS:
        _fail("M005", "recipe roots must be sorted, unique, and nonempty")
    for root in roots:
        _identifier(root, "recipe root")

    manifest: dict[str, object] = {
        "environment": {
            "network": "forbidden",
            "python": ">=3.11,<4",
            "recipe_engine": "ass-103-builtin-v1",
        },
        "expected": {"sha256": "", "size": 0},
        "materials": material_records,
        "provenance": provenance_records,
        "recipe": {"kind": RECIPE, "roots": root_list},
        "schema": SCHEMA,
        "sequence": sequence,
        "subject": subject,
        "tcb": list(current_tcb()),
    }
    # Validation computes the closure. Use it here so the expected result and replay
    # share the specified ordering but not stored output bytes.
    closure = _dependency_closure(material_records, roots)
    if set(closure) != set(material_ids):
        _fail("D004", "every declared material must belong to the root closure")
    output = _framed_output((identifier, data_by_id[identifier]) for identifier in closure)
    manifest["expected"] = {"sha256": _sha256(output), "size": len(output)}
    raw = _canonical_json(manifest)
    if len(raw) > MAX_MANIFEST_BYTES:
        _fail("M001", "canonical manifest exceeds its byte limit")
    return raw


def build_bundle(manifest: bytes, materials: tuple[MaterialSource, ...]) -> bytes:
    """Create deterministic USTAR bytes in memory; callers choose any persistence."""

    parsed = _parse_manifest(manifest)
    manifest_records = parsed.get("materials")
    if not isinstance(manifest_records, list):
        _fail("M007", "manifest materials must be an array")
    source_by_path = {item.path: item.data for item in materials}
    expected_paths = [record.get("path") for record in manifest_records if isinstance(record, dict)]
    if (
        len(expected_paths) != len(manifest_records)
        or len(source_by_path) != len(materials)
        or len(materials) != len(expected_paths)
        or set(source_by_path) != set(expected_paths)
    ):
        _fail("M009", "bundle sources do not exactly match manifest paths")
    output = io.BytesIO()
    with tarfile.open(fileobj=output, mode="w", format=tarfile.USTAR_FORMAT) as archive:
        for path, payload in (("manifest.json", manifest),) + tuple(
            (path, source_by_path[path]) for path in sorted(source_by_path)
        ):
            info = tarfile.TarInfo(path)
            info.size = len(payload)
            info.mode = 0o644
            info.uid = info.gid = info.mtime = 0
            info.uname = info.gname = ""
            archive.addfile(info, io.BytesIO(payload))
    result = output.getvalue()
    _scan_archive(result)
    return result


def make_anchor(manifest: bytes, *, minimum_sequence: int | None = None) -> TrustAnchor:
    """Model a trust decision made through a channel outside the bundle."""

    value = _parse_manifest(manifest)
    subject = value.get("subject")
    sequence = value.get("sequence")
    if not isinstance(subject, str) or type(sequence) is not int:
        _fail("M001", "cannot anchor an incomplete manifest")
    provenance = value.get("provenance")
    tcb = value.get("tcb")
    if not isinstance(provenance, list) or not isinstance(tcb, list):
        _fail("M001", "cannot anchor an incomplete manifest")
    provenance_pairs = tuple(
        sorted((str(item.get("id")), str(item.get("identity"))) for item in provenance if isinstance(item, dict))
    )
    tcb_pairs = tuple(
        sorted((str(item.get("id")), str(item.get("identity"))) for item in tcb if isinstance(item, dict))
    )
    floor = sequence if minimum_sequence is None else minimum_sequence
    if type(floor) is not int or not 0 <= floor <= MAX_SEQUENCE:
        _fail("A004", "anchor sequence floor is invalid")
    return TrustAnchor(_sha256(manifest), subject, floor, provenance_pairs, tcb_pairs)


def _validate_anchor(anchor: TrustAnchor) -> None:
    if type(anchor) is not TrustAnchor:
        _fail("A004", "trust anchor has the wrong record type")
    if type(anchor.manifest_sha256) is not str or SHA256_RE.fullmatch(anchor.manifest_sha256) is None:
        _fail("A004", "trust anchor manifest identity is invalid")
    if type(anchor.subject) is not str:
        _fail("A004", "trust anchor subject is invalid")
    try:
        subject_bytes = anchor.subject.encode("ascii")
    except UnicodeEncodeError:
        _fail("A004", "trust anchor subject is invalid")
    if not subject_bytes or len(subject_bytes) > MAX_TEXT_BYTES:
        _fail("A004", "trust anchor subject is invalid")
    if type(anchor.minimum_sequence) is not int or not 0 <= anchor.minimum_sequence <= MAX_SEQUENCE:
        _fail("A004", "trust anchor sequence floor is invalid")
    for label, pairs, maximum in (
        ("provenance", anchor.approved_provenance, MAX_MATERIALS),
        ("TCB", anchor.approved_tcb, MAX_REFS),
    ):
        if type(pairs) is not tuple or not 1 <= len(pairs) <= maximum:
            _fail("A004", f"trust anchor {label} approvals are invalid")
        checked: list[tuple[str, str]] = []
        for pair in pairs:
            if type(pair) is not tuple or len(pair) != 2:
                _fail("A004", f"trust anchor {label} approval is invalid")
            identifier, identity = pair
            if type(identifier) is not str or ID_RE.fullmatch(identifier) is None:
                _fail("A004", f"trust anchor {label} id is invalid")
            if type(identity) is not str or SHA256_RE.fullmatch(identity) is None:
                _fail("A004", f"trust anchor {label} identity is invalid")
            checked.append((identifier, identity))
        if tuple(sorted(set(checked))) != pairs:
            _fail("A004", f"trust anchor {label} approvals must be sorted and unique")


def _dependency_closure(
    records: list[dict[str, object]], roots: Iterable[str]
) -> tuple[str, ...]:
    by_id = {record.get("id"): record for record in records}
    closure: set[str] = set()
    active: set[str] = set()

    def visit(identifier: str, depth: int) -> None:
        if depth > MAX_DEPENDENCY_DEPTH:
            _fail("D003", "dependency closure exceeds eight edges")
        if identifier in active:
            _fail("D002", "dependency graph contains a cycle")
        if identifier in closure:
            return
        record = by_id.get(identifier)
        if record is None:
            _fail("D001", "dependency closure references an unknown material")
        dependencies = record.get("depends_on")
        if not isinstance(dependencies, list):
            _fail("M007", "material dependencies must be an array")
        active.add(identifier)
        for dependency in dependencies:
            if not isinstance(dependency, str):
                _fail("M007", "dependency identifier must be text")
            visit(dependency, depth + 1)
        active.remove(identifier)
        closure.add(identifier)

    for root in roots:
        visit(root, 0)
    return tuple(sorted(closure))


def _validate_manifest(value: dict[str, object], anchor: TrustAnchor) -> tuple[
    list[dict[str, object]], tuple[str, ...], dict[str, object]
]:
    expected_keys = {
        "environment", "expected", "materials", "provenance", "recipe",
        "schema", "sequence", "subject", "tcb",
    }
    if set(value) != expected_keys or value.get("schema") != SCHEMA:
        _fail("M001", "manifest schema or top-level fields are invalid")
    subject = _plain_text(value.get("subject"), "subject")
    sequence = value.get("sequence")
    if type(sequence) is not int or not 0 <= sequence <= MAX_SEQUENCE:
        _fail("M006", "sequence is outside the unsigned teaching envelope")
    if subject != anchor.subject:
        _fail("A002", "trusted subject does not match the manifest")
    if sequence < anchor.minimum_sequence:
        _fail("A003", "manifest sequence is below the trusted rollback floor")
    environment = value.get("environment")
    if environment != {
        "network": "forbidden", "python": ">=3.11,<4", "recipe_engine": "ass-103-builtin-v1"
    }:
        _fail("E001", "environment profile is unsupported")
    if not (sys.version_info >= (3, 11) and sys.version_info < (4, 0)):
        _fail("E002", "host Python is outside the manifest profile")

    materials_value = value.get("materials")
    if not isinstance(materials_value, list) or not 1 <= len(materials_value) <= MAX_MATERIALS:
        _fail("M007", "material count is outside 1 through 16")
    materials: list[dict[str, object]] = []
    ids: list[str] = []
    paths: list[str] = []
    total = 0
    for item in materials_value:
        if not isinstance(item, dict) or set(item) != {
            "depends_on", "id", "path", "provenance_id", "sha256", "size"
        }:
            _fail("M007", "material record fields are invalid")
        identifier = _identifier(item.get("id"), "material id")
        path = _safe_path(item.get("path"))
        size = item.get("size")
        if type(size) is not int or not 0 <= size <= MAX_MEMBER_BYTES:
            _fail("M007", "material size is outside the member limit")
        _digest(item.get("sha256"), "material digest")
        _identifier(item.get("provenance_id"), "provenance id")
        dependencies = _unique_sorted_strings(item.get("depends_on"), "material dependencies")
        item["depends_on"] = list(dependencies)
        ids.append(identifier)
        paths.append(path)
        total += size
        materials.append(item)
    if ids != sorted(set(ids)) or len(paths) != len(set(paths)):
        _fail("M007", "material ids must be sorted and paths unique")
    _validate_material_paths(paths)
    if total > MAX_TOTAL_MATERIAL_BYTES:
        _fail("M007", "total declared material bytes exceed the limit")

    recipe = value.get("recipe")
    if not isinstance(recipe, dict) or set(recipe) != {"kind", "roots"} or recipe.get("kind") != RECIPE:
        _fail("R001", "recipe is not the supported built-in deterministic recipe")
    roots = _unique_sorted_strings(recipe.get("roots"), "recipe roots")
    if not roots:
        _fail("R001", "recipe must have at least one root")
    closure = _dependency_closure(materials, roots)
    if set(closure) != set(ids):
        _fail("D004", "declared material is outside the selected dependency closure")

    provenance_value = value.get("provenance")
    if (
        not isinstance(provenance_value, list)
        or not 1 <= len(provenance_value) <= MAX_MATERIALS
    ):
        _fail("V001", "provenance inventory must be nonempty")
    provenance_pairs: list[tuple[str, str]] = []
    provenance_ids: list[str] = []
    for item in provenance_value:
        if not isinstance(item, dict) or set(item) != {
            "id", "identity", "materials", "origin", "producer", "revision"
        }:
            _fail("V001", "provenance record fields are invalid")
        identifier = _identifier(item.get("id"), "provenance id")
        identity = _digest(item.get("identity"), "provenance identity")
        _plain_text(item.get("origin"), "provenance origin")
        _plain_text(item.get("producer"), "provenance producer")
        _plain_text(item.get("revision"), "provenance revision")
        governed = _unique_sorted_strings(item.get("materials"), "provenance materials")
        actual = tuple(record["id"] for record in materials if record["provenance_id"] == identifier)
        if not governed or governed != actual:
            _fail("V002", "provenance inventory omits or substitutes a governed material")
        if _provenance_identity(item) != identity:
            _fail("V003", "provenance content identity mismatch")
        provenance_ids.append(identifier)
        provenance_pairs.append((identifier, identity))
    if provenance_ids != sorted(set(provenance_ids)):
        _fail("V001", "provenance records must be sorted and unique")
    if any(record["provenance_id"] not in set(provenance_ids) for record in materials):
        _fail("V002", "material references missing provenance")
    if tuple(provenance_pairs) != anchor.approved_provenance:
        _fail("A005", "provenance identities are not approved by the trust anchor")

    tcb_value = value.get("tcb")
    if not isinstance(tcb_value, list) or not 1 <= len(tcb_value) <= MAX_REFS:
        _fail("T001", "TCB inventory must be nonempty")
    tcb_pairs: list[tuple[str, str]] = []
    tcb_ids: list[str] = []
    for item in tcb_value:
        if not isinstance(item, dict) or set(item) != {"id", "identity", "role", "version"}:
            _fail("T001", "TCB record fields are invalid")
        identifier = _identifier(item.get("id"), "TCB id")
        identity = _digest(item.get("identity"), "TCB identity")
        _plain_text(item.get("role"), "TCB role")
        _plain_text(item.get("version"), "TCB version")
        tcb_ids.append(identifier)
        tcb_pairs.append((identifier, identity))
    if tcb_ids != sorted(set(tcb_ids)):
        _fail("T001", "TCB records must be sorted and unique")
    if tuple(tcb_pairs) != anchor.approved_tcb:
        _fail("A006", "TCB identities are not approved by the trust anchor")
    observed_pairs = tuple(sorted((item["id"], item["identity"]) for item in current_tcb()))
    if tuple(tcb_pairs) != observed_pairs:
        _fail("T002", "observed replay TCB differs from the manifest")

    expected = value.get("expected")
    if not isinstance(expected, dict) or set(expected) != {"sha256", "size"}:
        _fail("R002", "expected output record is invalid")
    _digest(expected.get("sha256"), "expected output digest")
    expected_size = expected.get("size")
    if type(expected_size) is not int or not 0 <= expected_size <= MAX_OUTPUT_BYTES:
        _fail("R002", "expected output size is invalid")
    return materials, closure, expected


def replay_bundle(bundle: bytes, anchor: TrustAnchor) -> ReplayResult:
    """Replay one anchored bundle offline inside a fresh temporary directory."""

    _validate_anchor(anchor)
    entries = _scan_archive(bundle)
    manifest_entry = entries[0]
    manifest_raw = bundle[
        manifest_entry.offset : manifest_entry.offset + manifest_entry.size
    ]
    manifest = _parse_manifest(manifest_raw)
    manifest_identity = _sha256(manifest_raw)
    if manifest_identity != anchor.manifest_sha256:
        _fail("A001", "manifest content identity does not match the trust anchor")
    materials, closure, expected = _validate_manifest(manifest, anchor)
    entries_by_name = {entry.name: entry for entry in entries[1:]}
    expected_paths = {str(record["path"]) for record in materials}
    if set(entries_by_name) != expected_paths:
        _fail("B008", "archive omits or adds a manifest material")

    retained: dict[str, bytes] = {}
    digests: list[tuple[str, str]] = []
    for record in materials:
        entry = entries_by_name[str(record["path"])]
        payload = bundle[entry.offset : entry.offset + entry.size]
        if entry.size != record["size"] or _sha256(payload) != record["sha256"]:
            _fail("B009", "material size or content identity mismatch")
        retained[str(record["id"])] = payload
        digests.append((str(record["id"]), str(record["sha256"])))

    temporary_value = ""
    with tempfile.TemporaryDirectory(prefix="ass-103-replay-") as temporary_name:
        temporary_value = temporary_name
        temporary = Path(temporary_name)
        for record in materials:
            target = temporary / str(record["path"])
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(retained[str(record["id"])])
        output = _framed_output((identifier, retained[identifier]) for identifier in closure)
        output_path = temporary / "replay-output.bin"
        output_path.write_bytes(output)
        observed = output_path.read_bytes()
        if len(observed) != expected["size"] or _sha256(observed) != expected["sha256"]:
            _fail("R002", "deterministic replay output differs from the manifest")
    removed = not Path(temporary_value).exists()
    if not removed:
        _fail("R004", "temporary replay workspace was not removed")
    return ReplayResult(
        str(manifest["subject"]),
        int(manifest["sequence"]),
        manifest_identity,
        closure,
        tuple(digests),
        int(expected["size"]),
        str(expected["sha256"]),
        current_environment(),
        temporary_value,
        removed,
    )
