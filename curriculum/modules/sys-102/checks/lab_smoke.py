#!/usr/bin/env python3
"""Compile and smoke-check the SYS-102 C17/Rust ownership examples."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


sys.dont_write_bytecode = True
MODULE_ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = MODULE_ROOT / "examples"
SOURCE_NAMES = (
    "owned_buffer.h",
    "owned_buffer.c",
    "c_harness.c",
    "ownership_bridge.rs",
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def run(
    command: list[str],
    *,
    cwd: Path,
    environment: dict[str, str],
    timeout: int = 20,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=cwd,
        env=environment,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=timeout,
        check=False,
    )


def executable_home(executable: str) -> Path | None:
    path_value = shutil.which(executable)
    if path_value is None:
        return None
    path = Path(path_value)
    for parent in path.parents:
        if parent.name in {".cargo", ".local"}:
            return parent.parent
    return None


def tool_environment(workspace: Path) -> dict[str, str]:
    environment = dict(os.environ)
    environment.update(
        {
            "LC_ALL": "C",
            "TMPDIR": str(workspace / "tmp"),
            "PYTHONDONTWRITEBYTECODE": "1",
            "RUST_BACKTRACE": "0",
        }
    )
    rust_home = executable_home("rustc")
    if rust_home is not None:
        rustup_home = rust_home / ".rustup"
        toolchains = rustup_home / "toolchains"
        require(toolchains.is_dir(), "installed rustup toolchain store is unavailable")
        require(
            any(path.name.startswith("1.96.1-") for path in toolchains.iterdir()),
            "installed Rust 1.96.1 toolchain is unavailable",
        )
        environment["RUSTUP_HOME"] = str(rustup_home)
    return environment


def cc_environment(environment: dict[str, str]) -> dict[str, str]:
    result = dict(environment)
    home = executable_home("cc")
    if home is not None:
        result["HOME"] = str(home)
    return result


def compile_c(
    source: Path,
    output: Path,
    *,
    sources: Path,
    workspace: Path,
    environment: dict[str, str],
    extra: list[Path] | None = None,
) -> None:
    command = [
        "cc",
        "-std=c17",
        "-Wall",
        "-Wextra",
        "-Wpedantic",
        "-Werror",
        "-I",
        str(sources),
        str(source),
    ]
    if extra:
        command.extend(str(path) for path in extra)
    command.extend(["-o", str(output)])
    result = run(command, cwd=workspace, environment=cc_environment(environment))
    require(result.returncode == 0, f"C compilation failed: {result.stderr}")
    require(result.stdout == "", "C compiler wrote unexpected stdout")


def check_c(
    workspace: Path,
    sources: Path,
    environment: dict[str, str],
) -> Path:
    object_path = workspace / "owned_buffer.o"
    compile_result = run(
        [
            "cc",
            "-std=c17",
            "-Wall",
            "-Wextra",
            "-Wpedantic",
            "-Werror",
            "-I",
            str(sources),
            "-c",
            str(sources / "owned_buffer.c"),
            "-o",
            str(object_path),
        ],
        cwd=workspace,
        environment=cc_environment(environment),
    )
    require(compile_result.returncode == 0, f"C object build failed: {compile_result.stderr}")
    require(compile_result.stdout == "", "C object build wrote unexpected stdout")

    harness = workspace / "c_harness"
    compile_c(
        sources / "c_harness.c",
        harness,
        sources=sources,
        workspace=workspace,
        environment=environment,
        extra=[object_path],
    )
    baseline = run([str(harness)], cwd=workspace, environment=environment)
    require(baseline.returncode == 0, f"C harness failed: {baseline.stderr}")
    require(baseline.stderr == "", "C harness wrote diagnostics")
    require(
        baseline.stdout == "c sys102 ownership tests: PASS\n",
        "C harness success output changed",
    )

    original_text = (sources / "c_harness.c").read_text(encoding="utf-8")
    wrong = "CHECK(sum == 10);"
    replacement = "CHECK(sum == 11);"
    require(original_text.count(wrong) == 1, "deliberate-failure mutation point changed")
    deliberate_source = workspace / "c_harness_deliberate.c"
    deliberate_source.write_text(original_text.replace(wrong, replacement), encoding="utf-8")
    deliberate_binary = workspace / "c_harness_deliberate"
    compile_c(
        deliberate_source,
        deliberate_binary,
        sources=sources,
        workspace=workspace,
        environment=environment,
        extra=[object_path],
    )
    failed = run([str(deliberate_binary)], cwd=workspace, environment=environment)
    require(failed.returncode != 0, "deliberately wrong C checksum expectation passed")
    require(failed.stdout == "", "deliberate C failure wrote success output")
    require("sum == 11" in failed.stderr, "deliberate C failure was not observable")

    deliberate_source.write_text(original_text, encoding="utf-8")
    recovered_binary = workspace / "c_harness_recovered"
    compile_c(
        deliberate_source,
        recovered_binary,
        sources=sources,
        workspace=workspace,
        environment=environment,
        extra=[object_path],
    )
    recovered = run([str(recovered_binary)], cwd=workspace, environment=environment)
    require(recovered.returncode == 0, f"restored C harness failed: {recovered.stderr}")
    require(recovered.stderr == "", "restored C harness wrote diagnostics")
    require(
        recovered.stdout == "c sys102 ownership tests: PASS\n",
        "restored C harness output changed",
    )
    return object_path


def check_rust(
    workspace: Path,
    sources: Path,
    object_path: Path,
    environment: dict[str, str],
) -> None:
    rust_home = executable_home("rustc")
    rust_environment = dict(environment)
    if rust_home is not None:
        rust_environment["HOME"] = str(rust_home)

    version = run(
        ["rustc", "+1.96.1", "--version"],
        cwd=workspace,
        environment=rust_environment,
    )
    require(version.returncode == 0, f"Rust 1.96.1 is unavailable: {version.stderr}")
    require(version.stdout.startswith("rustc 1.96.1 "), "Rust toolchain version changed")

    tests = workspace / "ownership_tests"
    compiled = run(
        [
            "rustc",
            "+1.96.1",
            "--edition=2024",
            "--test",
            "-D",
            "warnings",
            "-C",
            f"link-arg={object_path}",
            str(sources / "ownership_bridge.rs"),
            "-o",
            str(tests),
        ],
        cwd=workspace,
        environment=rust_environment,
    )
    require(compiled.returncode == 0, f"Rust test build failed: {compiled.stderr}")
    require(compiled.stdout == "", "Rust compiler wrote unexpected stdout")

    tested = run(
        [str(tests), "--test-threads=1"],
        cwd=workspace,
        environment=rust_environment,
    )
    require(tested.returncode == 0, f"Rust tests failed: {tested.stderr}\n{tested.stdout}")
    require(tested.stderr == "", "Rust tests wrote diagnostics")
    require("test result: ok. 5 passed; 0 failed" in tested.stdout, "Rust test count changed")

    borrow_conflict = workspace / "borrow_conflict.rs"
    borrow_conflict.write_text(
        "fn main() {\n"
        "    let mut bytes = [1_u8, 2, 3];\n"
        "    let shared = &bytes[..];\n"
        "    bytes[0] = 9;\n"
        "    println!(\"{}\", shared[0]);\n"
        "}\n",
        encoding="utf-8",
    )
    rejected = run(
        [
            "rustc",
            "+1.96.1",
            "--edition=2024",
            "-D",
            "warnings",
            str(borrow_conflict),
            "-o",
            str(workspace / "borrow_conflict"),
        ],
        cwd=workspace,
        environment=rust_environment,
    )
    require(rejected.returncode != 0, "overlapping shared/mutable Rust access compiled")
    require(
        "cannot assign" in rejected.stderr or "cannot borrow" in rejected.stderr,
        "Rust borrow rejection was not observable",
    )
    require(not (workspace / "borrow_conflict").exists(), "rejected Rust source produced a binary")


def main() -> int:
    for name in SOURCE_NAMES:
        require((EXAMPLES / name).is_file(), f"missing source: {name}")
    require(shutil.which("cc") is not None, "cc is unavailable")
    require(shutil.which("rustc") is not None, "rustc is unavailable")

    with tempfile.TemporaryDirectory(prefix="sys-102-smoke-") as temporary_value:
        workspace = Path(temporary_value)
        sources = workspace / "src"
        sources.mkdir()
        (workspace / "tmp").mkdir()
        for name in SOURCE_NAMES:
            shutil.copy2(EXAMPLES / name, sources / name)
        environment = tool_environment(workspace)
        object_path = check_c(workspace, sources, environment)
        check_rust(workspace, sources, object_path, environment)

    print("sys-102 lab smoke: PASS")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as error:
        print(f"sys-102 lab smoke: FAIL: {error}", file=sys.stderr)
        raise SystemExit(1)
