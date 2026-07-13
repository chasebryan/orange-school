#!/usr/bin/env python3
"""Smoke-check the PRG-102 examples using only the Python standard library."""

from pathlib import Path
import subprocess
import sys
import types

MODULE_ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = MODULE_ROOT / "examples"


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def load_example(filename):
    path = EXAMPLES / filename
    source = path.read_text(encoding="utf-8")
    code = compile(source, str(path), "exec")
    module = types.ModuleType(path.stem)
    module.__file__ = str(path)
    exec(code, module.__dict__)
    return module


def run_example(filename, *arguments):
    return subprocess.run(
        [sys.executable, str(EXAMPLES / filename), *arguments],
        cwd=MODULE_ROOT,
        text=True,
        capture_output=True,
        timeout=5,
        check=False,
    )


def expect_value_error(action, message):
    try:
        action()
    except ValueError:
        return
    raise AssertionError(message)


def check_bounded_scores():
    module = load_example("bounded_scores.py")
    values = [7, 10, 7, 5]
    require(module.find_first(values, 7) == 0, "first search index is wrong")
    require(module.find_first(values, 8) is None, "missing search should return None")
    require(module.count_values(values) == {7: 2, 10: 1, 5: 1}, "counts are wrong")
    require(module.unique_in_order(values) == [7, 10, 5], "stable dedup is wrong")
    require(module.ordered_copy(values) == (5, 7, 7, 10), "ordering is wrong")
    require(values == [7, 10, 7, 5], "ordered_copy changed its input")

    normal = run_example("bounded_scores.py", "7", "7", "10", "7", "5")
    require(normal.returncode == 0, f"score example failed: {normal.stderr}")
    require("first target index: 0" in normal.stdout, "search output is missing")
    require("target count: 2" in normal.stdout, "count output is missing")
    require(normal.stderr == "", "valid score run wrote a diagnostic")

    boundary_arguments = ["100", *(["100"] * module.MAX_ITEMS)]
    boundary = run_example("bounded_scores.py", *boundary_arguments)
    require(boundary.returncode == 0, "maximum-size score input should succeed")
    require("target count: 100" in boundary.stdout, "maximum-size count is wrong")

    too_many = run_example(
        "bounded_scores.py", "0", *(["0"] * (module.MAX_ITEMS + 1))
    )
    require(too_many.returncode != 0, "oversized score input should fail")
    require("supply from 1 through" in too_many.stderr, "bound diagnostic is missing")


def check_inventory_lookup():
    module = load_example("inventory_lookup.py")
    require(module.parse_entry("orange=3") == ("orange", 3), "entry tuple is wrong")
    inventory = module.build_inventory(["orange=3", "book=0"])
    require(inventory == {"orange": 3, "book": 0}, "inventory mapping is wrong")
    expect_value_error(
        lambda: module.build_inventory(["orange=1", "orange=2"]),
        "duplicate names should fail",
    )

    normal = run_example("inventory_lookup.py", "orange=3", "book=0")
    require(normal.returncode == 0, f"inventory example failed: {normal.stderr}")
    require("total units: 3" in normal.stdout, "inventory total is missing")
    require("names ordered: book, orange" in normal.stdout, "ordered names are wrong")
    require("out of stock: book" in normal.stdout, "out-of-stock set is wrong")

    invalid = run_example("inventory_lookup.py", "Orange=3")
    require(invalid.returncode != 0, "invalid name should fail")
    require("invalid item name" in invalid.stderr, "name diagnostic is missing")


def main():
    check_bounded_scores()
    check_inventory_lookup()
    print("prg-102 lab smoke: PASS")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as error:
        print(f"prg-102 lab smoke: FAIL: {error}", file=sys.stderr)
        raise SystemExit(1)
