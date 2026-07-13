from __future__ import annotations

import importlib.util
import io
import tarfile
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "check_orange_examples", ROOT / "scripts" / "check_orange_examples.py"
)
assert SPEC and SPEC.loader
ORANGE_CHECKER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(ORANGE_CHECKER)


def tar_with_member(name: str, *, kind: bytes = tarfile.REGTYPE) -> bytes:
    buffer = io.BytesIO()
    with tarfile.open(fileobj=buffer, mode="w") as archive:
        member = tarfile.TarInfo(name)
        member.type = kind
        if kind == tarfile.REGTYPE:
            payload = b"evidence\n"
            member.size = len(payload)
            archive.addfile(member, io.BytesIO(payload))
        else:
            archive.addfile(member)
    return buffer.getvalue()


class OrangeArchiveTests(unittest.TestCase):
    def test_maps_eval_modes_to_eval_subcommand(self) -> None:
        self.assertEqual(ORANGE_CHECKER.command_for_mode("eval-pass"), "eval")
        self.assertEqual(ORANGE_CHECKER.command_for_mode("eval-fail"), "eval")

    def test_rejects_unknown_example_mode(self) -> None:
        with self.assertRaisesRegex(ValueError, "unsupported Orange example mode"):
            ORANGE_CHECKER.command_for_mode("run-pass")

    def test_extracts_regular_file(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            destination = Path(temporary) / "snapshot"
            ORANGE_CHECKER.extract_archive(
                tar_with_member("compiler/Cargo.toml"), destination
            )
            self.assertEqual(
                (destination / "compiler" / "Cargo.toml").read_text(
                    encoding="utf-8"
                ),
                "evidence\n",
            )

    def test_rejects_parent_traversal_before_writing(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            destination = Path(temporary) / "snapshot"
            with self.assertRaisesRegex(ValueError, "unsafe path"):
                ORANGE_CHECKER.extract_archive(
                    tar_with_member("compiler/../../escaped"), destination
                )
            self.assertFalse((Path(temporary) / "escaped").exists())

    def test_rejects_absolute_path(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            destination = Path(temporary) / "snapshot"
            with self.assertRaisesRegex(ValueError, "unsafe path"):
                ORANGE_CHECKER.extract_archive(
                    tar_with_member("/compiler/Cargo.toml"), destination
                )

    def test_rejects_symbolic_link(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            destination = Path(temporary) / "snapshot"
            with self.assertRaisesRegex(ValueError, "unsupported member type"):
                ORANGE_CHECKER.extract_archive(
                    tar_with_member("compiler/link", kind=tarfile.SYMTYPE),
                    destination,
                )

    def test_rejects_non_sha_revision_without_git(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            ok, error = ORANGE_CHECKER.extract_pinned_source(
                Path(temporary), "main", Path(temporary) / "snapshot"
            )
            self.assertFalse(ok)
            self.assertIn("invalid catalog Orange revision", error)


if __name__ == "__main__":
    unittest.main()
