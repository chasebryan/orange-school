#!/usr/bin/env python3
"""Worked ASS-103 offline replay bundle."""

from __future__ import annotations

import sys

from replay_bundle import (
    MaterialSource,
    ProvenanceSource,
    build_bundle,
    build_manifest,
    make_anchor,
    replay_bundle,
)


sys.dont_write_bytecode = True


def example_materials() -> tuple[MaterialSource, ...]:
    return (
        MaterialSource(
            "format-spec",
            "materials/format.txt",
            b"records are ASCII key=value lines\n",
            (),
            "local-source",
        ),
        MaterialSource(
            "sample-data",
            "materials/sample.txt",
            b"alpha=17\nbeta=29\n",
            ("format-spec",),
            "local-source",
        ),
    )


def make_example(sequence: int = 7) -> tuple[bytes, bytes]:
    materials = example_materials()
    manifest = build_manifest(
        subject="quartz-record-demo",
        sequence=sequence,
        materials=materials,
        provenance=(
            ProvenanceSource(
                "local-source",
                "ASS-103 worked example",
                "local:course-owned-inputs",
                "quartz-v1",
            ),
        ),
        roots=("sample-data",),
    )
    return manifest, build_bundle(manifest, materials)


def main() -> int:
    manifest, bundle = make_example()
    result = replay_bundle(bundle, make_anchor(manifest))
    print(f"subject: {result.subject}")
    print(f"sequence: {result.sequence}")
    print(f"closure: {','.join(result.dependency_closure)}")
    print(f"manifest: {result.manifest_sha256}")
    print(f"output-size: {result.output_size}")
    print(f"output: {result.output_sha256}")
    print(f"workspace-removed: {str(result.temporary_removed).lower()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
