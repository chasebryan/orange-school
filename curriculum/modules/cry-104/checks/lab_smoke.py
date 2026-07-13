#!/usr/bin/env python3
"""Smoke-check CRY-104 provenance and vector evidence."""

from __future__ import annotations

import json
import hashlib
import hmac
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


sys.dont_write_bytecode = True
MODULE_ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = MODULE_ROOT / "examples"
RESOURCES = MODULE_ROOT / "resources"
sys.path.insert(0, str(EXAMPLES))

from vector_harness import (  # noqa: E402
    MAX_JSON_BYTES,
    file_sha256,
    load_sha256_vectors,
    run_sha256_vectors,
    verify_provenance,
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def expect_error(action, expected_text: str) -> None:
    try:
        action()
    except ValueError as error:
        require(expected_text in str(error), f"wrong error for {expected_text!r}: {error}")
        return
    raise AssertionError(f"expected ValueError containing {expected_text!r}")


def write_json(path: Path, value) -> None:
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def check_baseline() -> None:
    artifacts = verify_provenance(EXAMPLES / "provenance.json", EXAMPLES)
    require(len(artifacts) == 1, "expected one provenance artifact")
    vectors = load_sha256_vectors(artifacts[0])
    require(len(vectors) == 3, "expected three course vectors")
    results = run_sha256_vectors(vectors)
    require(all(item.passed for item in results), "a baseline SHA-256 vector failed")
    require(
        [item.vector_id for item in results]
        == ["sha256-empty", "sha256-abc", "sha256-two-block-example"],
        "vector order or identity changed",
    )
    require(
        [item["source_artifact_id"] for item in vectors]
        == [
            "nist-cavp-sha-byte-archive",
            "nist-sha256-example-pdf",
            "nist-sha256-example-pdf",
        ],
        "exact vector source references changed",
    )


def check_assessment_resources() -> None:
    sheet = (RESOURCES / "rfc4231-cases-1-4.md").read_text(encoding="utf-8")
    rows = [line for line in sheet.splitlines() if re.match(r"\| [1-4] \|", line)]
    require(len(rows) == 4, "assessment data sheet must contain four cases")
    for expected_case, row in enumerate(rows, start=1):
        columns = [item.strip().strip("`") for item in row.strip("|").split("|")]
        require(len(columns) == 5, f"case {expected_case} has the wrong column count")
        case, section, key_hex, data_hex, expected_hex = columns
        require(case == str(expected_case), f"assessment case {expected_case} is out of order")
        require(section == f"4.{expected_case + 1}", f"case {case} has the wrong RFC section")
        key = bytes.fromhex(key_hex)
        data = bytes.fromhex(data_hex)
        actual = hmac.new(key, data, hashlib.sha256).hexdigest()
        require(actual == expected_hex, f"assessment HMAC case {case} is wrong")

    errata = (RESOURCES / "rfc4231-errata-snapshot.md").read_text(encoding="utf-8")
    for evidence in ("3853", "Editorial", "Held for Document Update", "2026-07-12"):
        require(evidence in errata, f"assessment errata snapshot lost {evidence!r}")


def check_provenance_failures(workspace: Path) -> None:
    copied = workspace / "examples"
    shutil.copytree(EXAMPLES, copied)
    vector_path = copied / "vectors" / "sha256.json"
    manifest_path = copied / "provenance.json"

    captured = verify_provenance(manifest_path, copied)[0]
    vector_path.write_text(vector_path.read_text(encoding="utf-8") + " ", encoding="utf-8")
    require(
        all(item.passed for item in run_sha256_vectors(load_sha256_vectors(captured))),
        "verified byte capture changed after its source path changed",
    )
    expect_error(
        lambda: verify_provenance(manifest_path, copied), "digest mismatch"
    )

    vector_path.write_bytes(b" " * (MAX_JSON_BYTES + 1))
    expect_error(
        lambda: verify_provenance(manifest_path, copied),
        f"exceeds {MAX_JSON_BYTES} bytes",
    )

    shutil.rmtree(copied)
    shutil.copytree(EXAMPLES, copied)
    manifest = json.loads((copied / "provenance.json").read_text(encoding="utf-8"))
    manifest["artifacts"][0]["path"] = "../outside.json"
    write_json(copied / "provenance.json", manifest)
    expect_error(
        lambda: verify_provenance(copied / "provenance.json", copied),
        "unsafe artifact path",
    )

    if hasattr(os, "mkfifo"):
        shutil.rmtree(copied)
        shutil.copytree(EXAMPLES, copied)
        fifo = copied / "vectors" / "blocked.json"
        os.mkfifo(fifo)
        manifest = json.loads((copied / "provenance.json").read_text(encoding="utf-8"))
        manifest["artifacts"][0]["path"] = "vectors/blocked.json"
        manifest["artifacts"][0]["sha256"] = "0" * 64
        write_json(copied / "provenance.json", manifest)
        expect_error(
            lambda: verify_provenance(copied / "provenance.json", copied),
            "not a regular file",
        )


def check_vector_failures(workspace: Path) -> None:
    copied = workspace / "mutated"
    shutil.copytree(EXAMPLES, copied)
    vector_path = copied / "vectors" / "sha256.json"
    manifest_path = copied / "provenance.json"
    bundle = json.loads(vector_path.read_text(encoding="utf-8"))

    bundle["vectors"][1]["digest_hex"] = "0" * 64
    write_json(vector_path, bundle)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["artifacts"][0]["sha256"] = file_sha256(vector_path)
    write_json(manifest_path, manifest)
    artifacts = verify_provenance(manifest_path, copied)
    results = run_sha256_vectors(load_sha256_vectors(artifacts[0]))
    require(
        [item.passed for item in results] == [True, False, True],
        "mutated expected digest was not detected by vector execution",
    )

    bundle["vectors"][1]["id"] = bundle["vectors"][0]["id"]
    write_json(vector_path, bundle)
    expect_error(lambda: load_sha256_vectors(vector_path), "duplicate vector id")

    bundle["vectors"][1]["id"] = "sha256-abc"
    bundle["vectors"][1]["message_hex"] = "AB"
    write_json(vector_path, bundle)
    expect_error(lambda: load_sha256_vectors(vector_path), "lowercase hexadecimal")

    duplicate_json = '{"schema_version":1,"schema_version":1,"algorithm":"SHA-256"}'
    vector_path.write_text(duplicate_json, encoding="utf-8")
    expect_error(lambda: load_sha256_vectors(vector_path), "duplicate JSON key")


def check_worked_program(workspace: Path) -> None:
    result = subprocess.run(
        [sys.executable, "-B", str(EXAMPLES / "vector_worked.py")],
        cwd=workspace,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=8,
        check=False,
    )
    require(result.returncode == 0, f"worked vector run failed: {result.stderr}")
    require(result.stderr == "", "worked vector run wrote a diagnostic")
    require("sha256-empty: PASS:" in result.stdout, "empty vector evidence missing")
    require("sha256-abc: PASS:" in result.stdout, "abc vector evidence missing")
    require("summary: 3/3 passed" in result.stdout, "summary evidence missing")


def main() -> int:
    check_baseline()
    check_assessment_resources()
    with tempfile.TemporaryDirectory(prefix="cry-104-smoke-") as temporary:
        workspace = Path(temporary)
        check_provenance_failures(workspace)
        check_vector_failures(workspace)
        check_worked_program(workspace)
    print("cry-104 lab smoke: PASS")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as error:
        print(f"cry-104 lab smoke: FAIL: {error}", file=sys.stderr)
        raise SystemExit(1)
