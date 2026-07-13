#!/usr/bin/env python3
"""Smoke-check the bounded ASS-103 offline replay model."""

from __future__ import annotations

from dataclasses import replace
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tarfile
import tempfile


sys.dont_write_bytecode = True
MODULE_ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = MODULE_ROOT / "examples"
sys.path.insert(0, str(EXAMPLES))

from replay_bundle import (  # noqa: E402
    MAX_ARCHIVE_BYTES,
    MAX_DEPENDENCY_DEPTH,
    MAX_MATERIALS,
    MAX_MEMBER_BYTES,
    MAX_PATH_BYTES,
    MAX_SEQUENCE,
    MAX_TOTAL_MATERIAL_BYTES,
    MaterialSource,
    ProvenanceSource,
    ReplayError,
    TrustAnchor,
    build_bundle,
    build_manifest,
    make_anchor,
    replay_bundle,
)
from replay_worked import example_materials, make_example  # noqa: E402


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def expect_error(code: str, action, message: str) -> ReplayError:
    try:
        action()
    except ReplayError as error:
        require(error.diagnostic.code == code, f"{message}: got {error.diagnostic!r}")
        return error
    raise AssertionError(message)


def canonical(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("ascii")


def changed_manifest(raw: bytes, change) -> bytes:
    value = json.loads(raw)
    change(value)
    return canonical(value)


def raw_tar(members: tuple[tuple[str, bytes, str, str], ...]) -> bytes:
    """Create an in-memory hostile archive. tuple is name, bytes, type, linkname."""
    output = io.BytesIO()
    with tarfile.open(fileobj=output, mode="w", format=tarfile.USTAR_FORMAT) as archive:
        for name, payload, kind, linkname in members:
            info = tarfile.TarInfo(name)
            info.type = kind.encode("ascii")
            info.linkname = linkname
            info.size = len(payload) if kind == "0" else 0
            info.mode = 0o644
            info.uid = info.gid = info.mtime = 0
            info.uname = info.gname = ""
            archive.addfile(info, io.BytesIO(payload) if kind == "0" else None)
    return output.getvalue()


def changed_header(bundle: bytes, start: int, replacement: bytes) -> bytes:
    changed = bytearray(bundle)
    changed[start : start + len(replacement)] = replacement
    changed[148:156] = b" " * 8
    checksum = sum(changed[:512])
    changed[148:156] = f"{checksum:06o}\0 ".encode("ascii")
    return bytes(changed)


def manifest_and_bundle(materials: tuple[MaterialSource, ...], roots: tuple[str, ...]):
    manifest = build_manifest(
        subject="endpoint-replay",
        sequence=MAX_SEQUENCE,
        materials=materials,
        provenance=(ProvenanceSource("endpoint-source", "endpoint producer", "local:endpoint", "v1"),),
        roots=roots,
    )
    return manifest, build_bundle(manifest, materials)


def check_normal_replay_and_determinism() -> None:
    manifest, bundle = make_example()
    anchor = make_anchor(manifest)
    first = replay_bundle(bundle, anchor)
    second_manifest, second_bundle = make_example()
    second = replay_bundle(second_bundle, make_anchor(second_manifest))
    require(manifest == second_manifest, "canonical manifests are not deterministic")
    require(bundle == second_bundle, "canonical bundles are not deterministic")
    require(first.subject == "quartz-record-demo" and first.sequence == 7, "selection changed")
    require(first.dependency_closure == ("format-spec", "sample-data"), "closure changed")
    require(first.manifest_sha256 == anchor.manifest_sha256, "manifest identity changed")
    require(first.output_sha256 == second.output_sha256, "replay output is nondeterministic")
    require(first.output_size == second.output_size == 90, "framed output size changed")
    require(first.temporary_removed and second.temporary_removed, "temporary workspace survived")
    require(not Path(first.temporary_path).exists(), "reported replay path still exists")


def check_resource_endpoints() -> None:
    materials = tuple(
        MaterialSource(
            f"material-{index:02d}",
            f"materials/item-{index:02d}.bin",
            bytes([index]) * MAX_MEMBER_BYTES,
            (),
            "endpoint-source",
        )
        for index in range(MAX_MATERIALS)
    )
    manifest, bundle = manifest_and_bundle(materials, tuple(item.identifier for item in materials))
    result = replay_bundle(bundle, make_anchor(manifest))
    require(len(result.material_sha256) == MAX_MATERIALS, "16-material endpoint failed")
    require(sum(len(item.data) for item in materials) == MAX_TOTAL_MATERIAL_BYTES,
            "65,536-byte total endpoint changed")
    require(len(bundle) <= MAX_ARCHIVE_BYTES, "valid endpoint exceeds archive cap")

    expect_error(
        "M007",
        lambda: manifest_and_bundle(
            materials + (
                MaterialSource("material-16", "materials/item-16.bin", b"x", (), "endpoint-source"),
            ),
            tuple(item.identifier for item in materials) + ("material-16",),
        ),
        "17-material overflow passed",
    )
    expect_error(
        "M007",
        lambda: manifest_and_bundle(
            (MaterialSource("large", "materials/large.bin", b"x" * (MAX_MEMBER_BYTES + 1), (), "endpoint-source"),),
            ("large",),
        ),
        "4,097-byte material passed",
    )
    path_endpoint = "materials/" + "p" * (MAX_PATH_BYTES - len("materials/"))
    path_material = (MaterialSource("path", path_endpoint, b"x", (), "endpoint-source"),)
    path_manifest, path_bundle = manifest_and_bundle(path_material, ("path",))
    require(replay_bundle(path_bundle, make_anchor(path_manifest)).subject == "endpoint-replay",
            "80-byte path endpoint failed")
    expect_error(
        "P001",
        lambda: manifest_and_bundle(
            (MaterialSource("path", path_endpoint + "x", b"x", (), "endpoint-source"),),
            ("path",),
        ),
        "81-byte path passed",
    )
    expect_error(
        "B001",
        lambda: replay_bundle(b"x" * (MAX_ARCHIVE_BYTES + 1), make_anchor(manifest)),
        "archive byte one-beyond passed",
    )

    def chain(edge_count: int) -> tuple[MaterialSource, ...]:
        return tuple(
            MaterialSource(
                f"node-{index:02d}",
                f"materials/node-{index:02d}",
                bytes([index]),
                () if index == 0 else (f"node-{index - 1:02d}",),
                "endpoint-source",
            )
            for index in range(edge_count + 1)
        )

    endpoint_chain = chain(MAX_DEPENDENCY_DEPTH)
    chain_manifest, chain_bundle = manifest_and_bundle(endpoint_chain, ("node-08",))
    require(len(replay_bundle(chain_bundle, make_anchor(chain_manifest)).dependency_closure) == 9,
            "dependency depth-8 endpoint failed")
    expect_error(
        "D003",
        lambda: manifest_and_bundle(chain(MAX_DEPENDENCY_DEPTH + 1), ("node-09",)),
        "dependency depth-9 overflow passed",
    )


def check_hostile_archives_before_retention() -> None:
    manifest, bundle = make_example()
    anchor = make_anchor(manifest)
    format_payload = example_materials()[0].data
    sample_payload = example_materials()[1].data
    base = (("manifest.json", manifest, "0", ""),)

    expect_error(
        "B003",
        lambda: replay_bundle(raw_tar(base + (("materials/format.txt", b"", "2", "target"),)), anchor),
        "symlink member passed",
    )
    expect_error(
        "P001",
        lambda: replay_bundle(raw_tar(base + (("../escape", b"x", "0", ""),)), anchor),
        "traversal member passed",
    )
    for unsafe in (
        "line\nbreak",
        "C:/escape",
        "materials/A",
        "materials/nul.txt",
        "materials/trailing.",
        "replay-output.bin",
        "replay-output.bin/child",
        "manifest.json/child",
    ):
        expect_error(
            "P001",
            lambda unsafe=unsafe: manifest_and_bundle(
                (MaterialSource("unsafe", unsafe, b"x", (), "endpoint-source"),),
                ("unsafe",),
            ),
            f"unsafe material path {unsafe!r} passed",
        )
    expect_error(
        "P001",
        lambda: manifest_and_bundle(
            (
                MaterialSource("leaf", "tree/leaf", b"x", (), "endpoint-source"),
                MaterialSource("tree", "tree", b"x", (), "endpoint-source"),
            ),
            ("leaf", "tree"),
        ),
        "prefix-conflicting material paths passed",
    )
    expect_error(
        "B004",
        lambda: replay_bundle(
            raw_tar(base + (
                ("materials/format.txt", format_payload, "0", ""),
                ("materials/format.txt", format_payload, "0", ""),
            )),
            anchor,
        ),
        "duplicate path passed",
    )
    expect_error(
        "B005",
        lambda: replay_bundle(raw_tar(base + (("oversize.bin", b"x" * (MAX_MEMBER_BYTES + 1), "0", ""),)), anchor),
        "oversize member passed",
    )
    noncanonical_mode = changed_header(bundle, 100, b"0000600\0")
    expect_error(
        "B002", lambda: replay_bundle(noncanonical_mode, anchor),
        "noncanonical archive metadata passed",
    )
    manifest_size = int(bundle[124:136].rstrip(b"\0 "), 8)
    nonzero_padding = bytearray(bundle)
    nonzero_padding[512 + manifest_size] = 1
    expect_error(
        "B002", lambda: replay_bundle(bytes(nonzero_padding), anchor),
        "nonzero archive padding passed",
    )
    expect_error(
        "B008",
        lambda: replay_bundle(
            raw_tar(base + (("materials/format.txt", format_payload, "0", ""),)), anchor
        ),
        "omitted material passed",
    )
    expect_error(
        "B008",
        lambda: replay_bundle(
            raw_tar(base + (
                ("materials/format.txt", format_payload, "0", ""),
                ("materials/sample.txt", sample_payload, "0", ""),
                ("materials/unlisted.txt", b"x", "0", ""),
            )),
            anchor,
        ),
        "undeclared archive member passed",
    )

    substituted = bundle.replace(b"alpha=17", b"alpha=18")
    require(substituted != bundle and len(substituted) == len(bundle), "substitution fixture failed")
    expect_error("B009", lambda: replay_bundle(substituted, anchor), "payload substitution passed")


def check_anchor_closure_and_comparison_failures() -> None:
    manifest, bundle = make_example()
    anchor = make_anchor(manifest)

    class ForgedAnchor(TrustAnchor):
        pass

    class ForgedText(str):
        pass

    expect_error(
        "A004",
        lambda: replay_bundle(
            bundle,
            ForgedAnchor(
                anchor.manifest_sha256,
                anchor.subject,
                anchor.minimum_sequence,
                anchor.approved_provenance,
                anchor.approved_tcb,
            ),
        ),
        "trust-anchor subclass passed",
    )
    expect_error(
        "A004",
        lambda: replay_bundle(
            bundle, replace(anchor, manifest_sha256=ForgedText(anchor.manifest_sha256))
        ),
        "trust-anchor string subclass passed",
    )
    changed_sequence = changed_manifest(manifest, lambda value: value.__setitem__("sequence", 8))
    changed_bundle = build_bundle(changed_sequence, example_materials())
    expect_error("A001", lambda: replay_bundle(changed_bundle, anchor), "manifest substitution passed")

    old_manifest, old_bundle = make_example(sequence=6)
    expect_error(
        "A003",
        lambda: replay_bundle(old_bundle, make_anchor(old_manifest, minimum_sequence=7)),
        "rollback below trusted sequence passed",
    )

    def unknown_dependency(value: dict[str, object]) -> None:
        value["materials"][1]["depends_on"] = ["missing"]

    unknown = changed_manifest(manifest, unknown_dependency)
    expect_error(
        "D001",
        lambda: replay_bundle(build_bundle(unknown, example_materials()), make_anchor(unknown)),
        "unknown dependency passed",
    )

    def cycle(value: dict[str, object]) -> None:
        value["materials"][0]["depends_on"] = ["sample-data"]

    cyclic = changed_manifest(manifest, cycle)
    expect_error(
        "D002",
        lambda: replay_bundle(build_bundle(cyclic, example_materials()), make_anchor(cyclic)),
        "dependency cycle passed",
    )

    def wrong_expected(value: dict[str, object]) -> None:
        value["expected"]["sha256"] = "sha256:" + "0" * 64

    wrong = changed_manifest(manifest, wrong_expected)
    expect_error(
        "R002",
        lambda: replay_bundle(build_bundle(wrong, example_materials()), make_anchor(wrong)),
        "wrong replay digest passed",
    )

    def changed_provenance(value: dict[str, object]) -> None:
        record = value["provenance"][0]
        record["origin"] = "local:substituted-origin"
        body = {key: item for key, item in record.items() if key != "identity"}
        import hashlib
        record["identity"] = "sha256:" + hashlib.sha256(canonical(body)).hexdigest()

    provenance_manifest = changed_manifest(manifest, changed_provenance)
    provenance_anchor = replace(make_anchor(provenance_manifest), approved_provenance=anchor.approved_provenance)
    expect_error(
        "A005",
        lambda: replay_bundle(build_bundle(provenance_manifest, example_materials()), provenance_anchor),
        "unapproved provenance substitution passed",
    )


def check_worked_and_deliberate_failure() -> None:
    environment = dict(os.environ)
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    with tempfile.TemporaryDirectory(prefix="ass-103-smoke-") as temporary_name:
        temporary = Path(temporary_name)
        worked = subprocess.run(
            [sys.executable, "-B", str(EXAMPLES / "replay_worked.py")],
            cwd=temporary,
            env=environment,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=8,
            check=False,
        )
        require(worked.returncode == 0, f"worked example failed: {worked.stderr}")
        require(worked.stderr == "", "worked example wrote stderr")
        require("subject: quartz-record-demo\n" in worked.stdout, "worked subject changed")
        require("closure: format-spec,sample-data\n" in worked.stdout, "worked closure changed")
        require("workspace-removed: true\n" in worked.stdout, "worked cleanup changed")

        mutation = temporary / "mutation.py"
        common = (
            f"import sys\nsys.path.insert(0, {str(EXAMPLES)!r})\n"
            "from replay_bundle import make_anchor, replay_bundle\n"
            "from replay_worked import make_example\n"
            "manifest, bundle = make_example()\n"
            "result = replay_bundle(bundle, make_anchor(manifest))\n"
        )
        mutation.write_text(common + "assert result.output_size == 89, 'intentionally wrong size'\n", encoding="utf-8")
        failed = subprocess.run(
            [sys.executable, "-B", str(mutation)], cwd=temporary, env=environment,
            text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=8, check=False,
        )
        require(failed.returncode != 0, "deliberately wrong replay expectation passed")
        require(failed.stdout == "" and "AssertionError" in failed.stderr,
                "deliberate replay failure was not observable")
        mutation.write_text(common + "assert result.output_size == 90\nprint('deliberate recovery: PASS')\n", encoding="utf-8")
        restored = subprocess.run(
            [sys.executable, "-B", str(mutation)], cwd=temporary, env=environment,
            text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=8, check=False,
        )
        require(restored.returncode == 0, f"restored replay failed: {restored.stderr}")
        require(restored.stdout == "deliberate recovery: PASS\n" and restored.stderr == "",
                "restored replay output changed")


def main() -> int:
    check_normal_replay_and_determinism()
    check_resource_endpoints()
    check_hostile_archives_before_retention()
    check_anchor_closure_and_comparison_failures()
    check_worked_and_deliberate_failure()
    print("ass-103 lab smoke: PASS")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (AssertionError, ReplayError) as error:
        print(f"ass-103 lab smoke: FAIL: {error}", file=sys.stderr)
        raise SystemExit(1)
