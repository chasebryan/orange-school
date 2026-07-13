from __future__ import annotations

import ast
import json
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def released_material_directories() -> list[Path]:
    catalog = json.loads((ROOT / "curriculum" / "catalog.json").read_text(encoding="utf-8"))
    return [
        ROOT / module["material"]
        for module in catalog["modules"]
        if module.get("status") == "released" and "material" in module
    ]


class HostSourceCompatibilityTests(unittest.TestCase):
    def test_python_sources_parse_as_python_3_11(self) -> None:
        paths = [
            path
            for material in released_material_directories()
            for path in material.rglob("*.py")
        ]
        self.assertTrue(paths, "expected released Python source")
        for path in paths:
            with self.subTest(path=path.relative_to(ROOT)):
                ast.parse(
                    path.read_text(encoding="utf-8"),
                    filename=str(path),
                    feature_version=(3, 11),
                )

    def test_bash_sources_pass_syntax_check(self) -> None:
        paths = [
            path
            for material in released_material_directories()
            for path in material.rglob("*.sh")
        ]
        self.assertTrue(paths, "expected released Bash source")
        for path in paths:
            with self.subTest(path=path.relative_to(ROOT)):
                result = subprocess.run(
                    ["bash", "-n", str(path)],
                    text=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    check=False,
                )
                self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()
