from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "check_host_examples", ROOT / "scripts" / "check_host_examples.py"
)
assert SPEC and SPEC.loader
HOST_CHECKER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(HOST_CHECKER)


class HostCheckerTests(unittest.TestCase):
    def test_parses_git_version(self) -> None:
        self.assertEqual(HOST_CHECKER.parse_version("git version 2.43.7\n"), (2, 43))

    def test_parses_bash_version(self) -> None:
        output = "GNU bash, version 5.2.26(1)-release (x86_64-pc-linux-gnu)\n"
        self.assertEqual(HOST_CHECKER.parse_version(output), (5, 2))

    def test_rejects_text_without_version(self) -> None:
        self.assertEqual(HOST_CHECKER.parse_version("not available\n"), ())

    def test_local_c17_profile_is_available(self) -> None:
        self.assertTrue(HOST_CHECKER.supports_c17())

    def test_pinned_rust_toolchain_matches(self) -> None:
        self.assertTrue(HOST_CHECKER.rust_toolchain_matches("1.96.1"))


if __name__ == "__main__":
    unittest.main()
