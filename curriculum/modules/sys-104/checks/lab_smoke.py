#!/usr/bin/env python3
"""Validate SYS-104 models and native baselines using temporary output only."""

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
SOURCES = ("target_policy.py", "baseline_add.c", "dispatch_model.rs")


class SmokeFailure(RuntimeError):
    """A failed build, test, or evidence boundary."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SmokeFailure(message)


def inferred_user_home(tool: str) -> Path | None:
    path = Path(tool)
    if path.parent.name == "bin" and path.parent.parent.name in {".cargo", ".local"}:
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
        timeout=15,
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


def build_environment(workspace: Path, cc: str, rustc: str) -> dict[str, str]:
    environment = dict(os.environ)
    environment.update(
        {
            "LC_ALL": "C",
            "TMPDIR": str(workspace / "tmp"),
            "PYTHONDONTWRITEBYTECODE": "1",
        }
    )
    tool_home = inferred_user_home(rustc) or inferred_user_home(cc)
    if tool_home is not None:
        environment["HOME"] = str(tool_home)
        rustup_home = tool_home / ".rustup"
        if "RUSTUP_HOME" not in environment and rustup_home.is_dir():
            environment["RUSTUP_HOME"] = str(rustup_home)
    return environment


def check_python_model(source_dir: Path) -> None:
    sys.path.insert(0, str(source_dir))
    try:
        from target_policy import (  # type: ignore[import-not-found]
            ArtifactTuple,
            BuildManifest,
            Variant,
            add_u32_lanes,
            select_variant,
        )

        artifact = ArtifactTuple(
            "x86_64-unknown-linux-gnu",
            "x86-64",
            "System V",
            "linux",
            "ELF",
            "little",
            64,
        )
        baseline = Variant("baseline", 32, 32, frozenset())
        simd = Variant("simd128", 32, 128, frozenset({"sse2"}))
        manifest = BuildManifest(artifact, (baseline, simd))
        require(baseline.lane_count == 1, "scalar baseline lane count changed")
        require(simd.lane_count == 4, "u32 SIMD lane count changed")
        require(
            select_variant(manifest, artifact, frozenset()).name == "baseline",
            "missing runtime feature did not select baseline",
        )
        require(
            select_variant(manifest, artifact, frozenset({"sse2"})).name == "simd128",
            "eligible accelerated variant was not selected",
        )
        require(
            add_u32_lanes((0, 1, 0xFFFFFFFF, 4), (0, 2, 1, 5), 4)
            == (0, 3, 0, 9),
            "lane semantics changed",
        )

        invalid_cases = (
            lambda: ArtifactTuple("x", "i", "a", "o", "f", "middle", 64),
            lambda: ArtifactTuple("x", "i", "a", "o", "f", "little", True),
            lambda: BuildManifest(artifact, (simd,)),
            lambda: Variant("bad-width", 24, 128, frozenset({"feature"})),
            lambda: select_variant(manifest, artifact, {"sse2"}),
            lambda: select_variant(
                manifest,
                ArtifactTuple("other", "x86-64", "System V", "linux", "ELF", "little", 64),
                frozenset(),
            ),
            lambda: add_u32_lanes((1,), (2,), 2),
            lambda: add_u32_lanes((True,), (2,), 1),
        )
        for invalid in invalid_cases:
            try:
                invalid()
            except (TypeError, ValueError):
                pass
            else:
                raise SmokeFailure("invalid policy-model input was accepted")
    finally:
        sys.path.remove(str(source_dir))
        sys.modules.pop("target_policy", None)


def object_observation(
    executable: Path,
    *,
    workspace: Path,
    environment: dict[str, str],
) -> dict[str, object]:
    artifact_sha256 = hashlib.sha256(executable.read_bytes()).hexdigest()
    for name, arguments in (
        ("readelf", ("-h", str(executable))),
        ("objdump", ("-f", str(executable))),
        ("file", (str(executable),)),
    ):
        tool = shutil.which(name)
        if tool is None:
            continue
        result = run(
            (tool, *arguments),
            cwd=workspace,
            environment=environment,
            expect_success=None,
        )
        if result.returncode == 0 and result.stdout.strip():
            version = run(
                (tool, "--version"),
                cwd=workspace,
                environment=environment,
                expect_success=None,
            )
            version_text = version.stdout + version.stderr
            return {
                "tool": name,
                "tool_version_sha256": hashlib.sha256(
                    version_text.encode()
                ).hexdigest(),
                "artifact_sha256": artifact_sha256,
                "stdout_sha256": hashlib.sha256(result.stdout.encode()).hexdigest(),
            }
    return {
        "tool": None,
        "tool_version_sha256": None,
        "artifact_sha256": artifact_sha256,
        "stdout_sha256": None,
    }


def main() -> int:
    cc = shutil.which("cc")
    rustc = shutil.which("rustc")
    require(cc is not None, "cc is unavailable")
    require(rustc is not None, "rustc is unavailable")

    with tempfile.TemporaryDirectory(prefix="sys-104-smoke-") as temporary:
        workspace = Path(temporary)
        source_dir = workspace / "src"
        source_dir.mkdir()
        (workspace / "tmp").mkdir()
        for source in SOURCES:
            shutil.copy2(EXAMPLES / source, source_dir / source)
        environment = build_environment(workspace, cc, rustc)

        check_python_model(source_dir)

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
        rust_cfg = run(
            (rustc, f"+{RUST_TOOLCHAIN}", "--print", "cfg"),
            cwd=workspace,
            environment=environment,
        )
        for key in ("target_arch=", "target_endian=", "target_os=", "target_pointer_width="):
            require(key in rust_cfg.stdout, f"rustc cfg omitted {key}")
        known_targets = run(
            (rustc, f"+{RUST_TOOLCHAIN}", "--print", "target-list"),
            cwd=workspace,
            environment=environment,
        )
        require(known_targets.stdout.strip() != "", "rustc target list is empty")
        cc_version = run(
            (cc, "--version"), cwd=workspace, environment=environment
        )

        c_executable = workspace / "c_baseline"
        run(
            (
                cc,
                "-std=c17",
                "-Wall",
                "-Wextra",
                "-Wpedantic",
                "-Werror",
                str(source_dir / "baseline_add.c"),
                "-o",
                str(c_executable),
            ),
            cwd=workspace,
            environment=environment,
        )
        c_result = run((str(c_executable),), cwd=workspace, environment=environment)
        require(c_result.stderr == "", "C baseline wrote diagnostics")
        require(c_result.stdout == "sys-104 C baseline: PASS\n", "C output changed")

        rust_tests = workspace / "rust_dispatch_tests"
        run(
            (
                rustc,
                f"+{RUST_TOOLCHAIN}",
                "--edition=2024",
                "--test",
                "-D",
                "warnings",
                str(source_dir / "dispatch_model.rs"),
                "-o",
                str(rust_tests),
            ),
            cwd=workspace,
            environment=environment,
        )
        rust_result = run(
            (str(rust_tests), "--test-threads=1"),
            cwd=workspace,
            environment=environment,
        )
        require(rust_result.stderr == "", "Rust dispatch tests wrote diagnostics")
        require("4 passed; 0 failed" in rust_result.stdout, "Rust test count changed")

        # This deliberate policy failure is data-only. It never executes a
        # target-specific instruction.
        deliberate = source_dir / "deliberate_failure.py"
        deliberate.write_text(
            "from target_policy import *\n"
            "a=ArtifactTuple('t','i','a','o','f','little',64)\n"
            "m=BuildManifest(a,(Variant('baseline',32,32,frozenset()),"
            "Variant('simd128',32,128,frozenset({'vector'}))))\n"
            "assert select_variant(m,a,frozenset()).name == 'simd128'\n",
            encoding="utf-8",
        )
        failed = run(
            (sys.executable, "-B", str(deliberate)),
            cwd=source_dir,
            environment=environment,
            expect_success=False,
        )
        require("AssertionError" in failed.stderr, "deliberate failure was not observable")

        observations = {
            "sources": {
                name: hashlib.sha256((source_dir / name).read_bytes()).hexdigest()
                for name in SOURCES
            },
            "rustc_vv_sha256": hashlib.sha256(rust_verbose.stdout.encode()).hexdigest(),
            "rust_cfg_sha256": hashlib.sha256(rust_cfg.stdout.encode()).hexdigest(),
            "rust_target_list_sha256": hashlib.sha256(
                known_targets.stdout.encode()
            ).hexdigest(),
            "cc_version_sha256": hashlib.sha256(
                (cc_version.stdout + cc_version.stderr).encode()
            ).hexdigest(),
            "c_artifact": object_observation(
                c_executable, workspace=workspace, environment=environment
            ),
        }
        evidence = workspace / "evidence.json"
        evidence.write_text(json.dumps(observations, sort_keys=True), encoding="utf-8")
        require(json.loads(evidence.read_text(encoding="utf-8")) == observations, "evidence changed")

    print("sys-104 lab smoke: PASS")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as error:
        print(f"sys-104 lab smoke: FAIL: {error}", file=sys.stderr)
        raise SystemExit(1)
