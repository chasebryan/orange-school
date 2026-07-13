#!/usr/bin/env python3
"""Run registered host-language lab and example smoke checks."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any


def parse_version(output: str) -> tuple[int, ...]:
    for token in output.replace("(", " ").split():
        pieces = token.split(".")
        if len(pieces) >= 2 and all(piece.isdigit() for piece in pieces[:2]):
            return tuple(int(piece) for piece in pieces[:2])
    return ()


def command_version(command: list[str]) -> tuple[int, ...]:
    try:
        result = subprocess.run(
            command,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )
    except OSError:
        return ()
    return parse_version(result.stdout) if result.returncode == 0 else ()


def supports_c17() -> bool:
    try:
        result = subprocess.run(
            ["cc", "-std=c17", "-Wall", "-Wextra", "-Werror", "-pedantic", "-x", "c", "-fsyntax-only", "-"],
            input="int main(void) { return 0; }\n",
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
    except OSError:
        return False
    return result.returncode == 0


def rust_toolchain_matches(expected: str) -> bool:
    try:
        result = subprocess.run(
            ["rustc", f"+{expected}", "--version"],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )
    except OSError:
        return False
    return result.returncode == 0 and result.stdout.startswith(f"rustc {expected} ")


def load_catalog(root: Path) -> dict[str, Any]:
    return json.loads((root / "curriculum" / "catalog.json").read_text(encoding="utf-8"))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--timeout", type=int, default=30)
    args = parser.parse_args(argv)
    root = args.root.resolve()
    catalog = load_catalog(root)
    envelope = catalog["host_validation_envelope"]
    required_python = tuple(int(value) for value in envelope["python_minimum"].split("."))
    required_bash = tuple(int(value) for value in envelope["bash_minimum"].split("."))
    required_git = tuple(int(value) for value in envelope["git_minimum"].split("."))
    actual_python = sys.version_info[:2]
    actual_bash = command_version(["bash", "--version"])
    actual_git = command_version(["git", "--version"])
    version_failures: list[str] = []
    for name, actual, required in (
        ("Python", actual_python, required_python),
        ("Bash", actual_bash, required_bash),
        ("Git", actual_git, required_git),
    ):
        if not actual or actual < required:
            version_failures.append(
                f"{name} {'.'.join(map(str, actual)) or '<unavailable>'} is below "
                f"{'.'.join(map(str, required))}"
            )
    if envelope["c_standard"] != "C17" or not supports_c17():
        version_failures.append("cc does not accept the required C17 validation profile")
    if not rust_toolchain_matches(envelope["rust_toolchain"]):
        version_failures.append(
            f"Rust {envelope['rust_toolchain']} is unavailable or does not match exactly"
        )
    if version_failures:
        print("host validation envelope is not satisfied:", file=sys.stderr)
        for failure in version_failures:
            print(f"- {failure}", file=sys.stderr)
        return 1

    checks: list[tuple[str, dict[str, Any]]] = []
    for module in catalog["modules"]:
        if module.get("status") != "released":
            continue
        for check in module.get("host_checks", []):
            checks.append((module["id"], check))

    failures: list[str] = []
    with tempfile.TemporaryDirectory(prefix="orange-school-host-") as sandbox_value:
        sandbox = Path(sandbox_value)
        home = sandbox / "home"
        temporary = sandbox / "tmp"
        home.mkdir()
        temporary.mkdir()
        environment = dict(os.environ)
        environment.update(
            {
                "HOME": str(home),
                "TMPDIR": str(temporary),
                "SCHOOL_ROOT": str(root),
                "PYTHONDONTWRITEBYTECODE": "1",
                "PYTHONHASHSEED": "0",
            }
        )

        for module_id, check in checks:
            path = root / check["path"]
            runner = check["runner"]
            command = ["bash", str(path)] if runner == "bash" else [sys.executable, str(path)]
            try:
                result = subprocess.run(
                    command,
                    cwd=root,
                    env=environment,
                    text=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    check=False,
                    timeout=args.timeout,
                )
            except subprocess.TimeoutExpired:
                failures.append(
                    f"{check['id']} ({module_id}) exceeded {args.timeout} seconds"
                )
                continue
            if result.returncode != 0:
                failures.append(
                    f"{check['id']} ({module_id}) exited {result.returncode}; "
                    f"stdout={result.stdout.strip()!r}; stderr={result.stderr.strip()!r}"
                )

    if failures:
        print("host example checks failed:", file=sys.stderr)
        for failure in failures:
            print(f"- {failure}", file=sys.stderr)
        return 1
    print(
        f"host example checks passed: {len(checks)} registered checks "
        f"(Python {actual_python[0]}.{actual_python[1]}, "
        f"Bash {actual_bash[0]}.{actual_bash[1]}, Git {actual_git[0]}.{actual_git[1]}, "
        f"C17, Rust {envelope['rust_toolchain']})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
