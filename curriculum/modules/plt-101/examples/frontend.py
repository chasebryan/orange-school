"""A bounded frontend for the deliberately small Pebble teaching language.

Pebble is independent courseware.  Its syntax and diagnostics do not specify,
predict, or emulate Orange.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TypeAlias


MAX_SOURCE_BYTES = 4096
MAX_TOKENS = 512
MAX_AST_NODES = 256
MAX_NESTING = 32
MAX_DIAGNOSTICS = 8
MAX_IDENTIFIER_BYTES = 32
MAX_INTEGER_DIGITS = 10


@dataclass(frozen=True, slots=True)
class Span:
    byte_start: int
    byte_end: int
    line_start: int
    column_start: int
    line_end: int
    column_end: int


@dataclass(frozen=True, slots=True)
class Diagnostic:
    code: str
    message: str
    span: Span


@dataclass(frozen=True, slots=True)
class Token:
    kind: str
    text: str
    span: Span


@dataclass(frozen=True, slots=True)
class Integer:
    text: str
    span: Span


@dataclass(frozen=True, slots=True)
class Name:
    text: str
    span: Span


@dataclass(frozen=True, slots=True)
class Binary:
    operator: str
    left: "Expression"
    right: "Expression"
    span: Span


Expression: TypeAlias = Integer | Name | Binary


@dataclass(frozen=True, slots=True)
class LetStatement:
    name: str
    name_span: Span
    expression: Expression
    span: Span


@dataclass(frozen=True, slots=True)
class EmitStatement:
    expression: Expression
    span: Span


Statement: TypeAlias = LetStatement | EmitStatement


@dataclass(frozen=True, slots=True)
class Program:
    statements: tuple[Statement, ...]


@dataclass(frozen=True, slots=True)
class FrontendResult:
    tokens: tuple[Token, ...]
    program: Program | None
    diagnostics: tuple[Diagnostic, ...]


def _plain_str(value: object, label: str) -> str:
    if type(value) is not str:
        raise TypeError(f"{label} must be str")
    return value


def _bounded_utf8_size(source: str) -> int | None:
    """Count UTF-8 bytes without allocating an encoding larger than the cap."""
    size = 0
    for character in source:
        size += len(character.encode("utf-8", errors="strict"))
        if size > MAX_SOURCE_BYTES:
            return None
    return size


def _point(byte_offset: int, line: int, column: int) -> Span:
    return Span(byte_offset, byte_offset, line, column, line, column)


def _join_spans(first: Span, last: Span) -> Span:
    return Span(
        first.byte_start,
        last.byte_end,
        first.line_start,
        first.column_start,
        last.line_end,
        last.column_end,
    )


def lex(source: str) -> tuple[tuple[Token, ...], tuple[Diagnostic, ...]]:
    """Tokenize bounded UTF-8 source using ASCII-only Pebble spellings."""

    source = _plain_str(source, "source")
    try:
        encoded_size = _bounded_utf8_size(source)
    except UnicodeEncodeError:
        span = _point(0, 1, 1)
        return (), (Diagnostic("L000", "source cannot be encoded as strict UTF-8", span),)
    if encoded_size is None:
        span = _point(0, 1, 1)
        return (), (
            Diagnostic(
                "L001",
                f"source exceeds {MAX_SOURCE_BYTES} UTF-8 bytes",
                span,
            ),
        )

    tokens: list[Token] = []
    diagnostics: list[Diagnostic] = []
    index = 0
    byte_offset = 0
    line = 1
    column = 1

    def advance() -> str:
        nonlocal index, byte_offset, line, column
        character = source[index]
        index += 1
        byte_offset += len(character.encode("utf-8"))
        if character == "\n":
            line += 1
            column = 1
        else:
            column += 1
        return character

    def emit(kind: str, text: str, start: tuple[int, int, int]) -> None:
        start_byte, start_line, start_column = start
        tokens.append(
            Token(
                kind,
                text,
                Span(start_byte, byte_offset, start_line, start_column, line, column),
            )
        )

    punctuation = {
        "=": "EQUAL",
        "+": "PLUS",
        "-": "MINUS",
        "*": "STAR",
        "/": "SLASH",
        "(": "LPAREN",
        ")": "RPAREN",
        ";": "SEMICOLON",
    }
    keywords = {"let": "LET", "emit": "EMIT"}

    while index < len(source):
        character = source[index]
        if character in " \t\r\n":
            advance()
            continue
        if len(tokens) >= MAX_TOKENS:
            diagnostics.append(
                Diagnostic(
                    "L002",
                    f"token count exceeds {MAX_TOKENS}",
                    _point(byte_offset, line, column),
                )
            )
            break

        start = (byte_offset, line, column)
        if character in punctuation:
            emit(punctuation[character], advance(), start)
            continue
        if "a" <= character <= "z" or "A" <= character <= "Z" or character == "_":
            spelling: list[str] = []
            spelling_too_long = False
            while index < len(source):
                current = source[index]
                if not (
                    "a" <= current <= "z"
                    or "A" <= current <= "Z"
                    or "0" <= current <= "9"
                    or current == "_"
                ):
                    break
                consumed = advance()
                if len(spelling) < MAX_IDENTIFIER_BYTES:
                    spelling.append(consumed)
                else:
                    spelling_too_long = True
            text = "".join(spelling)
            if spelling_too_long:
                diagnostics.append(
                    Diagnostic(
                        "L003",
                        f"identifier exceeds {MAX_IDENTIFIER_BYTES} bytes",
                        Span(start[0], byte_offset, start[1], start[2], line, column),
                    )
                )
            else:
                emit(keywords.get(text, "IDENTIFIER"), text, start)
            if len(diagnostics) >= MAX_DIAGNOSTICS:
                break
            continue
        if "0" <= character <= "9":
            digits: list[str] = []
            digits_too_long = False
            while index < len(source) and "0" <= source[index] <= "9":
                consumed = advance()
                if len(digits) < MAX_INTEGER_DIGITS:
                    digits.append(consumed)
                else:
                    digits_too_long = True
            text = "".join(digits)
            if digits_too_long:
                diagnostics.append(
                    Diagnostic(
                        "L004",
                        f"integer exceeds {MAX_INTEGER_DIGITS} digits",
                        Span(start[0], byte_offset, start[1], start[2], line, column),
                    )
                )
            else:
                emit("INTEGER", text, start)
            if len(diagnostics) >= MAX_DIAGNOSTICS:
                break
            continue

        invalid = advance()
        diagnostics.append(
            Diagnostic(
                "L005",
                f"unexpected character U+{ord(invalid):04X}",
                Span(start[0], byte_offset, start[1], start[2], line, column),
            )
        )
        if len(diagnostics) >= MAX_DIAGNOSTICS:
            break

    eof_span = _point(byte_offset, line, column)
    tokens.append(Token("EOF", "", eof_span))
    return tuple(tokens), tuple(diagnostics)


class _ParseFailure(Exception):
    def __init__(self, diagnostic: Diagnostic) -> None:
        super().__init__(diagnostic.message)
        self.diagnostic = diagnostic


class _Parser:
    def __init__(self, tokens: tuple[Token, ...]) -> None:
        self.tokens = tokens
        self.index = 0
        self.node_count = 0
        self.diagnostics: list[Diagnostic] = []

    @property
    def current(self) -> Token:
        return self.tokens[self.index]

    def take(self) -> Token:
        token = self.current
        if token.kind != "EOF":
            self.index += 1
        return token

    def expect(self, kind: str, message: str) -> Token:
        if self.current.kind != kind:
            raise _ParseFailure(Diagnostic("P001", message, self.current.span))
        return self.take()

    def node(self, span: Span) -> None:
        self.node_count += 1
        if self.node_count > MAX_AST_NODES:
            raise _ParseFailure(
                Diagnostic("P002", f"AST node count exceeds {MAX_AST_NODES}", span)
            )

    def parse_program(self) -> FrontendResult:
        statements: list[Statement] = []
        while self.current.kind != "EOF" and len(self.diagnostics) < MAX_DIAGNOSTICS:
            start_index = self.index
            try:
                statements.append(self.parse_statement())
            except _ParseFailure as failure:
                self.diagnostics.append(failure.diagnostic)
                while self.current.kind not in {"SEMICOLON", "EOF"}:
                    self.take()
                if self.current.kind == "SEMICOLON":
                    self.take()
                elif self.index == start_index:
                    break
        program = None if self.diagnostics else Program(tuple(statements))
        return FrontendResult(self.tokens, program, tuple(self.diagnostics))

    def parse_statement(self) -> Statement:
        start = self.current
        if start.kind == "LET":
            self.take()
            name = self.expect("IDENTIFIER", "expected identifier after 'let'")
            self.expect("EQUAL", "expected '=' after binding name")
            expression = self.parse_sum(0)
            end = self.expect("SEMICOLON", "expected ';' after binding")
            span = _join_spans(start.span, end.span)
            self.node(span)
            return LetStatement(name.text, name.span, expression, span)
        if start.kind == "EMIT":
            self.take()
            expression = self.parse_sum(0)
            end = self.expect("SEMICOLON", "expected ';' after emitted expression")
            span = _join_spans(start.span, end.span)
            self.node(span)
            return EmitStatement(expression, span)
        raise _ParseFailure(
            Diagnostic("P003", "expected a 'let' or 'emit' statement", start.span)
        )

    def parse_sum(self, depth: int) -> Expression:
        left = self.parse_product(depth)
        while self.current.kind in {"PLUS", "MINUS"}:
            operator = self.take()
            right = self.parse_product(depth)
            span = _join_spans(left.span, right.span)
            self.node(span)
            left = Binary(operator.text, left, right, span)
        return left

    def parse_product(self, depth: int) -> Expression:
        left = self.parse_primary(depth)
        while self.current.kind in {"STAR", "SLASH"}:
            operator = self.take()
            right = self.parse_primary(depth)
            span = _join_spans(left.span, right.span)
            self.node(span)
            left = Binary(operator.text, left, right, span)
        return left

    def parse_primary(self, depth: int) -> Expression:
        token = self.current
        if token.kind == "INTEGER":
            self.take()
            self.node(token.span)
            return Integer(token.text, token.span)
        if token.kind == "IDENTIFIER":
            self.take()
            self.node(token.span)
            return Name(token.text, token.span)
        if token.kind == "LPAREN":
            if depth >= MAX_NESTING:
                raise _ParseFailure(
                    Diagnostic("P004", f"nesting exceeds {MAX_NESTING}", token.span)
                )
            self.take()
            expression = self.parse_sum(depth + 1)
            self.expect("RPAREN", "expected ')' to close expression")
            return expression
        raise _ParseFailure(Diagnostic("P005", "expected an expression", token.span))


def parse_source(source: str) -> FrontendResult:
    """Return tokens and either one complete AST or structured diagnostics."""

    tokens, diagnostics = lex(source)
    if diagnostics:
        return FrontendResult(tokens, None, diagnostics)
    return _Parser(tokens).parse_program()


def ast_shape(value: Program | Statement | Expression) -> object:
    """Return a span-free structural form useful for metamorphic tests."""

    if isinstance(value, Program):
        return ("program", tuple(ast_shape(statement) for statement in value.statements))
    if isinstance(value, LetStatement):
        return ("let", value.name, ast_shape(value.expression))
    if isinstance(value, EmitStatement):
        return ("emit", ast_shape(value.expression))
    if isinstance(value, Integer):
        return ("integer", value.text)
    if isinstance(value, Name):
        return ("name", value.text)
    if isinstance(value, Binary):
        return (value.operator, ast_shape(value.left), ast_shape(value.right))
    raise TypeError("unsupported AST value")
