#!/usr/bin/env python3
"""Smoke-check the bounded Pebble teaching frontend."""

from __future__ import annotations

import ast
import os
import subprocess
import sys
import tempfile
from pathlib import Path


sys.dont_write_bytecode = True
MODULE_ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = MODULE_ROOT / "examples"
sys.path.insert(0, str(EXAMPLES))

from frontend import (  # noqa: E402
    MAX_AST_NODES,
    MAX_DIAGNOSTICS,
    MAX_IDENTIFIER_BYTES,
    MAX_INTEGER_DIGITS,
    MAX_NESTING,
    MAX_SOURCE_BYTES,
    MAX_TOKENS,
    Binary,
    ast_shape,
    lex,
    parse_source,
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def require_error(error_type: type[BaseException], action, message: str) -> None:
    try:
        action()
    except error_type:
        return
    raise AssertionError(message)


def parse_ok(source: str):
    result = parse_source(source)
    require(result.diagnostics == (), f"unexpected diagnostics: {result.diagnostics!r}")
    require(result.program is not None, "valid source did not produce a program")
    return result


def check_tokens_positions_and_precedence() -> None:
    source = "let n = 2 + 3 * 4;\nemit n;"
    result = parse_ok(source)
    require(result.tokens[0].kind == "LET", "keyword token changed")
    require(result.tokens[1].kind == "IDENTIFIER", "identifier token changed")
    require(result.tokens[-1].kind == "EOF", "EOF token is missing")
    require(
        ast_shape(result.program)
        == (
            "program",
            (
                ("let", "n", ("+", ("integer", "2"), ("*", ("integer", "3"), ("integer", "4")))),
                ("emit", ("name", "n")),
            ),
        ),
        "precedence shape changed",
    )

    unicode_result = parse_source("emit 1;\nλ")
    require(unicode_result.program is None, "non-ASCII spelling produced an AST")
    diagnostic = unicode_result.diagnostics[0]
    require(diagnostic.code == "L005", "invalid-character code changed")
    require(diagnostic.span.byte_start == 8, "UTF-8 byte offset changed")
    require((diagnostic.span.line_start, diagnostic.span.column_start) == (2, 1), "line/column changed")
    require(diagnostic.span.byte_end == 10, "multibyte byte endpoint changed")


def check_bounds_and_invalid_inputs() -> None:
    require_error(TypeError, lambda: parse_source(b"emit 1;"), "bytes source was accepted")
    oversized = parse_source(" " * (MAX_SOURCE_BYTES + 1))
    require(oversized.diagnostics[0].code == "L001", "source byte cap was not enforced")
    exact_source = "emit 1;" + " " * (MAX_SOURCE_BYTES - len("emit 1;"))
    require(parse_ok(exact_source).program is not None, "source byte endpoint failed")

    identifier = "a" * MAX_IDENTIFIER_BYTES
    require(parse_ok(f"let {identifier} = 1;").program is not None, "identifier endpoint failed")
    too_long_identifier = parse_source(f"let {identifier}a = 1;")
    require(too_long_identifier.diagnostics[0].code == "L003", "identifier cap was not enforced")
    hostile_identifier = parse_source("a" * MAX_SOURCE_BYTES)
    require(hostile_identifier.diagnostics[0].code == "L003", "hostile identifier diagnostic changed")
    require(
        all(len(token.text) <= MAX_IDENTIFIER_BYTES for token in hostile_identifier.tokens),
        "hostile identifier text was retained",
    )

    digits = "9" * MAX_INTEGER_DIGITS
    require(parse_ok(f"emit {digits};").program is not None, "integer endpoint failed")
    too_many_digits = parse_source(f"emit {digits}9;")
    require(too_many_digits.diagnostics[0].code == "L004", "integer digit cap was not enforced")
    hostile_integer = parse_source("9" * MAX_SOURCE_BYTES)
    require(hostile_integer.diagnostics[0].code == "L004", "hostile integer diagnostic changed")
    require(
        all(len(token.text) <= MAX_INTEGER_DIGITS for token in hostile_integer.tokens),
        "hostile integer text was retained",
    )
    huge_source = parse_source("a" * (MAX_SOURCE_BYTES * 100))
    require(huge_source.diagnostics[0].code == "L001", "huge source did not fail at the source cap")

    nested = "(" * MAX_NESTING + "1" + ")" * MAX_NESTING
    require(parse_ok(f"emit {nested};").program is not None, "nesting endpoint failed")
    too_deep = parse_source(f"emit ({nested});")
    require(too_deep.diagnostics[0].code == "P004", "nesting cap was not enforced")

    token_endpoint = "1+" * 255 + "1;"
    endpoint_tokens, endpoint_diagnostics = lex(token_endpoint)
    require(endpoint_diagnostics == (), "token endpoint was rejected")
    require(len(endpoint_tokens) == MAX_TOKENS + 1, "token endpoint count changed")
    over_tokens, over_diagnostics = lex("1+" * 256 + "1;")
    require(over_diagnostics[0].code == "L002", "token cap was not enforced")
    require(len(over_tokens) == MAX_TOKENS + 1, "bounded token retention changed")

    missing_expression = parse_source("emit ;")
    require(missing_expression.program is None, "invalid expression produced an AST")
    require(missing_expression.diagnostics[0].code == "P005", "expression diagnostic changed")
    recovered = parse_source("let = 1; emit ; let good = 2;")
    require(recovered.program is None, "recovery returned a partial AST")
    require([item.code for item in recovered.diagnostics] == ["P001", "P005"], "recovery diagnostics changed")
    require(len(recovered.diagnostics) <= MAX_DIAGNOSTICS, "diagnostic cap was exceeded")

    missing_close = parse_source("emit (1 + 2;")
    require(missing_close.diagnostics[0].code == "P001", "missing delimiter diagnostic changed")
    require(missing_close.diagnostics[0].message == "expected ')' to close expression", "diagnostic text changed")

    node_endpoint_expression = "+".join("1" for _ in range(128))
    node_endpoint = parse_ok(f"emit {node_endpoint_expression};")
    require(node_endpoint.program is not None, "AST node endpoint failed")
    node_overflow_expression = "+".join("1" for _ in range(129))
    node_overflow = parse_source(f"emit {node_overflow_expression};")
    require(node_overflow.program is None, "AST node overflow produced a program")
    require(node_overflow.diagnostics[0].code == "P002", "AST node cap was not enforced")
    require(MAX_AST_NODES == 256, "documented AST node cap changed")

    capped_diagnostics = parse_source("λ" * (MAX_DIAGNOSTICS + 3))
    require(len(capped_diagnostics.diagnostics) == MAX_DIAGNOSTICS, "lexer diagnostic cap changed")


def _python_expression_shape(node: ast.AST) -> object:
    if isinstance(node, ast.Constant) and type(node.value) is int:
        return ("integer", str(node.value))
    if isinstance(node, ast.Name):
        return ("name", node.id)
    if isinstance(node, ast.BinOp):
        operators = {ast.Add: "+", ast.Sub: "-", ast.Mult: "*", ast.Div: "/"}
        operator = operators[type(node.op)]
        return (operator, _python_expression_shape(node.left), _python_expression_shape(node.right))
    raise AssertionError(f"unexpected Python AST node: {type(node).__name__}")


def check_metamorphic_and_differential_cases() -> None:
    compact = parse_ok("emit 1+2*3-4/2;")
    spaced = parse_ok("\n\t emit ( 1 + 2 * 3 ) - 4 / 2 ; \n")
    compact_expression = compact.program.statements[0].expression
    spaced_expression = spaced.program.statements[0].expression
    require(ast_shape(compact_expression) == ast_shape(spaced_expression), "whitespace/parentheses metamorphism failed")

    reference = ast.parse("1+2*3-4/2", mode="eval")
    require(
        ast_shape(compact_expression) == _python_expression_shape(reference.body),
        "independent Python precedence comparison failed",
    )
    require(isinstance(compact_expression, Binary), "comparison expression was not binary")


def check_worked_program_and_failure_sensitivity() -> None:
    environment = dict(os.environ)
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    with tempfile.TemporaryDirectory(prefix="plt-101-smoke-") as temporary_value:
        temporary = Path(temporary_value)
        worked = subprocess.run(
            [sys.executable, "-B", str(EXAMPLES / "frontend_worked.py")],
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
        require("tokens: 13\n" in worked.stdout, "worked token count changed")
        require("('integer', '3'), ('integer', '4')" in worked.stdout, "worked AST is missing")

        deliberate = temporary / "deliberate_failure.py"
        deliberate.write_text(
            f"import sys\nsys.path.insert(0, {str(EXAMPLES)!r})\n"
            "from frontend import ast_shape, parse_source\n"
            "result = parse_source('emit 1 + 2 * 3;')\n"
            "assert ast_shape(result.program.statements[0].expression)[0] == '*', "
            "'intentionally wrong precedence root'\n",
            encoding="utf-8",
        )
        failed = subprocess.run(
            [sys.executable, "-B", str(deliberate)],
            cwd=temporary,
            env=environment,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=8,
            check=False,
        )
        require(failed.returncode != 0, "deliberately wrong precedence expectation passed")
        require(failed.stdout == "", "deliberate failure wrote stdout")
        require("AssertionError" in failed.stderr, "deliberate failure was not observable")

        deliberate.write_text(
            f"import sys\nsys.path.insert(0, {str(EXAMPLES)!r})\n"
            "from frontend import ast_shape, parse_source\n"
            "result = parse_source('emit 1 + 2 * 3;')\n"
            "assert ast_shape(result.program.statements[0].expression)[0] == '+'\n"
            "print('deliberate recovery: PASS')\n",
            encoding="utf-8",
        )
        passed = subprocess.run(
            [sys.executable, "-B", str(deliberate)],
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
    check_tokens_positions_and_precedence()
    check_bounds_and_invalid_inputs()
    check_metamorphic_and_differential_cases()
    check_worked_program_and_failure_sensitivity()
    print("plt-101 lab smoke: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
