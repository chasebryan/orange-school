#!/usr/bin/env python3
"""Check SYS-105 public fixtures and bounded leakage-evidence helpers."""

from __future__ import annotations

import hashlib
from itertools import repeat
import math
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Callable


sys.dont_write_bytecode = True
MODULE_ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = MODULE_ROOT / "examples"
SOURCES = ("compare.h", "compare.c", "harness.c", "leakage_evidence.py")
EXPECTED_OUTPUT = """leaky-prefix iterations=1 equal=0
leaky-suffix iterations=32 equal=0
control-prefix iterations=32 equal=0
control-suffix iterations=32 equal=0
control-equal iterations=32 equal=1
"""


class SmokeFailure(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SmokeFailure(message)


def expect_error(error_type: type[BaseException], action: Callable[[], object]) -> None:
    try:
        action()
    except error_type:
        return
    raise SmokeFailure(f"expected {error_type.__name__}")


def run(command: list[str], cwd: Path, environment: dict[str, str]) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        command,
        cwd=cwd,
        env=environment,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=12,
        check=False,
    )
    require(
        result.returncode == 0,
        f"command failed ({result.returncode}): {' '.join(command)}; "
        f"stdout={result.stdout!r}; stderr={result.stderr!r}",
    )
    return result


def find_c17_compiler(environment: dict[str, str]) -> str:
    """Return a C compiler that actually works inside the sanitized host envelope."""
    candidates = [
        shutil.which("cc"),
        shutil.which("gcc"),
        shutil.which("clang"),
        "/usr/bin/cc",
        "/usr/bin/gcc",
        "/usr/bin/clang",
        "/bin/cc",
    ]
    seen: set[str] = set()
    for candidate in candidates:
        if candidate is None or candidate in seen or not Path(candidate).is_file():
            continue
        seen.add(candidate)
        try:
            probe = subprocess.run(
                [candidate, "-std=c17", "-Wall", "-Wextra", "-Werror", "-pedantic", "-x", "c", "-fsyntax-only", "-"],
                input="int main(void) { return 0; }\n",
                env=environment,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=12,
                check=False,
            )
        except (OSError, subprocess.SubprocessError):
            continue
        if probe.returncode == 0:
            return candidate
    raise SmokeFailure("no C17 compiler works inside the sanitized host envelope")


def check_statistics(source_dir: Path) -> None:
    sys.path.insert(0, str(source_dir))
    from leakage_evidence import (  # noqa: PLC0415
        MAX_ABS_SAMPLE,
        MAX_SAMPLES_PER_CLASS,
        bonferroni_per_test_alpha,
        synthetic_fixture,
        welch_evidence,
    )

    fixture = synthetic_fixture()
    control = welch_evidence(fixture["control_left"], fixture["control_right"])
    deliberate = welch_evidence(
        fixture["deliberate_left"], fixture["deliberate_right"]
    )
    drift = welch_evidence(fixture["drift_early"], fixture["drift_late"])
    require(control.mean_difference == 0.0, "control effect changed")
    require(control.t_statistic == 0.0, "control t statistic changed")
    require(deliberate.mean_difference == -40.0, "deliberate effect changed")
    require(abs(deliberate.t_statistic) > 50.0, "deliberate signal became weak")
    require(drift.mean_difference == -10.0, "drift confound changed")
    require(abs(drift.t_statistic) > 10.0, "drift example no longer shows confounding")
    require(
        math.isclose(bonferroni_per_test_alpha(0.05, 10), 0.005),
        "multiple-test threshold changed",
    )
    expect_error(ValueError, lambda: welch_evidence([1.0], [2.0, 3.0]))
    expect_error(ValueError, lambda: welch_evidence([1.0, 1.0], [1.0, 1.0]))
    expect_error(ValueError, lambda: welch_evidence([1.0, math.nan], [2.0, 3.0]))
    expect_error(TypeError, lambda: welch_evidence([True, 1.0], [2.0, 3.0]))
    bounded_endpoint = welch_evidence(
        [-MAX_ABS_SAMPLE, MAX_ABS_SAMPLE],
        [-MAX_ABS_SAMPLE + 1.0, MAX_ABS_SAMPLE - 1.0],
    )
    require(math.isfinite(bounded_endpoint.t_statistic), "sample-magnitude endpoint failed")
    expect_error(
        ValueError,
        lambda: welch_evidence([MAX_ABS_SAMPLE + 1.0, 0.0], [1.0, 2.0]),
    )
    expect_error(
        ValueError,
        lambda: welch_evidence(
            [float(value) for value in range(MAX_SAMPLES_PER_CLASS + 1)],
            [2.0, 3.0],
        ),
    )
    expect_error(ValueError, lambda: welch_evidence(repeat(1.0), [2.0, 3.0]))
    expect_error(ValueError, lambda: bonferroni_per_test_alpha(0.0, 1))
    expect_error(ValueError, lambda: bonferroni_per_test_alpha(0.05, 0))
    expect_error(TypeError, lambda: bonferroni_per_test_alpha(0.05, True))


