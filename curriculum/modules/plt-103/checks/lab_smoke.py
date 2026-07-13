#!/usr/bin/env python3
"""Smoke-check the bounded Cairn typed IR and artifact pipeline."""

from __future__ import annotations

from dataclasses import replace
import os
from pathlib import Path
import struct
import subprocess
import sys
import tempfile


sys.dont_write_bytecode = True
MODULE_ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = MODULE_ROOT / "examples"
sys.path.insert(0, str(EXAMPLES))

from ir_pipeline import (  # noqa: E402
    BOOL,
    I32,
    I32_MAX,
    I32_MIN,
    INSTRUCTION_SIZE,
    MAX_ARTIFACT_BYTES,
    MAX_AST_DEPTH,
    MAX_BINDINGS,
    MAX_IR_INSTRUCTIONS,
    MAX_NAME_BYTES,
    MAX_SOURCE_NODES,
    Add,
    BoolLiteral,
    Choose,
    Instruction,
    IntLiteral,
    Less,
    Let,
    Name,
    PipelineError,
    Program,
    TypedValue,
    compile_artifact,
    decode,
    encode,
    evaluate_source,
    execute_ir,
    lower,
    validate_ir,
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def require_error(code: str, action, message: str) -> PipelineError:
    try:
        action()
    except PipelineError as error:
        require(error.diagnostic.code == code, f"{message}: got {error.diagnostic!r}")
        return error
    raise AssertionError(message)


def balanced_add(leaves: int) -> object:
    require(leaves >= 1 and leaves & (leaves - 1) == 0, "balanced_add needs a power of two")
    layer: list[object] = [IntLiteral(1) for _ in range(leaves)]
    while len(layer) > 1:
        layer = [Add(layer[index], layer[index + 1]) for index in range(0, len(layer), 2)]
    return layer[0]


def nested_add(depth: int) -> object:
    expression: object = IntLiteral(1)
    for _ in range(depth - 1):
        expression = Add(expression, IntLiteral(1))
    return expression


def nested_lets(count: int) -> object:
    expression: object = IntLiteral(99)
    for index in reversed(range(count)):
        expression = Let(f"x{index}", IntLiteral(index), expression)
    return expression


def check_normal_lowering_and_shadowing() -> None:
    expression = Let(
        "x",
        Add(IntLiteral(20), IntLiteral(1)),
        Choose(Less(Name("x"), IntLiteral(22)), Add(Name("x"), Name("x")), IntLiteral(0)),
    )
    reference = evaluate_source(expression)
    program = lower(expression)
    artifact = encode(program)
    require(reference == TypedValue(I32, 42), "source reference result changed")
    require(execute_ir(program) == reference, "source and IR disagree")
    require(execute_ir(decode(artifact)) == reference, "artifact round trip changed the result")
    require(
        [instruction.opcode for instruction in program.instructions]
        == ["const_i32", "const_i32", "add_i32", "const_i32", "less_i32", "add_i32", "const_i32", "select"],
        "deterministic lowering order changed",
    )
    require([item.destination for item in program.instructions] == list(range(8)), "SSA destinations changed")

    shadowed = Let("x", IntLiteral(1), Let("x", IntLiteral(2), Add(Name("x"), IntLiteral(3))))
    renamed = Let("a", IntLiteral(1), Let("b", IntLiteral(2), Add(Name("b"), IntLiteral(3))))
    require(evaluate_source(shadowed) == TypedValue(I32, 5), "lexical shadowing changed")
    require(compile_artifact(shadowed) == compile_artifact(renamed), "alpha-renaming changed closed artifact")


def check_source_and_instruction_bounds() -> None:
    require(evaluate_source(IntLiteral(I32_MIN)) == TypedValue(I32, I32_MIN), "i32 minimum failed")
    require(evaluate_source(IntLiteral(I32_MAX)) == TypedValue(I32, I32_MAX), "i32 maximum failed")
    require_error("S005", lambda: lower(IntLiteral(I32_MIN - 1)), "i32 lower one-beyond passed")
    require_error("S005", lambda: lower(IntLiteral(I32_MAX + 1)), "i32 upper one-beyond passed")

    endpoint = balanced_add(32)
    endpoint_program = lower(endpoint)
    endpoint_artifact = encode(endpoint_program)
    require(len(endpoint_program.instructions) == MAX_IR_INSTRUCTIONS == 63, "instruction endpoint changed")
    require(MAX_SOURCE_NODES == 63, "source-node endpoint changed")
    require(len(endpoint_artifact) == MAX_ARTIFACT_BYTES, "artifact byte endpoint changed")
    require(execute_ir(decode(endpoint_artifact)) == TypedValue(I32, 32), "endpoint artifact changed")
    require_error("S002", lambda: lower(balanced_add(64)), "first representable node count above 63 passed")

    depth_endpoint = nested_add(MAX_AST_DEPTH)
    require(evaluate_source(depth_endpoint) == TypedValue(I32, MAX_AST_DEPTH), "depth endpoint failed")
    require_error("S003", lambda: lower(nested_add(MAX_AST_DEPTH + 1)), "depth one-beyond passed")

    require(evaluate_source(nested_lets(MAX_BINDINGS)) == TypedValue(I32, 99), "binding endpoint failed")
    require_error("S006", lambda: lower(nested_lets(MAX_BINDINGS + 1)), "binding one-beyond passed")

    name = "n" * MAX_NAME_BYTES
    require(evaluate_source(Let(name, IntLiteral(1), Name(name))) == TypedValue(I32, 1), "name endpoint failed")
    require_error(
        "S004",
        lambda: lower(Let(name + "n", IntLiteral(1), Name(name + "n"))),
        "name byte one-beyond passed",
    )

    too_many = tuple(
        Instruction("const_i32", I32, index, immediate=index)
        for index in range(MAX_IR_INSTRUCTIONS + 1)
    )
    require_error(
        "I001",
        lambda: validate_ir(Program(too_many, MAX_IR_INSTRUCTIONS, I32)),
        "IR count one-beyond passed",
    )


def check_type_runtime_and_ir_failures() -> None:
    cases = (
        ("T001", Name("missing")),
        ("T002", Add(BoolLiteral(True), IntLiteral(1))),
        ("T003", Less(IntLiteral(1), BoolLiteral(False))),
        ("T004", Choose(IntLiteral(1), IntLiteral(2), IntLiteral(3))),
        ("T005", Choose(BoolLiteral(True), IntLiteral(2), BoolLiteral(False))),
    )
    for code, expression in cases:
        require_error(code, lambda expression=expression: lower(expression), f"{code} source failure passed")
    require_error(
        "R001",
        lambda: evaluate_source(Add(IntLiteral(I32_MAX), IntLiteral(1))),
        "source overflow passed",
    )
    overflow_program = lower(Add(IntLiteral(I32_MAX), IntLiteral(1)))
    require_error("R001", lambda: execute_ir(overflow_program), "IR overflow passed")

    valid = lower(Add(IntLiteral(1), IntLiteral(2)))
    records = list(valid.instructions)
    records[2] = replace(records[2], argument_1=2)
    require_error(
        "I004",
        lambda: validate_ir(Program(tuple(records), valid.result_register, valid.result_type)),
        "forward/self use passed",
    )
    records = list(valid.instructions)
    records[1] = replace(records[1], destination=0)
    require_error(
        "I003",
        lambda: validate_ir(Program(tuple(records), valid.result_register, valid.result_type)),
        "duplicate destination passed",
    )
    records = list(valid.instructions)
    records[0] = replace(records[0], destination=False)
    require_error(
        "I003",
        lambda: validate_ir(Program(tuple(records), valid.result_register, valid.result_type)),
        "Boolean destination passed as integer zero",
    )
    require_error(
        "I007",
        lambda: validate_ir(replace(valid, result_type=BOOL)),
        "mismatched result type passed",
    )


def check_equivalence_table() -> None:
    expressions: list[object] = []
    for left in (-7, -1, 0, 1, 9, 100):
        for right in (-3, 0, 4, 11, 23, 101):
            expressions.append(
                Let(
                    "lhs",
                    IntLiteral(left),
                    Let(
                        "rhs",
                        IntLiteral(right),
                        Choose(
                            Less(Name("lhs"), Name("rhs")),
                            Add(Name("lhs"), Name("rhs")),
                            Name("lhs"),
                        ),
                    ),
                )
            )
    require(len(expressions) == 36, "fixed equivalence table changed")
    for expression in expressions:
        reference = evaluate_source(expression)
        program = lower(expression)
        require(execute_ir(program) == reference, "source/IR table disagreement")
        artifact = encode(program)
        require(encode(decode(artifact)) == artifact, "artifact encoding is not canonical")
        require(execute_ir(decode(artifact)) == reference, "decoded table disagreement")


def check_artifact_rejections() -> None:
    artifact = encode(lower(Add(IntLiteral(1), IntLiteral(2))))
    require_error("A001", lambda: decode(bytearray(artifact)), "mutable artifact passed")
    require_error("A002", lambda: decode(artifact[:11]), "short header passed")
    require_error("A003", lambda: decode(b"NOPE" + artifact[4:]), "bad magic passed")
    require_error("A003", lambda: decode(artifact[:4] + b"\x02" + artifact[5:]), "bad version passed")
    require_error("A004", lambda: decode(artifact[:5] + b"\x01" + artifact[6:]), "header flags passed")
    require_error("A006", lambda: decode(artifact[:-1]), "truncated record passed")
    require_error("A006", lambda: decode(artifact + b"\x00"), "trailing byte passed")

    over_count = bytearray(artifact)
    struct.pack_into(">H", over_count, 6, MAX_IR_INSTRUCTIONS + 1)
    require_error("A005", lambda: decode(bytes(over_count)), "artifact count one-beyond passed")

    forward = bytearray(artifact)
    # Third record is add_i32; its first operand field starts four bytes into the record.
    struct.pack_into(">H", forward, 12 + 2 * INSTRUCTION_SIZE + 4, 2)
    require_error("I004", lambda: decode(bytes(forward)), "artifact forward use passed")

    unused_immediate = bytearray(artifact)
    struct.pack_into(">i", unused_immediate, 12 + 2 * INSTRUCTION_SIZE + 10, 7)
    require_error("A004", lambda: decode(bytes(unused_immediate)), "noncanonical unused field passed")


def check_worked_and_deliberate_failure() -> None:
    environment = dict(os.environ)
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    with tempfile.TemporaryDirectory(prefix="plt-103-smoke-") as temporary_value:
        temporary = Path(temporary_value)
        worked = subprocess.run(
            [sys.executable, "-B", str(EXAMPLES / "ir_worked.py")],
            cwd=temporary,
            env=environment,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=8,
            check=False,
        )
        require(worked.returncode == 0, f"worked example failed: {worked.stderr}")
        require(worked.stderr == "", "worked example wrote stderr")
        require("source: i32 42\n" in worked.stdout, "worked source value changed")
        require("instructions: 8\n" in worked.stdout, "worked instruction count changed")
        require("artifact-bytes: 140\n" in worked.stdout, "worked artifact size changed")
        require("decoded: i32 42\n" in worked.stdout, "worked decoded value changed")

        mutation = temporary / "mutation.py"
        mutation.write_text(
            f"import sys\nsys.path.insert(0, {str(EXAMPLES)!r})\n"
            "from ir_pipeline import Add, IntLiteral, decode, encode, execute_ir, lower\n"
            "artifact = encode(lower(Add(IntLiteral(20), IntLiteral(22))))\n"
            "assert execute_ir(decode(artifact)).value == 41, 'intentionally wrong result'\n",
            encoding="utf-8",
        )
        failed = subprocess.run(
            [sys.executable, "-B", str(mutation)],
            cwd=temporary,
            env=environment,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=8,
            check=False,
        )
        require(failed.returncode != 0, "deliberately wrong equivalence expectation passed")
        require(failed.stdout == "", "deliberate failure wrote stdout")
        require("AssertionError" in failed.stderr, "deliberate failure was not observable")

        mutation.write_text(
            f"import sys\nsys.path.insert(0, {str(EXAMPLES)!r})\n"
            "from ir_pipeline import Add, IntLiteral, decode, encode, execute_ir, lower\n"
            "artifact = encode(lower(Add(IntLiteral(20), IntLiteral(22))))\n"
            "assert execute_ir(decode(artifact)).value == 42\n"
            "print('deliberate recovery: PASS')\n",
            encoding="utf-8",
        )
        passed = subprocess.run(
            [sys.executable, "-B", str(mutation)],
            cwd=temporary,
            env=environment,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=8,
            check=False,
        )
        require(passed.returncode == 0, f"restored expectation failed: {passed.stderr}")
        require(passed.stdout == "deliberate recovery: PASS\n", "recovery output changed")
        require(passed.stderr == "", "recovery wrote stderr")


def main() -> int:
    require(sys.version_info >= (3, 11), "Python 3.11 or newer is required")
    check_normal_lowering_and_shadowing()
    check_source_and_instruction_bounds()
    check_type_runtime_and_ir_failures()
    check_equivalence_table()
    check_artifact_rejections()
    check_worked_and_deliberate_failure()
    print("plt-103 lab smoke: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
