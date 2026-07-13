#!/usr/bin/env python3
"""Build and inspect the SYS-103 C17/Rust ABI example in a temporary tree."""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Sequence


sys.dont_write_bytecode = True
MODULE_ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = MODULE_ROOT / "examples"
RUST_TOOLCHAIN = "1.96.1"
SOURCES = (
    "abi_contract.h",
    "checksum.c",
    "layout_probe.c",
    "c_harness.c",
    "ffi_probe.rs",
    "unresolved_consumer.c",
)


class SmokeFailure(RuntimeError):
    """A failed build or observation."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SmokeFailure(message)


def inferred_user_home(tool: str) -> Path | None:
    path = Path(tool)
    if (
        path.parent.name == "bin"
        and path.parent.parent.name in {".cargo", ".local"}
    ):
        return path.parent.parent.parent
    return None


def run(
    command: Sequence[str],
    *,
    cwd: Path,
    environment: dict[str, str],
    expect_success: bool | None = True,
) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        list(command),
        cwd=cwd,
        env=environment,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=12,
        check=False,
    )
    if expect_success is True and result.returncode != 0:
        raise SmokeFailure(
            f"command failed ({result.returncode}): {' '.join(command)}; "
            f"stdout={result.stdout!r}; stderr={result.stderr!r}"
        )
    if expect_success is False and result.returncode == 0:
        raise SmokeFailure(f"command unexpectedly succeeded: {' '.join(command)}")
    return result


def source_hashes(source_dir: Path) -> dict[str, str]:
    return {
        name: hashlib.sha256((source_dir / name).read_bytes()).hexdigest()
        for name in SOURCES
    }


def build_environment(
    workspace: Path, cc: str, rustc: str
) -> dict[str, str]:
    environment = dict(os.environ)
    environment.update(
        {
            "LC_ALL": "C",
            "TMPDIR": str(workspace / "tmp"),
        }
    )
    tool_home = inferred_user_home(rustc) or inferred_user_home(cc)
    if tool_home is not None:
        environment["HOME"] = str(tool_home)
        rustup_home = tool_home / ".rustup"
        if "RUSTUP_HOME" not in environment and rustup_home.is_dir():
            environment["RUSTUP_HOME"] = str(rustup_home)
    return environment


def compile_c(
    cc: str,
    source: Path,
    output: Path,
    *,
    include: Path,
    workspace: Path,
    environment: dict[str, str],
) -> None:
    run(
        (
            cc,
            "-std=c17",
            "-Wall",
            "-Wextra",
            "-Wpedantic",
            "-Werror",
            "-I",
            str(include),
            "-c",
            str(source),
            "-o",
            str(output),
        ),
        cwd=workspace,
        environment=environment,
    )


def inspect_symbols_and_objects(
    *,
    tools: dict[str, str | None],
    workspace: Path,
    environment: dict[str, str],
    checksum_object: Path,
    harness_object: Path,
    executable: Path,
) -> dict[str, object]:
    observations: dict[str, object] = {}
    nm = tools["nm"]
    if nm is not None:
        checksum_symbols = run(
            (nm, str(checksum_object)),
            cwd=workspace,
            environment=environment,
            expect_success=None,
        )
        harness_symbols = run(
            (nm, str(harness_object)),
            cwd=workspace,
            environment=environment,
            expect_success=None,
        )
        if checksum_symbols.returncode == 0 and harness_symbols.returncode == 0:
            require(
                "sys103_checksum" in checksum_symbols.stdout,
                "nm did not observe the checksum definition",
            )
            require(
                "sys103_checksum" in harness_symbols.stdout,
                "nm did not observe the checksum reference",
            )
            observations["nm"] = {
                "usable_for_artifacts": True,
                "checksum_sha256": hashlib.sha256(
                    checksum_symbols.stdout.encode("utf-8")
                ).hexdigest(),
                "harness_sha256": hashlib.sha256(
                    harness_symbols.stdout.encode("utf-8")
                ).hexdigest(),
            }
        else:
            observations["nm"] = {
                "usable_for_artifacts": False,
                "checksum_status": checksum_symbols.returncode,
                "harness_status": harness_symbols.returncode,
            }

    readelf = tools["readelf"]
    objdump = tools["objdump"]
    inspector_results: dict[str, str] = {}
    if readelf is not None:
        readelf_results: list[tuple[str, subprocess.CompletedProcess[str]]] = []
        for label, arguments in (
            ("sections", (readelf, "-S", str(checksum_object))),
            ("relocations", (readelf, "-r", str(harness_object))),
            ("dynamic", (readelf, "-d", str(executable))),
        ):
            result = run(
                arguments,
                cwd=workspace,
                environment=environment,
                expect_success=None,
            )
            readelf_results.append((label, result))
        if all(
            result.returncode == 0 and result.stdout.strip() != ""
            for _, result in readelf_results
        ):
            inspector_results = {
                label: hashlib.sha256(result.stdout.encode("utf-8")).hexdigest()
                for label, result in readelf_results
            }
            observations["object_inspector"] = {
                "tool": "readelf",
                "outputs": inspector_results,
            }
    if "object_inspector" not in observations and objdump is not None:
        objdump_results: list[tuple[str, subprocess.CompletedProcess[str]]] = []
        for label, arguments in (
            ("sections", (objdump, "-h", str(checksum_object))),
            ("relocations", (objdump, "-r", str(harness_object))),
            ("dynamic", (objdump, "-p", str(executable))),
        ):
            result = run(
                arguments,
                cwd=workspace,
                environment=environment,
                expect_success=None,
            )
            objdump_results.append((label, result))
        if all(
            result.returncode == 0 and result.stdout.strip() != ""
            for _, result in objdump_results
        ):
            inspector_results = {
                label: hashlib.sha256(result.stdout.encode("utf-8")).hexdigest()
                for label, result in objdump_results
            }
            observations["object_inspector"] = {
                "tool": "objdump",
                "outputs": inspector_results,
            }
    if "object_inspector" not in observations:
        observations["object_inspector"] = {"tool": None, "outputs": {}}
    return observations


def main() -> int:
    tools = {
        name: shutil.which(name)
        for name in ("cc", "rustc", "ar", "nm", "readelf", "objdump")
    }
    require(tools["cc"] is not None, "cc is unavailable")
    require(tools["rustc"] is not None, "rustc is unavailable")
    cc = str(tools["cc"])
    rustc = str(tools["rustc"])

    with tempfile.TemporaryDirectory(prefix="sys-103-smoke-") as temporary:
        workspace = Path(temporary)
        source_dir = workspace / "src"
        temporary_dir = workspace / "tmp"
        source_dir.mkdir()
        temporary_dir.mkdir()
        for name in SOURCES:
            shutil.copy2(EXAMPLES / name, source_dir / name)

        environment = build_environment(workspace, cc, rustc)
        rust_version = run(
            (rustc, f"+{RUST_TOOLCHAIN}", "--version"),
            cwd=workspace,
            environment=environment,
        )
        require(
            rust_version.stdout.startswith(f"rustc {RUST_TOOLCHAIN} "),
            f"expected rustc {RUST_TOOLCHAIN}, observed {rust_version.stdout.strip()}",
        )
        rust_verbose = run(
            (rustc, f"+{RUST_TOOLCHAIN}", "-vV"),
            cwd=workspace,
            environment=environment,
        )
        cc_version = run(
            (cc, "--version"), cwd=workspace, environment=environment
        )

        checksum_object = workspace / "checksum.o"
        layout_object = workspace / "layout_probe.o"
        harness_object = workspace / "c_harness.o"
        unresolved_object = workspace / "unresolved_consumer.o"
        for source_name, output in (
            ("checksum.c", checksum_object),
            ("layout_probe.c", layout_object),
            ("c_harness.c", harness_object),
            ("unresolved_consumer.c", unresolved_object),
        ):
            compile_c(
                cc,
                source_dir / source_name,
                output,
                include=source_dir,
                workspace=workspace,
                environment=environment,
            )

        archive = workspace / "libsys103.a"
        archive_used = False
        ar = tools["ar"]
        if ar is not None:
            archive_result = run(
                (ar, "rcs", str(archive), str(checksum_object), str(layout_object)),
                cwd=workspace,
                environment=environment,
                expect_success=None,
            )
            archive_used = archive_result.returncode == 0 and archive.is_file()

        library_inputs = (
            (str(archive),)
            if archive_used
            else (str(checksum_object), str(layout_object))
        )
        c_executable = workspace / "c_harness"
        run(
            (cc, str(harness_object), *library_inputs, "-o", str(c_executable)),
            cwd=workspace,
            environment=environment,
        )
        c_result = run(
            (str(c_executable),), cwd=workspace, environment=environment
        )
        require(c_result.stderr == "", "C harness wrote diagnostics")
        require(
            c_result.stdout.startswith("c ABI tests: PASS; request size="),
            "C harness success evidence changed",
        )

        rust_executable = workspace / "ffi_tests"
        rust_link_arguments: tuple[str, ...]
        if archive_used:
            rust_link_arguments = (
                "-L",
                f"native={workspace}",
                "-l",
                "static=sys103",
            )
        else:
            rust_link_arguments = (
                "-C",
                f"link-arg={checksum_object}",
                "-C",
                f"link-arg={layout_object}",
            )
        run(
            (
                rustc,
                f"+{RUST_TOOLCHAIN}",
                "--edition=2024",
                "--test",
                "-D",
                "warnings",
                *rust_link_arguments,
                str(source_dir / "ffi_probe.rs"),
                "-o",
                str(rust_executable),
            ),
            cwd=workspace,
            environment=environment,
        )
        rust_result = run(
            (str(rust_executable), "--test-threads=1"),
            cwd=workspace,
            environment=environment,
        )
        require(rust_result.stderr == "", "Rust tests wrote diagnostics")
        require("4 passed" in rust_result.stdout, "Rust endpoint/invalid tests changed")

        missing_executable = workspace / "must-not-link"
        missing_link = run(
            (cc, str(unresolved_object), "-o", str(missing_executable)),
            cwd=workspace,
            environment=environment,
            expect_success=False,
        )
        require(
            missing_link.stdout != "" or missing_link.stderr != "",
            "unresolved-symbol link failure had no diagnostic evidence",
        )
        inspections = inspect_symbols_and_objects(
            tools=tools,
            workspace=workspace,
            environment=environment,
            checksum_object=checksum_object,
            harness_object=harness_object,
            executable=c_executable,
        )
        evidence = {
            "schema": 1,
            "sources": source_hashes(source_dir),
            "cc_first_line": cc_version.stdout.splitlines()[0],
            "rustc": rust_version.stdout.strip(),
            "rust_target": next(
                line.removeprefix("host: ")
                for line in rust_verbose.stdout.splitlines()
                if line.startswith("host: ")
            ),
            "capabilities": {name: value is not None for name, value in tools.items()},
            "archive_used": archive_used,
            "c_observation": c_result.stdout.strip(),
            "deliberate_missing_link_status": missing_link.returncode,
            "inspections": inspections,
        }
        (workspace / "target-evidence.json").write_text(
            json.dumps(evidence, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )

    print("sys-103 lab smoke: PASS")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as error:
        print(f"sys-103 lab smoke: FAIL: {error}", file=sys.stderr)
        raise SystemExit(1)
