#!/usr/bin/env python3
"""Run every registered Orange example against the pinned compiler revision."""

from __future__ import annotations

import argparse
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path, PurePosixPath
from typing import Any


SHA_RE = re.compile(r"[0-9a-f]{40}")


def run(command: list[str], *, cwd: Path | None = None, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=cwd,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def run_bytes(command: list[str], *, cwd: Path | None = None) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(
        command,
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def load_catalog(root: Path) -> dict[str, Any]:
    return json.loads((root / "curriculum" / "catalog.json").read_text(encoding="utf-8"))


def command_for_mode(mode: str) -> str:
    """Map a validated catalog example mode to its orangec subcommand."""
    if mode.startswith("check-"):
        return "check"
    if mode.startswith("lex-"):
        return "lex"
    if mode.startswith("eval-"):
        return "eval"
    raise ValueError(f"unsupported Orange example mode: {mode}")


def validated_archive_members(
    archive: tarfile.TarFile, destination: Path
) -> list[tuple[tarfile.TarInfo, Path]]:
    """Map a Git archive to safe local paths before extracting any member."""
    destination = destination.resolve()
    validated: list[tuple[tarfile.TarInfo, Path]] = []
    seen: set[Path] = set()
    for member in archive.getmembers():
        member_path = PurePosixPath(member.name)
        if (
            not member.name
            or "\\" in member.name
            or member_path.is_absolute()
            or any(part in {"", ".", ".."} for part in member_path.parts)
        ):
            raise ValueError(f"unsafe path in pinned Orange archive: {member.name!r}")
        if not (member.isdir() or member.isfile()):
            raise ValueError(
                f"unsupported member type in pinned Orange archive: {member.name!r}"
            )
        target = destination.joinpath(*member_path.parts).resolve()
        try:
            target.relative_to(destination)
        except ValueError as error:
            raise ValueError(
                f"archive member escapes the snapshot: {member.name!r}"
            ) from error
        if target in seen:
            raise ValueError(f"duplicate path in pinned Orange archive: {member.name!r}")
        seen.add(target)
        validated.append((member, target))
    return validated


def extract_archive(archive_bytes: bytes, destination: Path) -> None:
    """Extract only regular files and directories from an already validated tar."""
    destination.mkdir(parents=True, exist_ok=False)
    with tarfile.open(fileobj=io.BytesIO(archive_bytes), mode="r:") as archive:
        members = validated_archive_members(archive, destination)
        for member, target in members:
            if member.isdir():
                target.mkdir(parents=True, exist_ok=True)
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            source = archive.extractfile(member)
            if source is None:
                raise ValueError(f"could not read archived file: {member.name!r}")
            with source, target.open("wb") as output:
                shutil.copyfileobj(source, output)
            target.chmod(member.mode & 0o777)


def extract_pinned_source(
    orange_repo: Path, revision: str, destination: Path
) -> tuple[bool, str]:
    """Export the pinned compiler source from a Git object provider."""
    if not SHA_RE.fullmatch(revision):
        return False, f"invalid catalog Orange revision: {revision!r}"

    commit = run(
        ["git", "cat-file", "-e", f"{revision}^{{commit}}"], cwd=orange_repo
    )
    if commit.returncode != 0:
        detail = commit.stderr.strip() or "commit object is unavailable"
        return False, f"Orange object provider lacks pinned commit {revision}: {detail}"

    archived = run_bytes(
        [
            "git",
            "archive",
            "--format=tar",
            revision,
            "--",
            "compiler",
            "rust-toolchain.toml",
        ],
        cwd=orange_repo,
    )
    if archived.returncode != 0:
        detail = archived.stderr.decode("utf-8", errors="replace").strip()
        return False, f"could not archive pinned Orange source: {detail}"
    try:
        extract_archive(archived.stdout, destination)
    except (OSError, tarfile.TarError, ValueError) as error:
        return False, f"could not safely extract pinned Orange source: {error}"

    required = [
        destination / "compiler" / "Cargo.toml",
        destination / "compiler" / "Cargo.lock",
        destination / "rust-toolchain.toml",
    ]
    missing = [path.relative_to(destination).as_posix() for path in required if not path.is_file()]
    if missing:
        return False, f"pinned Orange archive is missing required files: {', '.join(missing)}"
    return True, ""


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--orange-repo", type=Path)
    args = parser.parse_args(argv)
    root = args.root.resolve()
    catalog = load_catalog(root)
    expected_revision = catalog["orange_source"]["revision"]

    configured_repo = args.orange_repo or Path(os.environ.get("ORANGE_REPO", "../orange"))
    orange_repo = configured_repo.expanduser()
    if not orange_repo.is_absolute():
        orange_repo = (root / orange_repo).resolve()
    if not orange_repo.is_dir():
        print(
            f"Orange Git object provider not found at {orange_repo}; "
            "set ORANGE_REPO to an Orange repository containing the pinned commit",
            file=sys.stderr,
        )
        return 1

    examples: list[dict[str, Any]] = []
    for module in catalog["modules"]:
        if module.get("status") == "released":
            examples.extend(module.get("examples", []))

    with tempfile.TemporaryDirectory(prefix="orange-school-pinned-") as temporary:
        temporary_dir = Path(temporary)
        source_dir = temporary_dir / "source"
        extracted, extraction_error = extract_pinned_source(
            orange_repo, expected_revision, source_dir
        )
        if not extracted:
            print(extraction_error, file=sys.stderr)
            return 1

        target_dir = temporary_dir / "target"
        build = run(
            [
                "cargo",
                "build",
                "--locked",
                "--quiet",
                "--manifest-path",
                str(source_dir / "compiler" / "Cargo.toml"),
                "--package",
                "orangec",
                "--target-dir",
                str(target_dir),
            ],
            cwd=source_dir,
        )
        if build.returncode != 0:
            print("failed to build the pinned orangec:", file=sys.stderr)
            print(build.stderr, file=sys.stderr)
            return 1

        orangec = target_dir / "debug" / "orangec"
        failures: list[str] = []
        for example in examples:
            mode = example["mode"]
            command = command_for_mode(mode)
            path = root / example["path"]
            result = run([str(orangec), command, str(path)], cwd=root)
            should_pass = mode.endswith("-pass")
            expected_exit = 0 if should_pass else 1
            if result.returncode != expected_exit:
                failures.append(
                    f"{example['id']}: expected exit {expected_exit}, got {result.returncode}; "
                    f"stderr={result.stderr.strip()!r}"
                )
                continue
            if mode == "check-pass" and (result.stdout or result.stderr):
                failures.append(
                    f"{example['id']}: successful check must be silent; "
                    f"stdout={result.stdout.strip()!r}, stderr={result.stderr.strip()!r}"
                )
            if mode == "eval-pass" and result.stderr:
                failures.append(
                    f"{example['id']}: successful eval wrote stderr; "
                    f"stderr={result.stderr.strip()!r}"
                )
            if not should_pass and not result.stderr:
                failures.append(f"{example['id']}: rejected source emitted no diagnostic")
            stdout_file = example.get("stdout_file")
            if stdout_file:
                expected_exact = (root / stdout_file).read_text(encoding="utf-8")
                if result.stdout != expected_exact:
                    failures.append(
                        f"{example['id']}: stdout differed from {stdout_file}; "
                        f"stdout={result.stdout!r}"
                    )
            expected_stdout = example.get("stdout_contains")
            if expected_stdout and expected_stdout not in result.stdout:
                failures.append(
                    f"{example['id']}: stdout did not contain {expected_stdout!r}; "
                    f"stdout={result.stdout.strip()!r}"
                )
            expected_stderr = example.get("stderr_contains")
            if expected_stderr and expected_stderr not in result.stderr:
                failures.append(
                    f"{example['id']}: stderr did not contain {expected_stderr!r}; "
                    f"stderr={result.stderr.strip()!r}"
                )

    if failures:
        print("Orange example checks failed:", file=sys.stderr)
        for failure in failures:
            print(f"- {failure}", file=sys.stderr)
        return 1
    print(
        f"Orange example checks passed: {len(examples)} examples at {expected_revision}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