def inspect_if_available(
    object_path: Path, workspace: Path, environment: dict[str, str]
) -> None:
    nm = shutil.which("nm")
    if nm is not None:
        result = subprocess.run(
            [nm, str(object_path)],
            cwd=workspace,
            env=environment,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=12,
            check=False,
        )
        if result.returncode == 0:
            require("sys105_early_exit" in result.stdout, "nm missed early-exit symbol")
            require(
                "sys105_fixed_scan_source" in result.stdout,
                "nm missed fixed-scan symbol",
            )
    objdump = shutil.which("objdump")
    if objdump is not None:
        result = subprocess.run(
            [objdump, "-d", str(object_path)],
            cwd=workspace,
            env=environment,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=12,
            check=False,
        )
        if result.returncode == 0:
            require(result.stdout.strip() != "", "objdump returned empty output")


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="sys-105-smoke-") as value:
        workspace = Path(value)
        source_dir = workspace / "src"
        build_dir = workspace / "build"
        temporary_dir = workspace / "tmp"
        source_dir.mkdir()
        build_dir.mkdir()
        temporary_dir.mkdir()
        for name in SOURCES:
            shutil.copy2(EXAMPLES / name, source_dir / name)

        environment = dict(os.environ)
        environment.update(
            {
                "LC_ALL": "C",
                "TMPDIR": str(temporary_dir),
                "PYTHONDONTWRITEBYTECODE": "1",
                "PYTHONHASHSEED": "0",
            }
        )
        cc = find_c17_compiler(environment)
        common = [
            cc,
            "-std=c17",
            "-Wall",
            "-Wextra",
            "-Wpedantic",
            "-Werror",
            "-I",
            str(source_dir),
        ]
        compare_object = build_dir / "compare.o"
        harness_object = build_dir / "harness.o"
        run(common + ["-O2", "-c", str(source_dir / "compare.c"), "-o", str(compare_object)], workspace, environment)
        run(common + ["-O2", "-c", str(source_dir / "harness.c"), "-o", str(harness_object)], workspace, environment)
        executable = build_dir / "fixture"
        run([cc, str(compare_object), str(harness_object), "-o", str(executable)], workspace, environment)
        executed = run([str(executable)], workspace, environment)
        require(executed.stdout == EXPECTED_OUTPUT, "fixture observations changed")
        require(executed.stderr == "", "fixture wrote stderr")

        assembly_hashes: dict[str, str] = {}
        for level in ("-O0", "-O2"):
            assembly = build_dir / f"compare-{level[1:]}.s"
            run(common + [level, "-S", str(source_dir / "compare.c"), "-o", str(assembly)], workspace, environment)
            require(assembly.stat().st_size > 0, f"{level} assembly is empty")
            assembly_hashes[level] = hashlib.sha256(assembly.read_bytes()).hexdigest()
        require(set(assembly_hashes) == {"-O0", "-O2"}, "assembly evidence is incomplete")
        inspect_if_available(compare_object, workspace, environment)
        check_statistics(source_dir)

        require(
            not any(workspace.rglob("__pycache__")),
            "smoke check created a Python cache",
        )
    print("sys-105 lab smoke: PASS")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, SmokeFailure, subprocess.SubprocessError) as error:
        print(f"sys-105 lab smoke: FAIL: {error}", file=sys.stderr)
        raise SystemExit(1)
