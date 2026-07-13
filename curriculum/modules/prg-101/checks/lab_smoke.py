#!/usr/bin/env python3
"""Smoke-check the PRG-101 examples using only the Python standard library."""

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


def check_reading_goal():
    module = load_example("reading_goal.py")
    require(
        module.analyze_readings(10, [8, 10, 12]) == (30, 2),
        "reading analysis returned the wrong state",
    )
    require(
        "goal met every day: yes" in module.format_report(1, [1]),
        "boundary report should meet the goal",
    )

    normal = run_example("reading_goal.py", "10", "8", "10", "12")
    require(normal.returncode == 0, f"normal reading run failed: {normal.stderr}")
    require("total pages: 30" in normal.stdout, "normal total is missing")
    require("days meeting goal: 2" in normal.stdout, "normal count is missing")
    require(normal.stderr == "", "normal run wrote a diagnostic")

    boundary = run_example("reading_goal.py", "1", "0")
    require(boundary.returncode == 0, "boundary reading run should succeed")
    require("goal met every day: no" in boundary.stdout, "boundary branch is wrong")

    invalid = run_example("reading_goal.py", "ten", "4")
    require(invalid.returncode != 0, "invalid goal should fail")
    require(invalid.stdout == "", "invalid goal should not print a report")
    require("goal must be an integer" in invalid.stderr, "invalid diagnostic is missing")


def check_temperature_advice():
    module = load_example("temperature_advice.py")
    expected = {
        -100: "freezing",
        0: "freezing",
        1: "cool",
        19: "cool",
        20: "comfortable",
        29: "comfortable",
        30: "hot",
        100: "hot",
    }
    for value, label in expected.items():
        require(
            module.classify_temperature(value) == label,
            f"temperature {value} should be {label}",
        )

    normal = run_example("temperature_advice.py", "20")
    require(normal.returncode == 0, f"temperature run failed: {normal.stderr}")
    require(normal.stdout == "20 C: comfortable\n", "temperature output changed")

    invalid = run_example("temperature_advice.py", "101")
    require(invalid.returncode != 0, "out-of-range temperature should fail")
    require("temperature must be" in invalid.stderr, "range diagnostic is missing")


def main():
    check_reading_goal()
    check_temperature_advice()
    print("prg-101 lab smoke: PASS")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as error:
        print(f"prg-101 lab smoke: FAIL: {error}", file=sys.stderr)
        raise SystemExit(1)
