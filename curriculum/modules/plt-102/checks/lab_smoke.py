#!/usr/bin/env python3
"""Smoke-check the bounded Lumen type-and-effect semantics."""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Callable


sys.dont_write_bytecode = True
MODULE_ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = MODULE_ROOT / "examples"
sys.path.insert(0, str(EXAMPLES))

from semantics import (  # noqa: E402
    MAX_AST_DEPTH,
    MAX_AST_NODES,
    MAX_ENV_BINDINGS,
    MAX_INT,
    MAX_NAME_BYTES,
    MAX_OUTPUTS,
    Add,
    BoolLit,
    Effect,
    Emit,
    Eq,
    If,
    IntLit,
    Let,
    SemanticError,
    Seq,
    Sub,
    Type,
    Var,
    run,
    typecheck,
)


class SmokeFailure(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SmokeFailure(message)


def expect_error(
    code: str,
    action: Callable[[], object],
    message: str,
    expected_message: str | None = None,
) -> None:
    try:
        action()
    except SemanticError as error:
        require(error.code == code, f"{message}: got {error.code}: {error.message}")
        if expected_message is not None:
            require(
                error.message == expected_message,
                f"{message}: message changed to {error.message!r}",
            )
        return
    raise SmokeFailure(message)


def balanced_additions(leaves: int):
    if leaves == 1:
        return IntLit(0)
    left_leaves = leaves // 2
    return Add(
        balanced_additions(left_leaves),
        balanced_additions(leaves - left_leaves),
    )


def check_names_types_and_effects() -> None:
    require(typecheck(IntLit(0)).type is Type.INT, "integer type changed")
    require(typecheck(BoolLit(True)).type is Type.BOOL, "boolean type changed")
    require(typecheck(Eq(IntLit(1), IntLit(1))).type is Type.BOOL, "equality type changed")
    require(typecheck(Emit(IntLit(1))).type is Type.UNIT, "emit type changed")
    require(
        typecheck(
            If(BoolLit(True), IntLit(1), Seq(Emit(IntLit(2)), IntLit(2)))
        ).potential_effects
        == frozenset((Effect.EMIT,)),
        "if potential effect must include the untaken emitting branch",
    )
    shadow = Let("x", IntLit(1), Let("x", IntLit(2), Var("x")))
    require(run(shadow).value == 2, "nearest lexical binding did not shadow")
    require(run(Let("x", IntLit(1), Add(Var("x"), IntLit(2)))).value == 3, "name lookup failed")

    expect_error(
        "S003",
        lambda: typecheck(Var("missing")),
        "unbound name was accepted",
        "unbound name: missing",
    )
    expect_error(
        "S008",
        lambda: typecheck(BoolLit(1)),
        "malformed Boolean field was accepted",
        "boolean literal must be an exact boolean",
    )
    expect_error(
        "S002",
        lambda: typecheck(Var(1)),
        "malformed variable-name field was accepted",
        "binding name must be an exact string",
    )
    expect_error("S009", lambda: typecheck(Add(BoolLit(True), IntLit(1))), "bad addition typed")
    expect_error("S010", lambda: typecheck(Eq(IntLit(1), BoolLit(True))), "mixed equality typed")
    expect_error("S011", lambda: typecheck(If(IntLit(1), IntLit(2), IntLit(3))), "bad condition typed")
    expect_error("S012", lambda: typecheck(If(BoolLit(True), IntLit(1), BoolLit(False))), "mixed branches typed")
    expect_error("S014", lambda: typecheck(Emit(BoolLit(False))), "bad emit typed")
    expect_error("S015", lambda: typecheck(Seq(IntLit(1), IntLit(2))), "bad sequence typed")


def check_order_choice_and_runtime_failures() -> None:
    program = Let(
        "n",
        IntLit(5),
        Seq(
            Emit(Var("n")),
            Seq(Emit(Add(Var("n"), IntLit(1))), Sub(IntLit(10), Var("n"))),
        ),
    )
    result = run(program)
    require(result.type is Type.INT, "program result type changed")
    require(result.value == 5, "program result value changed")
    require(result.outputs == (5, 6), "left-to-right output order changed")
    require(result.potential_effects == frozenset((Effect.EMIT,)), "effect set changed")

    untaken = run(If(BoolLit(False), Emit(IntLit(9)), Emit(IntLit(7))))
    require(untaken.outputs == (7,), "evaluator executed both branches")
    require(untaken.potential_effects == frozenset((Effect.EMIT,)), "potential effect missing")
    expect_error(
        "R002",
        lambda: run(Add(IntLit(MAX_INT), IntLit(1))),
        "overflow was accepted",
        "arithmetic result is outside -1000000..1000000",
    )
    expect_error(
        "R001",
        lambda: run(Add(IntLit(1), IntLit(2)), step_budget=2),
        "step cap was ignored",
        "evaluation step budget exhausted",
    )
    expect_error(
        "R004",
        lambda: run(Seq(Emit(IntLit(1)), Emit(IntLit(2))), output_budget=1),
        "output cap was ignored",
    )
    expect_error("R005", lambda: run(IntLit(1), step_budget=True), "Boolean budget was accepted")


def check_endpoints_and_invalid_ast() -> None:
    require(run(IntLit(-MAX_INT)).value == -MAX_INT, "minimum integer failed")
    require(run(IntLit(MAX_INT)).value == MAX_INT, "maximum integer failed")
    expect_error("S007", lambda: typecheck(IntLit(MAX_INT + 1)), "large literal was accepted")
    expect_error("S007", lambda: typecheck(IntLit(True)), "Boolean integer literal was accepted")
    require(run(Let("x" * MAX_NAME_BYTES, IntLit(1), Var("x" * MAX_NAME_BYTES))).value == 1, "name endpoint failed")
    expect_error(
        "S002",
        lambda: typecheck(Let("x" * (MAX_NAME_BYTES + 1), IntLit(1), IntLit(2))),
        "overlong name was accepted",
    )
    expect_error("S002", lambda: typecheck(Var("é")), "non-ASCII name was accepted")
    expect_error(
        "S002",
        lambda: typecheck(Var("x" * (MAX_NAME_BYTES * 100_000))),
        "hostile overlong name was accepted",
    )
    expect_error("S001", lambda: typecheck(1), "host integer was accepted as AST")

    depth_endpoint = IntLit(0)
    for _ in range(MAX_AST_DEPTH - 1):
        depth_endpoint = Add(depth_endpoint, IntLit(0))
    # The left spine is exactly 32 nodes deep without consuming environment capacity.
    require(typecheck(depth_endpoint).type is Type.INT, "depth endpoint failed")
    too_deep = Add(depth_endpoint, IntLit(0))
    expect_error("S004", lambda: typecheck(too_deep), "depth one-beyond was accepted")

    # A full tree with 128 leaves has 255 nodes; Emit makes the 256-node endpoint.
    node_endpoint = Emit(balanced_additions(128))
    require(typecheck(node_endpoint).visited_nodes == MAX_AST_NODES, "node endpoint count changed")
    expect_error(
        "S005",
        lambda: typecheck(Let("x", IntLit(0), balanced_additions(128))),
        "node one-beyond was accepted",
    )
    require(run(node_endpoint, step_budget=MAX_AST_NODES).steps == MAX_AST_NODES, "step endpoint failed")
    expect_error(
        "R001",
        lambda: run(node_endpoint, step_budget=MAX_AST_NODES - 1),
        "step one-beyond was accepted",
    )

    environment_endpoint = Var("x")
    for _ in range(MAX_ENV_BINDINGS):
        environment_endpoint = Let("x", IntLit(0), environment_endpoint)
    require(run(environment_endpoint).value == 0, "environment endpoint failed")
    environment_too_large = Let("x", IntLit(0), environment_endpoint)
    expect_error("S013", lambda: typecheck(environment_too_large), "environment one-beyond was accepted")

    cyclic = Add(IntLit(1), IntLit(2))
    object.__setattr__(cyclic, "left", cyclic)
    expect_error("S006", lambda: typecheck(cyclic), "cycle was accepted")

    # A flat sequence would hit the teaching depth first, so use a balanced
    # constructor to isolate the output budget.
    def balanced_emit(values: list[int]):
        if len(values) == 1:
            return Emit(IntLit(values[0]))
        middle = len(values) // 2
        left = balanced_emit(values[:middle])
        right = balanced_emit(values[middle:])
        return Seq(left, right)

    endpoint = run(balanced_emit(list(range(MAX_OUTPUTS))))
    require(len(endpoint.outputs) == MAX_OUTPUTS, "output endpoint failed")
    expect_error(
        "R004",
        lambda: run(balanced_emit(list(range(MAX_OUTPUTS))), output_budget=MAX_OUTPUTS - 1),
        "output budget one-beyond was accepted",
    )


def check_worked_and_deliberate_failure() -> None:
    environment = dict(os.environ)
    environment.update({"PYTHONDONTWRITEBYTECODE": "1", "PYTHONHASHSEED": "0"})
    with tempfile.TemporaryDirectory(prefix="plt-102-smoke-") as temporary_value:
        temporary = Path(temporary_value)
        worked = subprocess.run(
            [sys.executable, "-B", str(EXAMPLES / "semantics_worked.py")],
            cwd=temporary,
            env=environment,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=8,
            check=False,
        )
        expected = (
            "type: Int\n"
            "potential effects: emit\n"
            "value: 22\n"
            "outputs: (21,)\n"
            "steps: 12\n"
        )
        require(worked.returncode == 0, f"worked example failed: {worked.stderr}")
        require(worked.stdout == expected, f"worked output changed: {worked.stdout!r}")
        require(worked.stderr == "", "worked example wrote stderr")

        probe = temporary / "probe.py"
        prefix = f"import sys; sys.path.insert(0, {str(EXAMPLES)!r})\n"
        probe.write_text(
            prefix
            + "from semantics import Add, IntLit, run\n"
            + "assert run(Add(IntLit(2), IntLit(3))).value == 6, 'deliberately wrong value'\n",
            encoding="utf-8",
        )
        failed = subprocess.run(
            [sys.executable, "-B", str(probe)], cwd=temporary, env=environment,
            text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=8, check=False,
        )
        require(failed.returncode != 0, "wrong semantic expectation did not fail")
        require("AssertionError" in failed.stderr, "deliberate failure was not observable")

        probe.write_text(
            prefix
            + "from semantics import Add, IntLit, run\n"
            + "assert run(Add(IntLit(2), IntLit(3))).value == 5\n"
            + "print('deliberate recovery: PASS')\n",
            encoding="utf-8",
        )
        recovered = subprocess.run(
            [sys.executable, "-B", str(probe)], cwd=temporary, env=environment,
            text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=8, check=False,
        )
        require(recovered.returncode == 0, "corrected semantic expectation did not pass")
        require(recovered.stdout == "deliberate recovery: PASS\n", "corrected output changed")
        require(recovered.stderr == "", "corrected probe wrote stderr")
        require(not any(temporary.rglob("__pycache__")), "smoke created a Python cache")


def main() -> int:
    check_names_types_and_effects()
    check_order_choice_and_runtime_failures()
    check_endpoints_and_invalid_ast()
    check_worked_and_deliberate_failure()
    print("plt-102 lab smoke: PASS")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, SmokeFailure, subprocess.SubprocessError) as error:
        print(f"plt-102 lab smoke: FAIL: {error}", file=sys.stderr)
        raise SystemExit(1)
