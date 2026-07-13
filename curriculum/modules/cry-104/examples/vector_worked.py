#!/usr/bin/env python3
"""Verify the pinned course vector bundle and print a bounded result record."""

from __future__ import annotations

from pathlib import Path

from vector_harness import load_sha256_vectors, run_sha256_vectors, verify_provenance


def main() -> int:
    root = Path(__file__).resolve().parent
    artifacts = verify_provenance(root / "provenance.json", root)
    vectors = load_sha256_vectors(artifacts[0])
    results = run_sha256_vectors(vectors)
    for result in results:
        verdict = "PASS" if result.passed else "FAIL"
        print(f"{result.vector_id}: {verdict}: {result.actual_digest}")
    print(f"summary: {sum(item.passed for item in results)}/{len(results)} passed")
    return 0 if all(item.passed for item in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
